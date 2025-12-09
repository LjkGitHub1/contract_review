# Generated migration to create audit_log table if it doesn't exist

from django.db import migrations, models
import django.db.models.deletion


def create_audit_log_table_if_not_exists(apps, schema_editor):
    """如果表不存在则创建"""
    db_alias = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        # 检查表是否存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'users_audit_log'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            # 创建表
            cursor.execute("""
                CREATE TABLE `users_audit_log` (
                    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
                    `action` VARCHAR(100) NOT NULL COMMENT '操作类型',
                    `resource_type` VARCHAR(50) DEFAULT NULL COMMENT '资源类型',
                    `resource_id` BIGINT DEFAULT NULL COMMENT '资源ID',
                    `ip_address` VARCHAR(39) DEFAULT NULL COMMENT 'IP地址',
                    `user_agent` VARCHAR(500) DEFAULT NULL COMMENT '用户代理',
                    `request_data` JSON DEFAULT NULL COMMENT '请求数据',
                    `response_data` JSON DEFAULT NULL COMMENT '响应数据',
                    `status` VARCHAR(20) DEFAULT NULL COMMENT '操作状态',
                    `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
                    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间',
                    `user_id` BIGINT DEFAULT NULL COMMENT '用户ID',
                    INDEX `idx_user` (`user_id`),
                    INDEX `idx_action` (`action`),
                    INDEX `idx_created` (`created_at`),
                    FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计日志表'
            """)


def reverse_create_audit_log_table(apps, schema_editor):
    """回滚操作：删除表"""
    db_alias = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS `users_audit_log`")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_audit_log_table_if_not_exists,
            reverse_create_audit_log_table,
        ),
    ]

