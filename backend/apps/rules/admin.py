from django.contrib import admin
from .models import ReviewRule, RuleMatch


@admin.register(ReviewRule)
class ReviewRuleAdmin(admin.ModelAdmin):
    list_display = ['rule_code', 'rule_name', 'rule_type', 'industry', 'risk_level', 'is_active', 'created_at']
    list_filter = ['rule_type', 'industry', 'risk_level', 'is_active', 'created_at']
    search_fields = ['rule_code', 'rule_name']


@admin.register(RuleMatch)
class RuleMatchAdmin(admin.ModelAdmin):
    list_display = ['rule', 'contract_id', 'match_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['rule__rule_name']

