# Generated migration for adding reviewer_level field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_audit_log_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reviewer_level',
            field=models.CharField(
                blank=True,
                choices=[('level1', '一级审核员'), ('level2', '二级审核员'), ('level3', '三级审核员（高级）')],
                help_text='仅当角色为审核员时有效',
                max_length=20,
                null=True,
                verbose_name='审核员层级'
            ),
        ),
    ]

