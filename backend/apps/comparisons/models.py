from django.db import models
from apps.users.models import User
from apps.contracts.models import Contract, Template


class ComparisonTask(models.Model):
    """对比任务表"""
    TASK_TYPE_CHOICES = [
        ('version', '版本对比'),
        ('template', '模板对比'),
        ('cross_industry', '跨行业对比'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, verbose_name='对比类型')
    source_contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='source_comparisons', null=True, blank=True, verbose_name='源合同')
    target_contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='target_comparisons', null=True, blank=True, verbose_name='目标合同')
    source_version = models.IntegerField(null=True, blank=True, verbose_name='源版本号')
    target_version = models.IntegerField(null=True, blank=True, verbose_name='目标版本号')
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='模板')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    result_data = models.JSONField(null=True, blank=True, verbose_name='对比结果数据')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')

    class Meta:
        db_table = 'comparisons_comparison_task'
        verbose_name = '对比任务'
        verbose_name_plural = '对比任务'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_task_type_display()} - {self.created_at}'


class ComparisonDiff(models.Model):
    """对比差异表"""
    DIFF_TYPE_CHOICES = [
        ('added', '新增'),
        ('deleted', '删除'),
        ('modified', '修改'),
    ]
    
    DIFF_LEVEL_CHOICES = [
        ('clause', '条款级'),
        ('field', '字段级'),
        ('risk', '风险级'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('high', '高风险'),
        ('medium', '中风险'),
        ('low', '低风险'),
    ]
    
    comparison_task = models.ForeignKey(ComparisonTask, on_delete=models.CASCADE, related_name='diffs', verbose_name='对比任务')
    diff_type = models.CharField(max_length=50, choices=DIFF_TYPE_CHOICES, verbose_name='差异类型')
    diff_level = models.CharField(max_length=50, choices=DIFF_LEVEL_CHOICES, blank=True, verbose_name='差异级别')
    source_content = models.TextField(blank=True, verbose_name='源内容')
    target_content = models.TextField(blank=True, verbose_name='目标内容')
    clause_id = models.CharField(max_length=100, blank=True, verbose_name='条款ID')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True, verbose_name='风险等级')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'comparisons_comparison_diff'
        verbose_name = '对比差异'
        verbose_name_plural = '对比差异'
        ordering = ['-risk_level', 'created_at']

    def __str__(self):
        return f'{self.get_diff_type_display()} - {self.diff_level}'

