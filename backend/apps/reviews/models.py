from django.db import models
from apps.users.models import User
from apps.contracts.models import Contract


def default_available_models():
    """默认可用模型列表（可序列化）"""
    return []


class ReviewTask(models.Model):
    """审核任务表"""
    TASK_TYPE_CHOICES = [
        ('auto', '自动审核'),
        ('manual', '人工审核'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('ai_processing', 'AI审核中'),
        ('ai_completed', 'AI审核完成'),
        ('manual_reviewing', '人工审核中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='review_tasks', verbose_name='合同')
    contract_version = models.IntegerField(null=True, blank=True, verbose_name='合同版本号')
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, default='auto', verbose_name='任务类型')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    priority = models.IntegerField(default=0, verbose_name='优先级')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='review_tasks', verbose_name='审核员')
    reviewer_level = models.CharField(
        max_length=20,
        choices=[
            ('level1', '一级审核员'),
            ('level2', '二级审核员'),
            ('level3', '三级审核员（高级）'),
        ],
        null=True,
        blank=True,
        verbose_name='审核员层级',
        help_text='审核任务的审核员层级'
    )
    review_levels = models.JSONField(
        null=True,
        blank=True,
        verbose_name='审核层级配置',
        help_text='JSON格式，配置需要哪些审核层级，如：["level1", "level3"]'
    )
    reviewer_assignments = models.JSONField(
        null=True,
        blank=True,
        verbose_name='审核员分配',
        help_text='JSON格式，配置每个层级对应的审核员，如：{"level1": 1, "level2": 2, "level3": 3}'
    )
    celery_task_id = models.CharField(max_length=255, blank=True, verbose_name='Celery任务ID')
    progress = models.JSONField(
        null=True,
        blank=True,
        verbose_name='审核进度',
        help_text='JSON格式，存储审核进度信息，如：{"current_step": "提取合同内容", "progress": 20, "steps": [...]}'
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'reviews_review_task'
        verbose_name = '审核任务'
        verbose_name_plural = '审核任务'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.contract.title} - {self.get_status_display()}'


class ReviewResult(models.Model):
    """审核结果表"""
    RISK_LEVEL_CHOICES = [
        ('high', '高风险'),
        ('medium', '中风险'),
        ('low', '低风险'),
    ]
    
    review_task = models.OneToOneField(ReviewTask, on_delete=models.CASCADE, related_name='result', verbose_name='审核任务')
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='review_results', verbose_name='合同')
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='总体评分')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True, verbose_name='风险等级')
    risk_count = models.IntegerField(default=0, verbose_name='风险数量')
    summary = models.TextField(blank=True, verbose_name='审核摘要')
    report_path = models.CharField(max_length=500, blank=True, verbose_name='报告文件路径')
    report_format = models.CharField(max_length=20, blank=True, verbose_name='报告格式')
    review_data = models.JSONField(null=True, blank=True, verbose_name='详细审核数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'reviews_review_result'
        verbose_name = '审核结果'
        verbose_name_plural = '审核结果'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.contract.title} - 审核结果'


class ReviewOpinion(models.Model):
    """审核意见表"""
    OPINION_TYPE_CHOICES = [
        ('risk', '风险'),
        ('suggestion', '建议'),
        ('warning', '警告'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('high', '高风险'),
        ('medium', '中风险'),
        ('low', '低风险'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
    ]
    
    review_result = models.ForeignKey(ReviewResult, on_delete=models.CASCADE, related_name='opinions', verbose_name='审核结果')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='审核人')
    clause_id = models.CharField(max_length=100, blank=True, verbose_name='条款ID')
    clause_content = models.TextField(blank=True, verbose_name='条款内容')
    opinion_type = models.CharField(max_length=50, choices=OPINION_TYPE_CHOICES, blank=True, verbose_name='意见类型')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True, verbose_name='风险等级')
    opinion_content = models.TextField(verbose_name='意见内容')
    legal_basis = models.TextField(blank=True, verbose_name='法律依据')
    suggestion = models.TextField(blank=True, verbose_name='修改建议')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'reviews_review_opinion'
        verbose_name = '审核意见'
        verbose_name_plural = '审核意见'
        ordering = ['-risk_level', '-created_at']

    def __str__(self):
        return f'{self.opinion_content[:50]}...'


