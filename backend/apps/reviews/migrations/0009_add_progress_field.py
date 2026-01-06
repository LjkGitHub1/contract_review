# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0008_add_reviewer_assignments_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewtask',
            name='progress',
            field=models.JSONField(blank=True, help_text='JSON格式，存储审核进度信息，如：{"current_step": "提取合同内容", "progress": 20, "steps": [...]}', null=True, verbose_name='审核进度'),
        ),
    ]

