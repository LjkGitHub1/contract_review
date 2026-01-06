"""
工具模块单元测试
"""
from django.test import TestCase
from django.core.cache import cache
from apps.utils.cache import cache_result, cache_delete_pattern, get_or_set_cache


class CacheUtilTest(TestCase):
    """缓存工具测试"""
    
    def setUp(self):
        """测试前准备"""
        cache.clear()
    
    def test_cache_result_decorator(self):
        """测试缓存装饰器"""
        call_count = [0]
        
        @cache_result(timeout=60, key_prefix='test', vary_on=['param'])
        def test_func(param):
            call_count[0] += 1
            return f'result_{param}'
        
        # 第一次调用，应该执行函数
        result1 = test_func('test')
        self.assertEqual(result1, 'result_test')
        self.assertEqual(call_count[0], 1)
        
        # 第二次调用，应该从缓存获取
        result2 = test_func('test')
        self.assertEqual(result2, 'result_test')
        self.assertEqual(call_count[0], 1)  # 不应该再次执行
        
        # 不同参数，应该再次执行
        result3 = test_func('test2')
        self.assertEqual(result3, 'result_test2')
        self.assertEqual(call_count[0], 2)
    
    def test_get_or_set_cache(self):
        """测试get_or_set_cache函数"""
        call_count = [0]
        
        def get_value():
            call_count[0] += 1
            return 'cached_value'
        
        # 第一次调用
        result1 = get_or_set_cache('test_key', get_value)
        self.assertEqual(result1, 'cached_value')
        self.assertEqual(call_count[0], 1)
        
        # 第二次调用，应该从缓存获取
        result2 = get_or_set_cache('test_key', get_value)
        self.assertEqual(result2, 'cached_value')
        self.assertEqual(call_count[0], 1)  # 不应该再次执行

