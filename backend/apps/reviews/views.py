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

from .models import ReviewTask, ReviewResult, ReviewOpinion, ReviewCycle
from .serializers import (
    ReviewTaskSerializer, ReviewResultSerializer,
    ReviewOpinionSerializer, ReviewCycleSerializer
)
from .tasks import process_review_task


class ReviewTaskViewSet(viewsets.ModelViewSet):
    queryset = ReviewTask.objects.all()
    serializer_class = ReviewTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['contract', 'task_type', 'status']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

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


class ReviewResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReviewResult.objects.all()
    serializer_class = ReviewResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['contract', 'risk_level']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
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

