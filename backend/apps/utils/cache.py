"""
缓存工具模块
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def cache_result(timeout=None, key_prefix='', vary_on=None):
    """
    缓存装饰器
    
    Args:
        timeout: 缓存超时时间（秒），默认使用CACHE_TTL中的设置
        key_prefix: 缓存键前缀
        vary_on: 影响缓存键的参数列表（函数参数名）
    
    Usage:
        @cache_result(timeout=300, key_prefix='contract', vary_on=['contract_id'])
        def get_contract(contract_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存键
            cache_key_parts = [key_prefix, func.__name__]
            
            # 添加参数到缓存键
            if vary_on:
                for param_name in vary_on:
                    if param_name in kwargs:
                        cache_key_parts.append(f"{param_name}:{kwargs[param_name]}")
                    else:
                        # 尝试从args中获取
                        try:
                            func_code = func.__code__
                            param_names = func_code.co_varnames[:func_code.co_argcount]
                            if param_name in param_names:
                                param_index = param_names.index(param_name)
                                if param_index < len(args):
                                    cache_key_parts.append(f"{param_name}:{args[param_index]}")
                        except:
                            pass
            
            # 如果没有指定vary_on，使用所有参数
            if not vary_on:
                if args:
                    cache_key_parts.append(f"args:{hash(str(args))}")
                if kwargs:
                    cache_key_parts.append(f"kwargs:{hash(str(sorted(kwargs.items())))}")
            
            cache_key = ':'.join(str(part) for part in cache_key_parts if part)
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # 获取缓存
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 设置缓存
            cache_timeout = timeout or settings.CACHE_TTL.get('default', 300)
            cache.set(cache_key, result, cache_timeout)
            
            return result
        return wrapper
    return decorator


def cache_delete_pattern(pattern):
    """
    删除匹配模式的缓存
    
    Args:
        pattern: 缓存键模式（支持通配符）
    """
    try:
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        
        # 获取所有匹配的键
        keys = redis_client.keys(f"contract_review:{pattern}")
        
        if keys:
            redis_client.delete(*keys)
            return len(keys)
        return 0
    except Exception:
        return 0


def cache_invalidate(*cache_keys):
    """
    使指定的缓存失效
    
    Args:
        *cache_keys: 缓存键列表
    """
    for key in cache_keys:
        cache.delete(key)


def get_or_set_cache(key, callable_func, timeout=None):
    """
    获取或设置缓存
    
    Args:
        key: 缓存键
        callable_func: 如果缓存不存在，调用此函数获取值
        timeout: 缓存超时时间
    
    Returns:
        缓存的值或函数返回值
    """
    result = cache.get(key)
    if result is not None:
        return result
    
    result = callable_func()
    cache_timeout = timeout or settings.CACHE_TTL.get('default', 300)
    cache.set(key, result, cache_timeout)
    return result

