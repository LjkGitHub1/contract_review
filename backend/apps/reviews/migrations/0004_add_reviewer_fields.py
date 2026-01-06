# Generated migration for adding reviewer and reviewer_level fields to ReviewTask model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_reviewfocusconfig'),
        ('users', '0003_add_reviewer_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewtask',
            name='reviewer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='review_tasks',
                to='users.user',
                verbose_name='审核员'
            ),
        ),
        migrations.AddField(
            model_name='reviewtask',
            name='reviewer_level',
            field=models.CharField(
                blank=True,
                choices=[('level1', '一级审核员'), ('level2', '二级审核员'), ('level3', '三级审核员（高级）')],
                help_text='审核任务的审核员层级',
                max_length=20,
                null=True,
                verbose_name='审核员层级'
            ),
        ),
    ]

