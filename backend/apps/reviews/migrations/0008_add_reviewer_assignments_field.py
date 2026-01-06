# Generated migration for adding reviewer_assignments field to ReviewTask model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0007_alter_aimodelconfig_available_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewtask',
            name='reviewer_assignments',
            field=models.JSONField(
                blank=True,
                help_text='JSON格式，配置每个层级对应的审核员，如：{"level1": 1, "level2": 2, "level3": 3}',
                null=True,
                verbose_name='审核员分配'
            ),
        ),
    ]

