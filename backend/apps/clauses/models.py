from django.db import models
from apps.users.models import User
from apps.contracts.models import Contract


class ContractClause(models.Model):
    """合同条款表"""
    CLAUSE_TYPE_CHOICES = [
        ('party', '合同主体'),
        ('subject', '标的物'),
        ('period', '履行期限'),
        ('liability', '违约责任'),
        ('payment', '付款方式'),
        ('other', '其他'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='clauses', verbose_name='合同')
    contract_version = models.IntegerField(null=True, blank=True, verbose_name='合同版本号')
    clause_no = models.CharField(max_length=50, blank=True, verbose_name='条款编号')
    clause_type = models.CharField(max_length=50, choices=CLAUSE_TYPE_CHOICES, verbose_name='条款类型')
    clause_title = models.CharField(max_length=500, blank=True, verbose_name='条款标题')
    clause_content = models.TextField(verbose_name='条款内容')
    start_position = models.IntegerField(null=True, blank=True, verbose_name='起始位置')
    end_position = models.IntegerField(null=True, blank=True, verbose_name='结束位置')
    extracted_data = models.JSONField(null=True, blank=True, verbose_name='提取的结构化数据')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='识别置信度')
    is_confirmed = models.BooleanField(default=False, verbose_name='是否已确认')
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='确认人')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'clauses_contract_clause'
        verbose_name = '合同条款'
        verbose_name_plural = '合同条款'
        ordering = ['start_position']

    def __str__(self):
        return f'{self.contract.title} - {self.get_clause_type_display()}'

