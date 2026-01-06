"""
性能监控工具模块
"""
import time
import logging
from functools import wraps
from django.db import connection, reset_queries
from django.conf import settings

logger = logging.getLogger(__name__)


def monitor_performance(log_queries=False):
    """
    性能监控装饰器
    
    Args:
        log_queries: 是否记录数据库查询
    
    Usage:
        @monitor_performance(log_queries=True)
        def my_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            query_count_start = len(connection.queries) if log_queries else 0
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_time = time.time() - start_time
                query_count = len(connection.queries) - query_count_start if log_queries else 0
                
                # 记录性能信息
                logger.info(
                    f'Performance: {func.__name__} - '
                    f'Time: {elapsed_time:.3f}s, '
                    f'Queries: {query_count}'
                )
                
                # 如果执行时间过长，记录警告
                if elapsed_time > 1.0:
                    logger.warning(
                        f'Slow performance: {func.__name__} took {elapsed_time:.3f}s'
                    )
                
                # 如果查询次数过多，记录警告
                if log_queries and query_count > 10:
                    logger.warning(
                        f'Too many queries: {func.__name__} executed {query_count} queries'
                    )
        return wrapper
    return decorator


def get_query_count():
    """获取当前请求的数据库查询次数"""
    return len(connection.queries)


def reset_query_count():
    """重置查询计数"""
    reset_queries()


class QueryCountMiddleware:
    """查询计数中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        reset_queries()
        response = self.get_response(request)
        query_count = len(connection.queries)
        
        if query_count > 10:
            logger.warning(
                f'Request {request.path} executed {query_count} queries'
            )
        
        return response

