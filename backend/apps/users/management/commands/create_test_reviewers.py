"""
创建测试审核员用户的管理命令
用法: python manage.py create_test_reviewers
"""

from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = '创建测试审核员用户（不同层级的审核员）'

    def handle(self, *args, **options):
        self.stdout.write('开始创建测试审核员用户...')

        # 定义测试用户数据
        test_reviewers = [
            {
                'username': 'reviewer_level1_1',
                'email': 'reviewer1@test.com',
                'real_name': '一级审核员-张三',
                'role': 'reviewer',
                'reviewer_level': 'level1',
                'password': 'test123456',
            },
            {
                'username': 'reviewer_level1_2',
                'email': 'reviewer2@test.com',
                'real_name': '一级审核员-李四',
                'role': 'reviewer',
                'reviewer_level': 'level1',
                'password': 'test123456',
            },
            {
                'username': 'reviewer_level2_1',
                'email': 'reviewer3@test.com',
                'real_name': '二级审核员-王五',
                'role': 'reviewer',
                'reviewer_level': 'level2',
                'password': 'test123456',
            },
            {
                'username': 'reviewer_level2_2',
                'email': 'reviewer4@test.com',
                'real_name': '二级审核员-赵六',
                'role': 'reviewer',
                'reviewer_level': 'level2',
                'password': 'test123456',
            },
            {
                'username': 'reviewer_level3_1',
                'email': 'reviewer5@test.com',
                'real_name': '三级审核员-孙七',
                'role': 'reviewer',
                'reviewer_level': 'level3',
                'password': 'test123456',
            },
            {
                'username': 'reviewer_level3_2',
                'email': 'reviewer6@test.com',
                'real_name': '三级审核员-周八',
                'role': 'reviewer',
                'reviewer_level': 'level3',
                'password': 'test123456',
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for reviewer_data in test_reviewers:
            username = reviewer_data['username']
            password = reviewer_data.pop('password')

            # 检查用户是否已存在
            user, created = User.objects.get_or_create(
                username=username,
                defaults=reviewer_data
            )

            if created:
                user.set_password(password)
                user.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建用户: {username} ({reviewer_data["real_name"]})')
                )
            else:
                # 如果用户已存在，更新信息
                updated = False
                for key, value in reviewer_data.items():
                    if getattr(user, key) != value:
                        setattr(user, key, value)
                        updated = True
                
                if updated:
                    user.set_password(password)
                    user.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ 更新用户: {username} ({reviewer_data["real_name"]})')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.NOTICE(f'- 跳过用户: {username} (已存在且无需更新)')
                    )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'创建完成！'))
        self.stdout.write(f'  新建: {created_count} 个用户')
        self.stdout.write(f'  更新: {updated_count} 个用户')
        self.stdout.write(f'  跳过: {skipped_count} 个用户')
        self.stdout.write('')
        self.stdout.write('测试用户登录信息:')
        self.stdout.write('  用户名: reviewer_level1_1, reviewer_level1_2, reviewer_level2_1, reviewer_level2_2, reviewer_level3_1, reviewer_level3_2')
        self.stdout.write('  密码: test123456')
        self.stdout.write('')

