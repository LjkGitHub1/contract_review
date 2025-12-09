from rest_framework import serializers
from .models import ComparisonTask, ComparisonDiff


class ComparisonDiffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparisonDiff
        fields = ['id', 'comparison_task', 'diff_type', 'diff_level', 'source_content',
                  'target_content', 'clause_id', 'risk_level', 'created_at']
        read_only_fields = ['created_at']


class ComparisonTaskSerializer(serializers.ModelSerializer):
    diffs = ComparisonDiffSerializer(many=True, read_only=True)
    source_contract_title = serializers.CharField(source='source_contract.title', read_only=True)
    target_contract_title = serializers.CharField(source='target_contract.title', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ComparisonTask
        fields = ['id', 'task_type', 'source_contract', 'source_contract_title',
                  'target_contract', 'target_contract_title', 'source_version',
                  'target_version', 'template', 'template_name', 'status', 'result_data',
                  'created_by', 'created_by_name', 'diffs', 'created_at', 'completed_at']
        read_only_fields = ['created_at', 'completed_at']

