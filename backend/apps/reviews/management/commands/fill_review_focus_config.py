"""
填充审核重点配置测试数据
使用方法: python manage.py fill_review_focus_config
"""
from django.core.management.base import BaseCommand
from apps.reviews.models import ReviewFocusConfig
from apps.users.models import User


class Command(BaseCommand):
    help = '填充审核重点配置测试数据'

    def handle(self, *args, **options):
        self.stdout.write('开始填充审核重点配置测试数据...')
        
        # 获取或创建管理员用户（用于created_by和updated_by）
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()
        
        # 一级审核员配置
        level1_config, created = ReviewFocusConfig.objects.get_or_create(
            level='level1',
            defaults={
                'level_name': '一级审核员',
                'focus_points': [
                    '格式规范',
                    '基础条款完整性',
                    '基本信息准确性',
                    '条款编号正确性'
                ],
                'focus_description': '一级审核员重点关注合同格式、基础条款和基本信息。确保合同格式符合要求，基础信息准确完整，基础条款齐全，条款编号正确。',
                'review_standards': '符合合同格式要求，基础信息准确完整，基础条款齐全，条款编号正确',
                'attention_items': [
                    '合同格式是否符合要求',
                    '条款编号是否正确',
                    '基本信息是否准确',
                    '基础条款是否完整',
                    '合同标题是否清晰',
                    '合同编号是否规范'
                ],
                'is_active': True,
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ 创建一级审核员配置'))
        else:
            self.stdout.write(self.style.WARNING(f'- 一级审核员配置已存在，跳过'))

        # 二级审核员配置
        level2_config, created = ReviewFocusConfig.objects.get_or_create(
            level='level2',
            defaults={
                'level_name': '二级审核员',
                'focus_points': [
                    '法律合规性',
                    '风险识别',
                    '条款合理性',
                    '权利义务平衡',
                    '违约责任约定'
                ],
                'focus_description': '二级审核员重点关注法律合规性、风险识别、条款合理性和权利义务平衡。确保合同条款符合法律法规，识别潜在风险，评估条款合理性，确保双方权利义务平衡。',
                'review_standards': '法律合规性、风险等级评估、条款合理性分析、权利义务平衡检查',
                'attention_items': [
                    '合同条款是否符合法律法规',
                    '是否存在法律风险',
                    '条款是否合理',
                    '双方权利义务是否平衡',
                    '违约责任约定是否合理',
                    '争议解决方式是否明确',
                    '合同生效条件是否明确'
                ],
                'is_active': True,
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ 创建二级审核员配置'))
        else:
            self.stdout.write(self.style.WARNING(f'- 二级审核员配置已存在，跳过'))

        # 三级审核员配置（高级）
        level3_config, created = ReviewFocusConfig.objects.get_or_create(
            level='level3',
            defaults={
                'level_name': '三级审核员（高级）',
                'focus_points': [
                    '重大风险',
                    '战略层面',
                    '商业决策',
                    '最终批准',
                    '战略价值评估'
                ],
                'focus_description': '三级审核员（高级）重点关注重大风险、战略层面、商业决策和最终批准。评估重大风险是否可控，是否符合企业战略，评估商业价值，做出最终决策。',
                'review_standards': '重大风险是否可控，是否符合企业战略，商业价值评估，是否批准签署',
                'attention_items': [
                    '重大风险点是否可控',
                    '是否符合企业战略',
                    '商业价值评估',
                    '最终决策',
                    '合同对企业的影响',
                    '长期战略价值',
                    '竞争对手分析'
                ],
                'is_active': True,
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ 创建三级审核员配置'))
        else:
            self.stdout.write(self.style.WARNING(f'- 三级审核员配置已存在，跳过'))

        self.stdout.write(self.style.SUCCESS('\n审核重点配置测试数据填充完成！'))
        self.stdout.write(f'共创建/更新 {ReviewFocusConfig.objects.count()} 条配置记录')

