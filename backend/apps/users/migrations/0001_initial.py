# Generated manually to fix migration dependency issue

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='部门名称')),
                ('code', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='部门编码')),
                ('description', models.TextField(blank=True, verbose_name='部门描述')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='是否删除')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.department', verbose_name='父部门')),
            ],
            options={
                'verbose_name': '部门',
                'verbose_name_plural': '部门',
                'db_table': 'users_department',
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='权限名称')),
                ('code', models.CharField(max_length=100, unique=True, verbose_name='权限编码')),
                ('resource', models.CharField(blank=True, max_length=100, verbose_name='资源类型')),
                ('action', models.CharField(blank=True, max_length=50, verbose_name='操作类型')),
                ('description', models.TextField(blank=True, verbose_name='权限描述')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='是否删除')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '权限',
                'verbose_name_plural': '权限',
                'db_table': 'users_permission',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='角色名称')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='角色编码')),
                ('description', models.TextField(blank=True, verbose_name='角色描述')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='是否删除')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '角色',
                'verbose_name_plural': '角色',
                'db_table': 'users_role',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='用户名')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='邮箱')),
                ('real_name', models.CharField(blank=True, max_length=100, verbose_name='真实姓名')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='手机号')),
                ('avatar', models.URLField(blank=True, max_length=500, verbose_name='头像URL')),
                ('role', models.CharField(choices=[('admin', '管理员'), ('reviewer', '审核员'), ('drafter', '起草人')], default='drafter', max_length=50, verbose_name='角色')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否激活')),
                ('is_staff', models.BooleanField(default=False, verbose_name='是否员工')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='是否删除')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.department', verbose_name='部门')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'db_table': 'users_user',
            },
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.permission', verbose_name='权限')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.role', verbose_name='角色')),
            ],
            options={
                'verbose_name': '角色权限',
                'verbose_name_plural': '角色权限',
                'db_table': 'users_role_permission',
                'unique_together': {('role', 'permission')},
            },
        ),
        migrations.AddField(
            model_name='role',
            name='permissions',
            field=models.ManyToManyField(through='users.RolePermission', to='users.permission', verbose_name='权限'),
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.role', verbose_name='角色')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户角色',
                'verbose_name_plural': '用户角色',
                'db_table': 'users_user_role',
                'unique_together': {('user', 'role')},
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100, verbose_name='操作类型')),
                ('resource_type', models.CharField(blank=True, max_length=50, verbose_name='资源类型')),
                ('resource_id', models.BigIntegerField(blank=True, null=True, verbose_name='资源ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('user_agent', models.CharField(blank=True, max_length=500, verbose_name='用户代理')),
                ('request_data', models.JSONField(blank=True, null=True, verbose_name='请求数据')),
                ('response_data', models.JSONField(blank=True, null=True, verbose_name='响应数据')),
                ('status', models.CharField(blank=True, choices=[('success', '成功'), ('failed', '失败')], max_length=20, verbose_name='操作状态')),
                ('error_message', models.TextField(blank=True, verbose_name='错误信息')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '审计日志',
                'verbose_name_plural': '审计日志',
                'db_table': 'users_audit_log',
                'ordering': ['-created_at'],
            },
        ),
    ]

