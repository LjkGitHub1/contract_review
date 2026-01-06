"""
创建缺失的数据库表
如果迁移显示已应用但表不存在，可以使用此命令直接创建表
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '创建缺失的数据库表（users_role_permission 和 users_user_role）'

    def handle(self, *args, **options):
        self.stdout.write('开始检查并创建缺失的数据库表...')
        
        with connection.cursor() as cursor:
            # 检查并创建 users_role_permission 表
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'users_role_permission'
            """)
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                self.stdout.write('创建 users_role_permission 表...')
                cursor.execute("""
                    CREATE TABLE `users_role_permission` (
                        `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
                        `role_id` BIGINT NOT NULL,
                        `permission_id` BIGINT NOT NULL,
                        `created_at` DATETIME(6) NOT NULL,
                        UNIQUE KEY `users_role_permission_role_id_permission_id_uniq` (`role_id`, `permission_id`),
                        INDEX `users_role_permission_role_id_idx` (`role_id`),
                        INDEX `users_role_permission_permission_id_idx` (`permission_id`),
                        FOREIGN KEY (`role_id`) REFERENCES `users_role` (`id`) ON DELETE CASCADE,
                        FOREIGN KEY (`permission_id`) REFERENCES `users_permission` (`id`) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表'
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ users_role_permission 表创建成功'))
            else:
                self.stdout.write('  - users_role_permission 表已存在')
            
            # 检查并创建 users_user_role 表
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'users_user_role'
            """)
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                self.stdout.write('创建 users_user_role 表...')
                cursor.execute("""
                    CREATE TABLE `users_user_role` (
                        `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
                        `user_id` BIGINT NOT NULL,
                        `role_id` BIGINT NOT NULL,
                        `created_at` DATETIME(6) NOT NULL,
                        UNIQUE KEY `users_user_role_user_id_role_id_uniq` (`user_id`, `role_id`),
                        INDEX `users_user_role_user_id_idx` (`user_id`),
                        INDEX `users_user_role_role_id_idx` (`role_id`),
                        FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE CASCADE,
                        FOREIGN KEY (`role_id`) REFERENCES `users_role` (`id`) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表'
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ users_user_role 表创建成功'))
            else:
                self.stdout.write('  - users_user_role 表已存在')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('表创建检查完成！'))
        self.stdout.write('现在可以运行: python manage.py create_test_permissions')

