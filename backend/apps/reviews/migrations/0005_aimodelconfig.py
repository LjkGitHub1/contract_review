# Generated migration for AIModelConfig model

from django.db import migrations, models
import django.db.models.deletion


def default_available_models():
    """默认可用模型列表（可序列化）"""
    return []


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_add_reviewer_fields'),
        ('users', '0003_add_reviewer_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIModelConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='配置名称')),
                ('provider', models.CharField(choices=[('siliconflow', '硅基流动'), ('openai', 'OpenAI'), ('anthropic', 'Anthropic'), ('custom', '自定义')], default='siliconflow', max_length=50, verbose_name='服务提供商')),
                ('api_key', models.CharField(help_text='硅基流动的API密钥', max_length=500, verbose_name='API密钥')),
                ('api_base_url', models.CharField(default='https://api.siliconflow.cn/v1', help_text='硅基流动API地址：https://api.siliconflow.cn/v1', max_length=500, verbose_name='API基础地址')),
                ('available_models', models.JSONField(default=default_available_models, help_text='JSON格式，包含可用模型列表，如：["deepseek-chat", "qwen-plus", "gpt-3.5-turbo"]', verbose_name='可用模型列表')),
                ('default_model', models.CharField(blank=True, help_text='从可用模型列表中选择一个作为默认模型', max_length=100, verbose_name='默认模型')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('is_default', models.BooleanField(default=False, help_text='只能有一个配置为系统默认', verbose_name='是否系统默认')),
                ('description', models.TextField(blank=True, verbose_name='配置描述')),
                ('temperature', models.FloatField(default=0.7, help_text='控制输出的随机性，范围0-2', verbose_name='温度参数')),
                ('max_tokens', models.IntegerField(default=2000, help_text='生成内容的最大长度', verbose_name='最大Token数')),
                ('timeout', models.IntegerField(default=30, verbose_name='超时时间（秒）')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_ai_configs', to='users.user', verbose_name='创建人')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_ai_configs', to='users.user', verbose_name='更新人')),
            ],
            options={
                'verbose_name': 'AI模型配置',
                'verbose_name_plural': 'AI模型配置',
                'db_table': 'reviews_ai_model_config',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
    ]

