from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.conf import settings
from django.http import FileResponse, Http404
import uuid
import os
from pathlib import Path
import docx
import fitz  # PyMuPDF

from .models import Contract, ContractVersion, Template, UserHabit
from .serializers import (
    ContractSerializer, ContractVersionSerializer,
    TemplateSerializer, UserHabitSerializer
)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.filter(is_deleted=False)
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contract_type', 'industry', 'status', 'drafter']
    search_fields = ['title', 'contract_no']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        # 自动生成合同编号
        if not serializer.validated_data.get('contract_no'):
            contract_no = f'CT{timezone.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:8].upper()}'
            serializer.save(contract_no=contract_no, drafter=self.request.user)
        else:
            serializer.save(drafter=self.request.user)

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """创建新版本"""
        contract = self.get_object()
        new_version = contract.current_version + 1
        
        version = ContractVersion.objects.create(
            contract=contract,
            version=new_version,
            content=request.data.get('content', contract.content),
            file_path=request.data.get('file_path', contract.file_path),
            change_summary=request.data.get('change_summary', ''),
            changed_by=request.user
        )
        
        contract.current_version = new_version
        contract.save()
        
        serializer = ContractVersionSerializer(version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """获取合同所有版本"""
        contract = self.get_object()
        versions = contract.versions.filter(is_deleted=False)
        serializer = ContractVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """回滚到指定版本"""
        contract = self.get_object()
        version_num = request.data.get('version')
        
        try:
            version = contract.versions.get(version=version_num, is_deleted=False)
            contract.content = version.content
            contract.file_path = version.file_path
            contract.save()
            
            # 创建回滚版本
            new_version = contract.current_version + 1
            ContractVersion.objects.create(
                contract=contract,
                version=new_version,
                content=version.content,
                file_path=version.file_path,
                change_summary=f'回滚到版本 {version_num}',
                changed_by=request.user
            )
            contract.current_version = new_version
            contract.save()
            
            return Response({'message': f'已回滚到版本 {version_num}'})
        except ContractVersion.DoesNotExist:
            return Response({'error': '版本不存在'}, status=status.HTTP_404_NOT_FOUND)


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.filter(is_deleted=False)
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['contract_type', 'industry', 'is_public', 'is_enterprise']
    search_fields = ['name', 'description']
    ordering_fields = ['usage_count', 'created_at']
    ordering = ['-usage_count', '-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """使用模板"""
        template = self.get_object()
        template.usage_count += 1
        template.save()
        return Response({'message': '模板使用次数已更新'})


class UserHabitViewSet(viewsets.ModelViewSet):
    queryset = UserHabit.objects.all()
    serializer_class = UserHabitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['habit_type', 'user']

    def get_queryset(self):
        return UserHabit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def update_habit(self, request):
        """更新用户习惯"""
        habit_type = request.data.get('habit_type')
        habit_key = request.data.get('habit_key')
        habit_value = request.data.get('habit_value')
        
        habit, created = UserHabit.objects.get_or_create(
            user=request.user,
            habit_type=habit_type,
            habit_key=habit_key,
            defaults={'habit_value': habit_value}
        )
        
        if not created:
            habit.habit_value = habit_value
            habit.frequency += 1
            habit.last_used_at = timezone.now()
            habit.save()
        
        serializer = self.get_serializer(habit)
        return Response(serializer.data)


class FileUploadView(APIView):
    """文件上传视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """上传文件并解析内容"""
        if 'file' not in request.FILES:
            return Response({'error': '未找到文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        file_ext = os.path.splitext(file.name)[1].lower()
        
        # 验证文件类型
        allowed_extensions = ['.doc', '.docx', '.pdf']
        if file_ext not in allowed_extensions:
            return Response({'error': '不支持的文件类型，仅支持 .doc, .docx, .pdf'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # 验证文件大小（10MB）
        if file.size > 10 * 1024 * 1024:
            return Response({'error': '文件大小不能超过10MB'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 保存文件
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'contracts', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_name = f'{uuid.uuid4().hex}{file_ext}'
            file_path = os.path.join(upload_dir, file_name)
            
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            relative_path = os.path.join('contracts', 'uploads', file_name)
            
            # 解析文件内容
            content = self._parse_file(file_path, file_ext)
            
            return Response({
                'file_path': relative_path,
                'content': content,
                'message': '文件上传成功'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f'文件处理失败: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _parse_file(self, file_path, file_ext):
        """解析文件内容"""
        content = {
            'text': '',
            'html': '',
            'title': '',  # 提取的标题
            'metadata': {}
        }
        
        try:
            if file_ext in ['.doc', '.docx']:
                # 解析Word文档
                doc = docx.Document(file_path)
                paragraphs = [p.text for p in doc.paragraphs]
                content['text'] = '\n'.join(paragraphs)
                content['html'] = '<br>'.join([f'<p>{p}</p>' for p in paragraphs])
                
                # 提取标题：优先从文档属性，其次从第一个非空段落
                title = ''
                # 尝试从文档核心属性获取标题
                try:
                    if doc.core_properties.title:
                        title = doc.core_properties.title.strip()
                except:
                    pass
                
                # 如果属性中没有标题，尝试从第一个段落提取
                if not title and paragraphs:
                    # 查找第一个非空段落作为标题候选
                    for para in paragraphs:
                        para_text = para.strip()
                        if para_text and len(para_text) <= 200:  # 标题通常不会太长
                            # 检查是否像标题（不包含太多标点，不是纯数字等）
                            if not para_text.replace(' ', '').replace('：', '').replace(':', '').isdigit():
                                title = para_text
                                break
                
                # 如果还是没找到，使用第一个非空段落的前100个字符
                if not title and paragraphs:
                    for para in paragraphs:
                        para_text = para.strip()
                        if para_text:
                            title = para_text[:100] if len(para_text) > 100 else para_text
                            break
                
                content['title'] = title
                content['metadata'] = {
                    'paragraph_count': len(paragraphs),
                    'word_count': len(content['text'].split())
                }
                
            elif file_ext == '.pdf':
                # 解析PDF文档
                doc = fitz.open(file_path)
                text_parts = []
                html_parts = []
                
                # 提取第一页文本用于标题提取
                first_page_text = ''
                if len(doc) > 0:
                    first_page = doc[0]
                    first_page_text = first_page.get_text()
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    text_parts.append(text)
                    html_parts.append(f'<div class="page"><h3>第{page_num + 1}页</h3><p>{text.replace(chr(10), "<br>")}</p></div>')
                
                content['text'] = '\n\n'.join(text_parts)
                content['html'] = ''.join(html_parts)
                
                # 从PDF提取标题
                title = ''
                # 尝试从元数据获取标题
                try:
                    metadata = doc.metadata
                    if metadata and metadata.get('title'):
                        title = metadata['title'].strip()
                except:
                    pass
                
                # 如果元数据中没有，从第一页文本提取
                if not title and first_page_text:
                    # 获取第一页的前几行作为标题候选
                    lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
                    if lines:
                        # 查找第一个看起来像标题的行（长度适中，不包含太多标点）
                        for line in lines[:5]:  # 只检查前5行
                            if 5 <= len(line) <= 200:
                                # 排除明显不是标题的行（如页码、日期等）
                                if not any(keyword in line for keyword in ['第', '页', '共', '日期', 'Date']):
                                    title = line
                                    break
                        
                        # 如果还是没找到，使用第一行
                        if not title and lines[0]:
                            title = lines[0][:100] if len(lines[0]) > 100 else lines[0]
                
                content['title'] = title
                content['metadata'] = {
                    'page_count': len(doc),
                    'word_count': len(content['text'].split())
                }
                doc.close()
                
        except Exception as e:
            content['error'] = f'解析文件时出错: {str(e)}'
        
        return content

