from django.db import models
from apps.users.models import User
from apps.reviews.models import ReviewTask


class ReviewRule(models.Model):
    """审核规则表"""
    RULE_TYPE_CHOICES = [
        ('general', '通用规则'),
        ('industry', '行业规则'),
        ('enterprise', '企业规则'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('high', '高风险'),
        ('medium', '中风险'),
        ('low', '低风险'),
    ]
    
    rule_code = models.CharField(max_length=100, unique=True, verbose_name='规则编码')
    rule_name = models.CharField(max_length=200, verbose_name='规则名称')
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES, verbose_name='规则类型')
    industry = models.CharField(max_length=50, blank=True, verbose_name='适用行业')
    category = models.CharField(max_length=50, blank=True, verbose_name='规则分类')
    priority = models.IntegerField(default=0, verbose_name='优先级')
    rule_content = models.JSONField(verbose_name='规则内容')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, blank=True, verbose_name='风险等级')
    legal_basis = models.TextField(blank=True, verbose_name='法律依据')
    description = models.TextField(blank=True, verbose_name='规则描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    version = models.IntegerField(default=1, verbose_name='规则版本')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'rules_review_rule'
        verbose_name = '审核规则'
        verbose_name_plural = '审核规则'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.rule_name


class RuleMatch(models.Model):
    """规则匹配记录表"""
    review_task = models.ForeignKey(ReviewTask, on_delete=models.CASCADE, related_name='rule_matches', verbose_name='审核任务')
    rule = models.ForeignKey(ReviewRule, on_delete=models.CASCADE, verbose_name='规则')
    contract_id = models.BigIntegerField(verbose_name='合同ID')
    matched_clause = models.TextField(blank=True, verbose_name='匹配的条款')
    match_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='匹配分数')
    match_result = models.JSONField(null=True, blank=True, verbose_name='匹配结果')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'rules_rule_match'
        verbose_name = '规则匹配'
        verbose_name_plural = '规则匹配'
        ordering = ['-match_score']

    def __str__(self):
        return f'{self.rule.rule_name} - 匹配记录'

