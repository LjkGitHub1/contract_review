from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('用户必须提供邮箱')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置 is_superuser=True')
        
        return self.create_user(username, email, password, **extra_fields)


class Department(models.Model):
    """部门表"""
    name = models.CharField(max_length=100, verbose_name='部门名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='父部门')
    code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='部门编码')
    description = models.TextField(blank=True, verbose_name='部门描述')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users_department'
        verbose_name = '部门'
        verbose_name_plural = '部门'

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """用户表"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('reviewer', '审核员'),
        ('drafter', '起草人'),
    ]
    
    username = models.CharField(max_length=150, unique=True, verbose_name='用户名')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    real_name = models.CharField(max_length=100, blank=True, verbose_name='真实姓名')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    avatar = models.URLField(max_length=500, blank=True, verbose_name='头像URL')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='部门')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='drafter', verbose_name='角色')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_staff = models.BooleanField(default=False, verbose_name='是否员工')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class Permission(models.Model):
    """权限表"""
    name = models.CharField(max_length=100, verbose_name='权限名称')
    code = models.CharField(max_length=100, unique=True, verbose_name='权限编码')
    resource = models.CharField(max_length=100, blank=True, verbose_name='资源类型')
    action = models.CharField(max_length=50, blank=True, verbose_name='操作类型')
    description = models.TextField(blank=True, verbose_name='权限描述')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users_permission'
        verbose_name = '权限'
        verbose_name_plural = '权限'

    def __str__(self):
        return self.name


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=100, verbose_name='角色名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='角色编码')
    description = models.TextField(blank=True, verbose_name='角色描述')
    permissions = models.ManyToManyField(Permission, through='RolePermission', verbose_name='权限')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users_role'
        verbose_name = '角色'
        verbose_name_plural = '角色'

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """角色权限关联表"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name='权限')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'users_role_permission'
        unique_together = [['role', 'permission']]
        verbose_name = '角色权限'
        verbose_name_plural = '角色权限'


class UserRole(models.Model):
    """用户角色关联表"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'users_user_role'
        unique_together = [['user', 'role']]
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'


class AuditLog(models.Model):
    """审计日志表"""
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    action = models.CharField(max_length=100, verbose_name='操作类型')
    resource_type = models.CharField(max_length=50, blank=True, verbose_name='资源类型')
    resource_id = models.BigIntegerField(null=True, blank=True, verbose_name='资源ID')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.CharField(max_length=500, blank=True, verbose_name='用户代理')
    request_data = models.JSONField(null=True, blank=True, verbose_name='请求数据')
    response_data = models.JSONField(null=True, blank=True, verbose_name='响应数据')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, verbose_name='操作状态')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'users_audit_log'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} - {self.created_at}'

