from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
import os
import logging

logger = logging.getLogger(__name__)

from .models import ReviewTask, ReviewResult, ReviewOpinion, ReviewCycle, ReviewFocusConfig, AIModelConfig
from .serializers import (
    ReviewTaskSerializer, ReviewResultSerializer,
    ReviewOpinionSerializer, ReviewCycleSerializer, ReviewFocusConfigSerializer,
    AIModelConfigSerializer
)
from .tasks import process_review_task
from .services import ReviewService
from .services_auto import AutoReviewService
from .services_loop import ReviewOpinionLoopService
from apps.users.models import User


class ReviewTaskViewSet(viewsets.ModelViewSet):
    queryset = ReviewTask.objects.all()
    serializer_class = ReviewTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['contract', 'status']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """优化查询：使用select_related和prefetch_related减少数据库查询"""
        queryset = ReviewTask.objects.all().select_related(
            'contract', 'contract__drafter', 'reviewer', 'created_by'
        ).prefetch_related(
            'contract__versions', 'contract__review_tasks'
        )
        
        # 如果是审核员，只显示分配给自己的任务
        user = self.request.user
        if user.is_authenticated and user.role == 'reviewer' and user.reviewer_level:
            # 由于JSONField查询限制，我们需要在Python层面过滤
            # 先获取所有可能相关的任务（reviewer字段或reviewer_assignments包含该层级的）
            from django.db.models import Q
            potential_tasks = queryset.filter(
                Q(reviewer=user) | 
                Q(reviewer_assignments__isnull=False)
            )
            
            # 在Python层面过滤
            filtered_task_ids = []
            for task in potential_tasks:
                # 检查是否分配给当前用户
                if task.reviewer == user:
                    filtered_task_ids.append(task.id)
                elif task.reviewer_assignments and isinstance(task.reviewer_assignments, dict):
                    assigned_user_id = task.reviewer_assignments.get(user.reviewer_level)
                    if assigned_user_id and int(assigned_user_id) == user.id:
                        filtered_task_ids.append(task.id)
            
            if filtered_task_ids:
                queryset = queryset.filter(id__in=filtered_task_ids)
            else:
                queryset = queryset.none()
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """启动审核任务"""
        task = self.get_object()
        if task.status != 'pending':
            return Response({'error': '任务状态不允许启动'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = 'processing'
        task.started_at = timezone.now()
        task.save()
        
        # 尝试异步执行，如果 Celery 不可用则同步执行
        try:
            celery_task = process_review_task.delay(task.id)
            task.celery_task_id = celery_task.id
            task.save()
            return Response({'message': '审核任务已启动（异步）', 'celery_task_id': celery_task.id})
        except Exception as e:
            # Celery 不可用，同步执行
            try:
                result = process_review_task(task.id)
                serializer = self.get_serializer(task)
                return Response({
                    'message': '审核任务已完成（同步）',
                    'task': serializer.data,
                    'result': result
                })
            except Exception as sync_error:
                # 同步执行也失败，更新状态为失败
                task.status = 'failed'
                task.error_message = f'执行失败: {str(sync_error)}'
                task.completed_at = timezone.now()
                task.save()
                return Response({
                    'error': f'审核任务执行失败: {str(sync_error)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        """获取审核结果"""
        task = self.get_object()
        try:
            result = task.result
            serializer = ReviewResultSerializer(result)
            return Response(serializer.data)
        except ReviewResult.DoesNotExist:
            return Response({'error': '审核结果不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def complete_manually(self, request, pk=None):
        """手动完成审核任务（用于处理卡住的任务）"""
        task = self.get_object()
        if task.status != 'processing':
            return Response({'error': '只能完成处理中的任务'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已有结果
        if hasattr(task, 'result'):
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.save()
            return Response({'message': '任务已标记为完成'})
        
        # 如果没有结果，尝试同步执行
        try:
            result = process_review_task(task.id)
            serializer = self.get_serializer(task)
            return Response({
                'message': '任务已手动完成',
                'task': serializer.data,
                'result': result
            })
        except Exception as e:
            task.status = 'failed'
            task.error_message = f'手动完成失败: {str(e)}'
            task.completed_at = timezone.now()
            task.save()
            return Response({
                'error': f'手动完成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def check_stuck_tasks(self, request):
        """检查并修复卡住的任务（处理中超过一定时间的任务）"""
        from datetime import timedelta
        
        # 查找处理中超过30分钟的任务
        threshold = timezone.now() - timedelta(minutes=30)
        stuck_tasks = ReviewTask.objects.filter(
            status='processing',
            started_at__lt=threshold
        )
        
        fixed_count = 0
        for task in stuck_tasks:
            # 检查是否有结果
            if hasattr(task, 'result'):
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save()
                fixed_count += 1
            else:
                # 标记为失败
                task.status = 'failed'
                task.error_message = '任务超时，自动标记为失败'
                task.completed_at = timezone.now()
                task.save()
                fixed_count += 1
        
        return Response({
            'message': f'已修复 {fixed_count} 个卡住的任务',
            'fixed_count': fixed_count
        })
    
    def retrieve(self, request, *args, **kwargs):
        """重写retrieve方法，确保返回result"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewers')
    def get_reviewers(self, request):
        """获取审核人员列表，可按层级筛选"""
        level = request.query_params.get('level', None)
        
        # 查询审核员角色且激活的用户
        queryset = User.objects.filter(
            role='reviewer',
            is_active=True,
            is_deleted=False
        )
        
        # 如果指定了层级，则筛选该层级的审核员
        if level:
            queryset = queryset.filter(reviewer_level=level)
        
        reviewers = queryset.values('id', 'username', 'real_name', 'email', 'reviewer_level')
        
        # 按层级分组
        grouped = {}
        for reviewer in reviewers:
            reviewer_level = reviewer['reviewer_level'] or 'unassigned'
            if reviewer_level not in grouped:
                grouped[reviewer_level] = []
            grouped[reviewer_level].append({
                'id': reviewer['id'],
                'username': reviewer['username'],
                'real_name': reviewer['real_name'] or reviewer['username'],
                'email': reviewer['email'],
                'level': reviewer['reviewer_level']
            })
        
        return Response({
            'reviewers': list(reviewers),
            'grouped': grouped
        })

    @action(detail=True, methods=['post'])
    def submit_review(self, request, pk=None):
        """审核员提交审核意见"""
        task = self.get_object()
        user = request.user
        
        # 检查用户是否是审核员
        if user.role != 'reviewer' or not user.reviewer_level:
            return Response({'error': '只有审核员可以提交审核意见'}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查任务是否分配给当前用户
        if task.reviewer != user:
            # 检查reviewer_assignments中是否包含当前用户
            if not task.reviewer_assignments or not isinstance(task.reviewer_assignments, dict):
                return Response({'error': '该任务未分配给您'}, status=status.HTTP_403_FORBIDDEN)
            
            assigned_user_id = task.reviewer_assignments.get(user.reviewer_level)
            if not assigned_user_id or int(assigned_user_id) != user.id:
                return Response({'error': '该任务未分配给您'}, status=status.HTTP_403_FORBIDDEN)
        
        # 检查任务状态
        if task.status not in ['pending', 'processing']:
            return Response({'error': '只能提交待处理或处理中任务的审核意见'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果任务状态是pending，更新为processing
        if task.status == 'pending':
            task.status = 'processing'
            task.started_at = timezone.now()
        
        # 获取或创建审核结果
        review_result, created = ReviewResult.objects.get_or_create(
            review_task=task,
            defaults={'contract': task.contract}
        )
        
        # 保存审核意见
        opinions_data = request.data.get('opinions', [])
        for opinion_data in opinions_data:
            ReviewOpinion.objects.create(
                review_result=review_result,
                reviewer=user,
                clause_id=opinion_data.get('clause_id', ''),
                clause_content=opinion_data.get('clause_content', ''),
                opinion_type=opinion_data.get('opinion_type', 'suggestion'),
                risk_level=opinion_data.get('risk_level', 'low'),
                opinion_content=opinion_data.get('opinion_content', ''),
                legal_basis=opinion_data.get('legal_basis', ''),
                suggestion=opinion_data.get('suggestion', ''),
                status='pending'
            )
        
        # 更新任务状态和审核员层级
        task.reviewer_level = user.reviewer_level
        task.reviewer = user
        task.save()
        
        # 检查是否所有层级的审核都已完成
        if task.review_levels and isinstance(task.review_levels, list):
            # 获取所有已完成的层级（通过检查是否有审核意见）
            completed_levels = set()
            for opinion in review_result.opinions.all():
                if opinion.reviewer and opinion.reviewer.reviewer_level:
                    completed_levels.add(opinion.reviewer.reviewer_level)
            
            # 如果所有配置的层级都已完成，标记任务为已完成
            if set(task.review_levels).issubset(completed_levels):
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save()
        
        return Response({
            'message': '审核意见已提交',
            'task_id': task.id,
            'review_result_id': review_result.id
        })


class ReviewResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReviewResult.objects.all()
    serializer_class = ReviewResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['contract', 'risk_level']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    @action(detail=True, methods=['post'])
    def generate_report(self, request, pk=None):
        """生成审核报告（Word或PDF格式）"""
        from .services_report import ReportGeneratorService
        from apps.contracts.models import Contract
        
        result = self.get_object()
        report_format = request.data.get('format', 'word')  # word 或 pdf
        
        try:
            contract = result.review_task.contract
        except:
            return Response({'error': '无法获取合同信息'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            report_service = ReportGeneratorService()
            
            if report_format.lower() == 'pdf':
                report_path = report_service.generate_pdf_report(result, contract)
            else:
                report_path = report_service.generate_word_report(result, contract)
            
            # 更新审核结果的报告路径
            result.report_path = report_path
            result.save()
            
            return Response({
                'success': True,
                'report_path': report_path,
                'message': f'{report_format.upper()}报告生成成功'
            })
            
        except Exception as e:
            logger.error(f'生成报告失败: {str(e)}')
            return Response({
                'error': f'生成报告失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def download_report(self, request, pk=None):
        """下载审核报告"""
        result = self.get_object()
        if not result.report_path:
            return Response({'error': '报告文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        file_path = os.path.join(settings.MEDIA_ROOT, result.report_path)
        if not os.path.exists(file_path):
            return Response({'error': '报告文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            file = open(file_path, 'rb')
            response = FileResponse(file)
            
            # 根据文件类型设置Content-Type
            file_ext = os.path.splitext(result.report_path)[1].lower()
            if file_ext == '.pdf':
                response['Content-Type'] = 'application/pdf'
            elif file_ext in ['.doc', '.docx']:
                response['Content-Type'] = 'application/msword'
            else:
                response['Content-Type'] = 'application/octet-stream'
            
            # 设置下载文件名
            file_name = f'审核报告_{result.contract.contract_no}{file_ext}'
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            
            return response
        except Exception as e:
            return Response({'error': f'下载失败: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def preview_report(self, request, pk=None):
        """预览审核报告"""
        result = self.get_object()
        if not result.report_path:
            return Response({'error': '报告文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        file_path = os.path.join(settings.MEDIA_ROOT, result.report_path)
        if not os.path.exists(file_path):
            return Response({'error': '报告文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            file_ext = os.path.splitext(result.report_path)[1].lower()
            
            if file_ext == '.pdf':
                # PDF预览
                file = open(file_path, 'rb')
                response = FileResponse(file)
                response['Content-Type'] = 'application/pdf'
                response['Content-Disposition'] = 'inline; filename="report.pdf"'
                return response
            elif file_ext in ['.doc', '.docx']:
                # Word文档，返回下载（浏览器可能不支持直接预览）
                file = open(file_path, 'rb')
                response = FileResponse(file)
                response['Content-Type'] = 'application/msword'
                response['Content-Disposition'] = 'inline; filename="report.docx"'
                return response
            else:
                # 其他格式，尝试文本预览
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return HttpResponse(content, content_type='text/plain; charset=utf-8')
                
        except Exception as e:
            return Response({'error': f'预览失败: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReviewOpinionViewSet(viewsets.ModelViewSet):
    queryset = ReviewOpinion.objects.filter(is_deleted=False)
    serializer_class = ReviewOpinionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['review_result', 'opinion_type', 'risk_level', 'status']
    ordering_fields = ['risk_level', 'created_at']
    ordering = ['-risk_level', '-created_at']

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewCycleViewSet(viewsets.ModelViewSet):
    queryset = ReviewCycle.objects.all()
    serializer_class = ReviewCycleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['contract', 'status']
    ordering_fields = ['cycle_no', 'created_at']
    ordering = ['-cycle_no']

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交审核"""
        cycle = self.get_object()
        cycle.status = 'reviewing'
        cycle.submitted_by = request.user
        cycle.submitted_at = timezone.now()
        cycle.opinion_summary = request.data.get('opinion_summary', '')
        cycle.save()
        
        # 创建审核任务
        review_task = ReviewTask.objects.create(
            contract=cycle.contract,
            task_type='auto',
            created_by=request.user
        )
        cycle.review_result = None  # 待审核完成后关联
        cycle.save()
        
        return Response({'message': '已提交审核', 'review_task_id': review_task.id})

    @action(detail=True, methods=['post'])
    def modify(self, request, pk=None):
        """修改合同"""
        cycle = self.get_object()
        cycle.status = 'modifying'
        cycle.modified_by = request.user
        cycle.modified_at = timezone.now()
        cycle.modification_summary = request.data.get('modification_summary', '')
        cycle.save()
        return Response({'message': '已记录修改'})
    
    @action(detail=False, methods=['post'])
    def summarize_opinions(self, request):
        """自动汇总各层级审核意见"""
        contract_id = request.data.get('contract_id')
        review_task_ids = request.data.get('review_task_ids', [])
        
        if not contract_id:
            return Response({'error': '请提供contract_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apps.contracts.models import Contract
            contract = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response({'error': '合同不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取审核任务
        review_tasks = None
        if review_task_ids:
            review_tasks = ReviewTask.objects.filter(
                id__in=review_task_ids,
                contract=contract
            )
        
        # 调用服务汇总意见
        loop_service = ReviewOpinionLoopService()
        result = loop_service.summarize_opinions(contract, review_tasks)
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def feedback_to_drafter(self, request):
        """反馈审核意见给起草人"""
        contract_id = request.data.get('contract_id')
        summary_table = request.data.get('summary_table')
        feedback_message = request.data.get('feedback_message')
        
        if not contract_id:
            return Response({'error': '请提供contract_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apps.contracts.models import Contract
            contract = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response({'error': '合同不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 如果没有提供汇总表，先生成
        if not summary_table:
            loop_service = ReviewOpinionLoopService()
            summarize_result = loop_service.summarize_opinions(contract)
            if not summarize_result.get('success'):
                return Response(summarize_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            summary_table = summarize_result.get('summary_table')
        
        # 反馈给起草人
        loop_service = ReviewOpinionLoopService()
        result = loop_service.feedback_to_drafter(contract, summary_table, feedback_message)
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def resubmit_for_review(self, request):
        """重新提交审核"""
        contract_id = request.data.get('contract_id')
        change_summary = request.data.get('change_summary')
        
        if not contract_id:
            return Response({'error': '请提供contract_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apps.contracts.models import Contract
            contract = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response({'error': '合同不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 重新提交审核
        loop_service = ReviewOpinionLoopService()
        result = loop_service.resubmit_for_review(
            contract=contract,
            modified_by=request.user,
            change_summary=change_summary
        )
        
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReviewFocusConfigViewSet(viewsets.ModelViewSet):
    """审核重点配置视图集"""
    queryset = ReviewFocusConfig.objects.all()
    serializer_class = ReviewFocusConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['level', 'is_active']
    ordering_fields = ['level', 'created_at']
    ordering = ['level']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """根据层级获取配置"""
        level = request.query_params.get('level')
        if not level:
            return Response({'error': '请提供level参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            config = ReviewFocusConfig.objects.get(level=level, is_active=True)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except ReviewFocusConfig.DoesNotExist:
            return Response({'error': '该层级的配置不存在'}, status=status.HTTP_404_NOT_FOUND)


class ReviewAISuggestionViewSet(viewsets.ViewSet):
    """AI审核建议视图集"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.review_service = ReviewService()
    
    def list(self, request):
        """列表方法（占位，实际不使用）"""
        return Response({'message': '请使用generate或get_by_task接口'})
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        生成AI审核建议
        POST /api/reviews/ai-suggestions/generate/
        {
            "contract_id": 1,
            "review_task_id": 1  // 可选
        }
        """
        from apps.contracts.models import Contract
        
        contract_id = request.data.get('contract_id')
        review_task_id = request.data.get('review_task_id')
        
        if not contract_id:
            return Response({'error': '请提供contract_id'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            contract = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response({'error': '合同不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取当前用户作为审核员
        reviewer = request.user
        
        # 检查用户是否是审核员
        if reviewer.role != 'reviewer' and not reviewer.reviewer_level:
            return Response({
                'error': '当前用户不是审核员或未设置审核员层级',
                'suggestions': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取审核任务（如果提供）
        review_task = None
        if review_task_id:
            try:
                review_task = ReviewTask.objects.get(id=review_task_id)
                # 更新审核任务的审核员信息
                review_task.reviewer = reviewer
                review_task.reviewer_level = reviewer.reviewer_level
                review_task.save()
            except ReviewTask.DoesNotExist:
                pass
        
        # 生成AI建议
        result = self.review_service.generate_ai_suggestions_for_reviewer(
            contract=contract,
            reviewer=reviewer,
            review_task=review_task
        )
        
        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_by_task(self, request):
        """
        根据审核任务获取AI建议
        GET /api/reviews/ai-suggestions/get_by_task/?review_task_id=1
        """
        review_task_id = request.query_params.get('review_task_id')
        
        if not review_task_id:
            return Response({'error': '请提供review_task_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            review_task = ReviewTask.objects.get(id=review_task_id)
        except ReviewTask.DoesNotExist:
            return Response({'error': '审核任务不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 从审核结果中获取AI建议
        try:
            review_result = review_task.result
            review_data = review_result.review_data or {}
            ai_suggestions = review_data.get('ai_suggestions')
            
            if not ai_suggestions:
                return Response({
                    'error': '该审核任务尚未生成AI建议',
                    'suggestions': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'review_task_id': review_task.id,
                'reviewer_level': review_data.get('reviewer_level'),
                'generated_at': review_data.get('generated_at'),
                'suggestions': ai_suggestions
            })
        except ReviewResult.DoesNotExist:
            return Response({
                'error': '该审核任务尚未生成审核结果',
                'suggestions': None
            }, status=status.HTTP_404_NOT_FOUND)


class AIModelConfigViewSet(viewsets.ModelViewSet):
    """AI模型配置视图集"""
    queryset = AIModelConfig.objects.all()
    serializer_class = AIModelConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['provider', 'is_active', 'is_default']
    ordering_fields = ['is_default', 'created_at']
    ordering = ['-is_default', '-created_at']
    
    def get_queryset(self):
        """优化查询，避免N+1问题"""
        return AIModelConfig.objects.select_related('created_by', 'updated_by').all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def get_default(self, request):
        """获取系统默认配置"""
        try:
            config = AIModelConfig.objects.get(is_default=True, is_active=True)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except AIModelConfig.DoesNotExist:
            return Response({'error': '未找到系统默认配置'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设置为系统默认配置"""
        config = self.get_object()
        config.is_default = True
        config.is_active = True
        config.save()
        serializer = self.get_serializer(config)
        return Response({
            'message': '已设置为系统默认配置',
            'config': serializer.data
        })

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """测试API连接"""
        config = self.get_object()
        
        # 验证配置
        if not config.api_key:
            return Response({
                'success': False,
                'message': 'API密钥未配置'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not config.default_model and not config.available_models:
            return Response({
                'success': False,
                'message': '未配置可用模型'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 测试API连接
        try:
            from .services import AIService
            ai_service = AIService(config=config)
            
            # 验证AI服务配置
            if not ai_service.api_key:
                return Response({
                    'success': False,
                    'message': 'API密钥无效'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not ai_service.model:
                return Response({
                    'success': False,
                    'message': '未设置默认模型'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 使用专门的测试方法，真正调用API，不使用模拟数据
            result = ai_service.test_api_connection()
            
            return Response({
                'success': True,
                'message': result.get('message', 'API连接测试成功'),
                'response': result.get('response', ''),
                'model': result.get('model', '')
            })
        except ImportError as e:
            return Response({
                'success': False,
                'message': f'缺少必要的依赖: {str(e)}。请安装requests库: pip install requests'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            error_msg = str(e)
            logger.error(f'API连接测试失败: {error_msg}', exc_info=True)
            return Response({
                'success': False,
                'message': f'API连接测试失败: {error_msg}'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def get_available_models(self, request):
        """获取硅基流动可用模型列表"""
        # 硅基流动常用模型列表（使用完整的模型ID）
        siliconflow_models = [
            # DeepSeek 系列
            {'value': 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B', 'label': 'DeepSeek-R1-0528-Qwen3-8B (推荐)'},
            {'value': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B', 'label': 'DeepSeek-R1-Distill-Qwen-7B'},
            {'value': 'deepseek-ai/DeepSeek-V3', 'label': 'DeepSeek-V3'},
            {'value': 'deepseek-ai/DeepSeek-V2.5', 'label': 'DeepSeek-V2.5'},
            {'value': 'deepseek-ai/DeepSeek-Coder-V2-Lite', 'label': 'DeepSeek-Coder-V2-Lite'},
            # Qwen 系列
            {'value': 'Qwen/Qwen2.5-72B-Instruct', 'label': 'Qwen2.5-72B-Instruct'},
            {'value': 'Qwen/Qwen2.5-32B-Instruct', 'label': 'Qwen2.5-32B-Instruct'},
            {'value': 'Qwen/Qwen2.5-14B-Instruct', 'label': 'Qwen2.5-14B-Instruct'},
            {'value': 'Qwen/Qwen2.5-7B-Instruct', 'label': 'Qwen2.5-7B-Instruct'},
            {'value': 'Qwen/Qwen2.5-3B-Instruct', 'label': 'Qwen2.5-3B-Instruct'},
            {'value': 'Qwen/Qwen2.5-1.5B-Instruct', 'label': 'Qwen2.5-1.5B-Instruct'},
            {'value': 'Qwen/Qwen2-72B-Instruct', 'label': 'Qwen2-72B-Instruct'},
            {'value': 'Qwen/Qwen2-7B-Instruct', 'label': 'Qwen2-7B-Instruct'},
            {'value': 'qwen-plus', 'label': 'Qwen Plus (旧版)'},
            {'value': 'qwen-turbo', 'label': 'Qwen Turbo (旧版)'},
            {'value': 'qwen-max', 'label': 'Qwen Max (旧版)'},
            # GLM 系列
            {'value': 'THUDM/glm-4-9b-chat', 'label': 'GLM-4-9B-Chat'},
            {'value': 'THUDM/glm-4-9b-chat-1m', 'label': 'GLM-4-9B-Chat-1M'},
            # 其他
            {'value': 'meta-llama/Llama-3.1-70B-Instruct', 'label': 'Llama-3.1-70B-Instruct'},
            {'value': 'meta-llama/Llama-3.1-8B-Instruct', 'label': 'Llama-3.1-8B-Instruct'},
        ]
        
        provider = request.query_params.get('provider', 'siliconflow')
        
        if provider == 'siliconflow':
            return Response({
                'provider': 'siliconflow',
                'models': siliconflow_models
            })
        else:
            return Response({
                'provider': provider,
                'models': []
            })
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """AI对话接口"""
        message = request.data.get('message', '').strip()
        history = request.data.get('history', [])
        
        if not message:
            return Response({
                'error': '消息内容不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .services import AIService
            ai_service = AIService()
            
            # 调用AI对话
            response_text = ai_service.chat(message, history)
            
            return Response({
                'response': response_text,
                'model': ai_service.model if ai_service.enabled else None
            })
        except Exception as e:
            logger.error(f'AI对话失败: {str(e)}')
            return Response({
                'error': f'AI对话失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

