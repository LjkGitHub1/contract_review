from django.db import models
from apps.users.models import User
from apps.reviews.models import ReviewResult
from apps.clauses.models import ContractClause


class RiskIdentification(models.Model):
    """风险识别记录表"""
    RISK_TYPE_CHOICES = [
        ('invalid', '无效条款'),
        ('missing', '缺失条款'),
        ('illegal', '违法条款'),
        ('non_compliant', '不合规条款'),
    ]
    
    RISK_CATEGORY_CHOICES = [
        ('legality', '合法性'),
        ('compliance', '合规性'),
        ('completeness', '完整性'),
        ('financial', '财务风险'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('high', '高风险'),
        ('medium', '中风险'),
        ('low', '低风险'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('handled', '已处理'),
        ('ignored', '已忽略'),
    ]
    
    review_result = models.ForeignKey(ReviewResult, on_delete=models.CASCADE, related_name='risks', verbose_name='审核结果')
    contract_id = models.BigIntegerField(verbose_name='合同ID')
    clause = models.ForeignKey(ContractClause, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联条款')
    risk_type = models.CharField(max_length=50, choices=RISK_TYPE_CHOICES, verbose_name='风险类型')
    risk_category = models.CharField(max_length=50, choices=RISK_CATEGORY_CHOICES, blank=True, verbose_name='风险分类')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, verbose_name='风险等级')
    risk_description = models.TextField(verbose_name='风险描述')
    risk_location = models.CharField(max_length=200, blank=True, verbose_name='风险位置')
    legal_basis = models.TextField(blank=True, verbose_name='法律依据')
    suggestion = models.TextField(blank=True, verbose_name='处理建议')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态')
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='处理人')
    handled_at = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'risks_risk_identification'
        verbose_name = '风险识别'
        verbose_name_plural = '风险识别'
        ordering = ['-risk_level', '-created_at']

    def __str__(self):
        return f'{self.get_risk_type_display()} - {self.risk_description[:50]}'

