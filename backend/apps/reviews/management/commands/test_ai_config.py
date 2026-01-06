"""
测试AI模型配置
使用方法: python manage.py test_ai_config
"""
from django.core.management.base import BaseCommand
from apps.reviews.models import AIModelConfig


class Command(BaseCommand):
    help = '测试AI模型配置'

    def handle(self, *args, **options):
        self.stdout.write('测试AI模型配置...')
        
        try:
            # 测试查询
            count = AIModelConfig.objects.count()
            self.stdout.write(self.style.SUCCESS(f'✓ 数据库表存在，当前有 {count} 条配置'))
            
            # 测试序列化
            from apps.reviews.serializers import AIModelConfigSerializer
            configs = AIModelConfig.objects.all()[:5]
            serializer = AIModelConfigSerializer(configs, many=True)
            self.stdout.write(self.style.SUCCESS(f'✓ 序列化器正常工作，序列化了 {len(serializer.data)} 条数据'))
            
            if serializer.data:
                self.stdout.write('示例数据：')
                for item in serializer.data[:2]:
                    self.stdout.write(f'  - {item.get("name", "N/A")}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ 错误: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())