class ReviewCycle(models.Model):
    """审核意见闭环表"""
    STATUS_CHOICES = [
        ('reviewing', '审核中'),
        ('modifying', '修改中'),
        ('completed', '已完成'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='review_cycles', verbose_name='合同')
    cycle_no = models.IntegerField(verbose_name='循环序号')
    review_result = models.ForeignKey(ReviewResult, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='审核结果')
    opinion_summary = models.TextField(blank=True, verbose_name='意见汇总')
    modification_summary = models.TextField(blank=True, verbose_name='修改摘要')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='reviewing', verbose_name='状态')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_cycles', verbose_name='提交人')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_cycles', verbose_name='修改人')
    modified_at = models.DateTimeField(null=True, blank=True, verbose_name='修改时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'reviews_review_cycle'
        verbose_name = '审核闭环'
        verbose_name_plural = '审核闭环'
        unique_together = [['contract', 'cycle_no']]
        ordering = ['-cycle_no']

    def __str__(self):
        return f'{self.contract.title} - 第{self.cycle_no}轮审核'


class ReviewFocusConfig(models.Model):
    """审核重点配置表"""
    LEVEL_CHOICES = [
        ('level1', '一级审核员'),
        ('level2', '二级审核员'),
        ('level3', '三级审核员（高级）'),
    ]
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, unique=True, verbose_name='审核层级')
    level_name = models.CharField(max_length=100, verbose_name='层级名称')
    focus_points = models.JSONField(verbose_name='审核重点', help_text='JSON格式，包含重点列表')
    focus_description = models.TextField(verbose_name='审核重点描述')
    review_standards = models.TextField(blank=True, verbose_name='审核标准')
    attention_items = models.JSONField(null=True, blank=True, verbose_name='关注事项', help_text='JSON格式，包含关注事项列表')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_focus_configs', verbose_name='更新人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'reviews_review_focus_config'
        verbose_name = '审核重点配置'
        verbose_name_plural = '审核重点配置'
        ordering = ['level']

    def __str__(self):
        return f'{self.get_level_display()} - {self.level_name}'


class AIModelConfig(models.Model):
    """AI模型配置表"""
    PROVIDER_CHOICES = [
        ('siliconflow', '硅基流动'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('custom', '自定义'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='配置名称')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, default='siliconflow', verbose_name='服务提供商')
    api_key = models.CharField(max_length=500, verbose_name='API密钥', help_text='硅基流动的API密钥')
    api_base_url = models.CharField(
        max_length=500,
        default='https://api.siliconflow.cn/v1',
        verbose_name='API基础地址',
        help_text='硅基流动API地址：https://api.siliconflow.cn/v1'
    )
    available_models = models.JSONField(
        default=default_available_models,
        verbose_name='可用模型列表',
        help_text='JSON格式，包含可用模型列表，如：["deepseek-chat", "qwen-plus", "gpt-3.5-turbo"]'
    )
    default_model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='默认模型',
        help_text='从可用模型列表中选择一个作为默认模型'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_default = models.BooleanField(default=False, verbose_name='是否系统默认', help_text='只能有一个配置为系统默认')
    description = models.TextField(blank=True, verbose_name='配置描述')
    temperature = models.FloatField(default=0.7, verbose_name='温度参数', help_text='控制输出的随机性，范围0-2')
    max_tokens = models.IntegerField(default=2000, verbose_name='最大Token数', help_text='生成内容的最大长度')
    timeout = models.IntegerField(default=30, verbose_name='超时时间（秒）')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_ai_configs', verbose_name='创建人')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_ai_configs', verbose_name='更新人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'reviews_ai_model_config'
        verbose_name = 'AI模型配置'
        verbose_name_plural = 'AI模型配置'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_provider_display()})'
    
    def save(self, *args, **kwargs):
        # 如果设置为系统默认，将其他配置的is_default设为False
        if self.is_default:
            AIModelConfig.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
