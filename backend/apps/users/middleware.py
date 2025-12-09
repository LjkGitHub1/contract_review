"""
操作日志中间件
自动记录所有 API 请求的操作日志
"""
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from apps.users.models import AuditLog

logger = logging.getLogger(__name__)


class AuditLogMiddleware(MiddlewareMixin):
    """
    操作日志中间件
    自动记录所有 API 请求的操作日志
    """
    
    # 排除的路径（不需要记录日志的路径）
    EXCLUDED_PATHS = [
        '/api/users/audit-logs/',  # 操作日志本身不需要记录
        '/api/auth/',  # 认证相关
        '/admin/',  # Django admin
        '/static/',  # 静态文件
        '/media/',  # 媒体文件
    ]
    
    # 排除的 HTTP 方法
    EXCLUDED_METHODS = ['OPTIONS', 'HEAD']
    
    def process_request(self, request):
        """处理请求前"""
        # 标记请求，以便在响应后记录日志
        if self._should_log(request):
            request._audit_log_data = {
                'start_time': timezone.now(),
                'request_data': self._get_request_data(request),
            }
    
    def process_response(self, request, response):
        """处理响应后"""
        if not self._should_log(request):
            return response
        
        # 检查是否有请求数据（可能在某些情况下没有）
        if not hasattr(request, '_audit_log_data'):
            return response
        
        try:
            # 获取请求信息
            user = getattr(request, 'user', None)
            if user and not user.is_authenticated:
                user = None
            
            # 确定操作类型
            action = self._get_action(request)
            
            # 确定资源类型和ID
            resource_type, resource_id = self._get_resource_info(request)
            
            # 获取 IP 地址
            ip_address = self._get_client_ip(request)
            
            # 获取用户代理
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            # 准备请求数据（排除敏感信息）
            request_data = request._audit_log_data.get('request_data', {})
            
            # 准备响应数据
            response_data = None
            if hasattr(response, 'data'):
                # DRF Response
                response_data = response.data
            elif hasattr(response, 'content'):
                # 尝试解析 JSON 响应
                try:
                    content = response.content.decode('utf-8')
                    if content:
                        response_data = json.loads(content)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            
            # 确定状态
            status = 'success' if 200 <= response.status_code < 400 else 'failed'
            
            # 错误信息
            error_message = ''
            if status == 'failed':
                if isinstance(response_data, dict):
                    error_message = str(response_data.get('detail', response_data.get('error', '')))[:500]
                else:
                    error_message = f'HTTP {response.status_code}'
            
            # 创建操作日志
            AuditLog.objects.create(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_data=request_data if request_data else None,
                response_data=response_data if response_data else None,
                status=status,
                error_message=error_message if error_message else '',
            )
        except Exception as e:
            # 记录日志失败不应该影响正常请求
            logger.error(f'Failed to create audit log: {str(e)}', exc_info=True)
        
        return response
    
    def _should_log(self, request):
        """判断是否应该记录日志"""
        # 排除非 API 请求
        if not request.path.startswith('/api/'):
            return False
        
        # 排除特定路径
        for excluded_path in self.EXCLUDED_PATHS:
            if request.path.startswith(excluded_path):
                return False
        
        # 排除特定方法
        if request.method in self.EXCLUDED_METHODS:
            return False
        
        return True
    
    def _get_action(self, request):
        """获取操作类型"""
        method = request.method
        path = request.path
        
        # 根据路径和方法确定操作类型
        if '/users/' in path:
            resource = '用户'
        elif '/contracts/' in path:
            resource = '合同'
        elif '/templates/' in path:
            resource = '模板'
        elif '/reviews/' in path:
            resource = '审核'
        elif '/rules/' in path:
            resource = '规则'
        elif '/departments/' in path:
            resource = '部门'
        else:
            resource = '其他'
        
        action_map = {
            'GET': '查询',
            'POST': '创建',
            'PUT': '更新',
            'PATCH': '部分更新',
            'DELETE': '删除',
        }
        
        action = action_map.get(method, method)
        return f'{resource}{action}'
    
    def _get_resource_info(self, request):
        """获取资源类型和ID"""
        path = request.path
        
        # 提取资源类型
        resource_type = None
        if '/users/' in path:
            resource_type = 'user'
        elif '/contracts/' in path:
            resource_type = 'contract'
        elif '/templates/' in path:
            resource_type = 'template'
        elif '/reviews/' in path:
            resource_type = 'review'
        elif '/rules/' in path:
            resource_type = 'rule'
        elif '/departments/' in path:
            resource_type = 'department'
        
        # 尝试从 URL 中提取资源ID
        resource_id = None
        path_parts = [p for p in path.split('/') if p]
        if len(path_parts) >= 3:
            try:
                # 假设格式为 /api/resource/id/
                potential_id = path_parts[-1]
                if potential_id.isdigit():
                    resource_id = int(potential_id)
            except (ValueError, IndexError):
                pass
        
        return resource_type, resource_id
    
    def _get_request_data(self, request):
        """获取请求数据（排除敏感信息）"""
        data = {}
        
        # 获取 GET 参数
        if request.GET:
            data['query_params'] = dict(request.GET)
        
        # 获取 POST/PUT/PATCH 数据
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'data'):
                    # DRF Request
                    body_data = dict(request.data)
                else:
                    # 普通请求
                    body_data = {}
                    if request.content_type == 'application/json':
                        try:
                            body_data = json.loads(request.body.decode('utf-8'))
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass
                    elif request.content_type.startswith('multipart/form-data'):
                        body_data = dict(request.POST)
                    else:
                        body_data = dict(request.POST)
                
                # 排除敏感信息
                sensitive_fields = ['password', 'token', 'secret', 'key', 'authorization']
                filtered_data = {}
                for key, value in body_data.items():
                    if any(sensitive in key.lower() for sensitive in sensitive_fields):
                        filtered_data[key] = '***'
                    else:
                        filtered_data[key] = value
                
                data['body'] = filtered_data
            except Exception as e:
                logger.warning(f'Failed to parse request data: {str(e)}')
        
        return data if data else None
    
    def _get_client_ip(self, request):
        """获取客户端 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

