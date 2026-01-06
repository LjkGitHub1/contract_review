# Generated migration for ReviewFocusConfig model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewFocusConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('level1', '一级审核员'), ('level2', '二级审核员'), ('level3', '三级审核员（高级）')], max_length=20, unique=True, verbose_name='审核层级')),
                ('level_name', models.CharField(max_length=100, verbose_name='层级名称')),
                ('focus_points', models.JSONField(help_text='JSON格式，包含重点列表', verbose_name='审核重点')),
                ('focus_description', models.TextField(verbose_name='审核重点描述')),
                ('review_standards', models.TextField(blank=True, verbose_name='审核标准')),
                ('attention_items', models.JSONField(blank=True, help_text='JSON格式，包含关注事项列表', null=True, verbose_name='关注事项')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user', verbose_name='创建人')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_focus_configs', to='users.user', verbose_name='更新人')),
            ],
            options={
                'verbose_name': '审核重点配置',
                'verbose_name_plural': '审核重点配置',
                'db_table': 'reviews_review_focus_config',
                'ordering': ['level'],
            },
        ),
    ]

