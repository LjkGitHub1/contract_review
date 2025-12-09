from django.db import models
from apps.users.models import User
from apps.contracts.models import Contract


class Recommendation(models.Model):
    """推荐记录表"""
    RECOMMENDATION_TYPE_CHOICES = [
        ('clause', '条款推荐'),
        ('template', '模板推荐'),
        ('risk_response', '风险应对建议'),
    ]
    
    CONTEXT_CHOICES = [
        ('drafting', '起草中'),
        ('modifying', '修改中'),
        ('reviewing', '审核中'),
        ('negotiating', '谈判中'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations', verbose_name='用户')
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=True, related_name='recommendations', verbose_name='合同')
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPE_CHOICES, verbose_name='推荐类型')
    recommendation_context = models.CharField(max_length=50, choices=CONTEXT_CHOICES, blank=True, verbose_name='推荐场景')
    item_type = models.CharField(max_length=50, blank=True, verbose_name='推荐项类型')
    item_id = models.BigIntegerField(null=True, blank=True, verbose_name='推荐项ID')
    item_content = models.TextField(blank=True, verbose_name='推荐项内容')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='推荐分数')
    reason = models.TextField(blank=True, verbose_name='推荐理由')
    is_accepted = models.BooleanField(null=True, blank=True, verbose_name='是否被接受')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'recommendations_recommendation'
        verbose_name = '推荐记录'
        verbose_name_plural = '推荐记录'
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.get_recommendation_type_display()}'

