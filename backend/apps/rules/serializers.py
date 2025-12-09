from rest_framework import serializers
from .models import ReviewRule, RuleMatch


class ReviewRuleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ReviewRule
        fields = ['id', 'rule_code', 'rule_name', 'rule_type', 'industry', 'category',
                  'priority', 'rule_content', 'risk_level', 'legal_basis', 'description',
                  'is_active', 'version', 'created_by', 'created_by_name',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class RuleMatchSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.rule_name', read_only=True)

    class Meta:
        model = RuleMatch
        fields = ['id', 'review_task', 'rule', 'rule_name', 'contract_id',
                  'matched_clause', 'match_score', 'match_result', 'created_at']
        read_only_fields = ['created_at']

