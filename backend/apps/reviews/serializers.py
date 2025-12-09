from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.contracts.serializers import ContractSerializer
from .models import ReviewTask, ReviewResult, ReviewOpinion, ReviewCycle


class ReviewOpinionSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = ReviewOpinion
        fields = ['id', 'review_result', 'reviewer', 'reviewer_name', 'clause_id',
                  'clause_content', 'opinion_type', 'risk_level', 'opinion_content',
                  'legal_basis', 'suggestion', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ReviewResultSerializer(serializers.ModelSerializer):
    opinions = ReviewOpinionSerializer(many=True, read_only=True)
    contract_title = serializers.CharField(source='contract.title', read_only=True)

    class Meta:
        model = ReviewResult
        fields = ['id', 'review_task', 'contract', 'contract_title', 'overall_score',
                  'risk_level', 'risk_count', 'summary', 'report_path', 'report_format',
                  'review_data', 'opinions', 'created_at']
        read_only_fields = ['created_at']


class ReviewTaskSerializer(serializers.ModelSerializer):
    result = ReviewResultSerializer(read_only=True)
    contract_title = serializers.CharField(source='contract.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ReviewTask
        fields = ['id', 'contract', 'contract_title', 'contract_version', 'task_type',
                  'status', 'priority', 'celery_task_id', 'started_at', 'completed_at',
                  'error_message', 'created_by', 'created_by_name', 'result',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']


class ReviewCycleSerializer(serializers.ModelSerializer):
    contract_title = serializers.CharField(source='contract.title', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.username', read_only=True)
    modified_by_name = serializers.CharField(source='modified_by.username', read_only=True)

    class Meta:
        model = ReviewCycle
        fields = ['id', 'contract', 'contract_title', 'cycle_no', 'review_result',
                  'opinion_summary', 'modification_summary', 'status', 'submitted_by',
                  'submitted_by_name', 'submitted_at', 'modified_by', 'modified_by_name',
                  'modified_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

