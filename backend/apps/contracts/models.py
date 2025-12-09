from django.db import models
from apps.users.models import User


class Contract(models.Model):
    """合同表"""
    CONTRACT_TYPE_CHOICES = [
        ('procurement', '采购合同'),
        ('sales', '销售合同'),
        ('labor', '劳动合同'),
        ('service', '服务合同'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('reviewing', '审核中'),
        ('reviewed', '已审核'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('signed', '已签署'),
    ]
    
    contract_no = models.CharField(max_length=100, unique=True, verbose_name='合同编号')
    title = models.CharField(max_length=500, verbose_name='合同标题')
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPE_CHOICES, verbose_name='合同类型')
    industry = models.CharField(max_length=50, blank=True, verbose_name='所属行业')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    content = models.JSONField(null=True, blank=True, verbose_name='合同内容')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='合同文件路径')
    file_format = models.CharField(max_length=20, blank=True, verbose_name='文件格式')
    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='使用的模板')
    drafter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drafted_contracts', verbose_name='起草人')
    current_version = models.IntegerField(default=1, verbose_name='当前版本号')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'contracts_contract'
        verbose_name = '合同'
        verbose_name_plural = '合同'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ContractVersion(models.Model):
    """合同版本表"""
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='versions', verbose_name='合同')
    version = models.IntegerField(verbose_name='版本号')
    content = models.JSONField(null=True, blank=True, verbose_name='版本内容')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='版本文件路径')
    change_summary = models.TextField(blank=True, verbose_name='变更摘要')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='变更人')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'contracts_contract_version'
        verbose_name = '合同版本'
        verbose_name_plural = '合同版本'
        unique_together = [['contract', 'version']]
        ordering = ['-version']

    def __str__(self):
        return f'{self.contract.title} - v{self.version}'


class Template(models.Model):
    """合同模板表"""
    name = models.CharField(max_length=200, verbose_name='模板名称')
    contract_type = models.CharField(max_length=50, verbose_name='合同类型')
    industry = models.CharField(max_length=50, blank=True, verbose_name='适用行业')
    category = models.CharField(max_length=50, blank=True, verbose_name='模板分类')
    content = models.TextField(verbose_name='模板内容')
    description = models.TextField(blank=True, verbose_name='模板描述')
    tags = models.JSONField(null=True, blank=True, verbose_name='标签列表')
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    is_enterprise = models.BooleanField(default=False, verbose_name='是否企业模板')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    enterprise_id = models.BigIntegerField(null=True, blank=True, verbose_name='企业ID')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'contracts_template'
        verbose_name = '合同模板'
        verbose_name_plural = '合同模板'
        ordering = ['-usage_count', '-created_at']

    def __str__(self):
        return self.name


class UserHabit(models.Model):
    """用户习惯表"""
    HABIT_TYPE_CHOICES = [
        ('clause_preference', '条款偏好'),
        ('template_preference', '模板偏好'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits', verbose_name='用户')
    habit_type = models.CharField(max_length=50, choices=HABIT_TYPE_CHOICES, verbose_name='习惯类型')
    habit_key = models.CharField(max_length=200, verbose_name='习惯键')
    habit_value = models.JSONField(null=True, blank=True, verbose_name='习惯值')
    frequency = models.IntegerField(default=1, verbose_name='使用频率')
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='最后使用时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'contracts_user_habit'
        verbose_name = '用户习惯'
        verbose_name_plural = '用户习惯'
        unique_together = [['user', 'habit_type', 'habit_key']]

    def __str__(self):
        return f'{self.user.username} - {self.habit_type}'

