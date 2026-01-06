from rest_framework import serializers
from apps.users.serializers import UserSerializer
from apps.contracts.serializers import ContractSerializer
from .models import ReviewTask, ReviewResult, ReviewOpinion, ReviewCycle, ReviewFocusConfig, AIModelConfig


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
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    reviewer_assignments_detail = serializers.SerializerMethodField()

    class Meta:
        model = ReviewTask
        fields = ['id', 'contract', 'contract_title', 'contract_version',
                  'status', 'priority', 'reviewer', 'reviewer_name', 'reviewer_level',
                  'review_levels', 'reviewer_assignments', 'reviewer_assignments_detail', 'celery_task_id', 
                  'progress', 'started_at', 'completed_at',
                  'error_message', 'created_by', 'created_by_name', 'result',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']

    def get_reviewer_assignments_detail(self, obj):
        """返回审核员分配的详细信息（包含审核员姓名等）"""
        try:
            # 检查字段是否存在（兼容迁移前的情况）
            if not hasattr(obj, 'reviewer_assignments') or not obj.reviewer_assignments:
                return {}
        except AttributeError:
            return {}
        
        from apps.users.models import User
        
        detail = {}
        try:
            # 确保reviewer_assignments是字典类型
            if isinstance(obj.reviewer_assignments, dict):
                for level, reviewer_id in obj.reviewer_assignments.items():
                    try:
                        # 确保reviewer_id是有效的整数
                        reviewer_id_int = int(reviewer_id) if reviewer_id else None
                        if reviewer_id_int:
                            reviewer = User.objects.get(id=reviewer_id_int)
                            detail[level] = {
                                'id': reviewer.id,
                                'username': reviewer.username,
                                'real_name': reviewer.real_name or reviewer.username,
                                'email': reviewer.email,
                            }
                        else:
                            detail[level] = {
                                'id': None,
                                'username': '未分配',
                                'real_name': '未分配',
                                'email': '',
                            }
                    except (User.DoesNotExist, ValueError, TypeError):
                        detail[level] = {
                            'id': reviewer_id,
                            'username': '未知用户',
                            'real_name': '未知用户',
                            'email': '',
                        }
        except (AttributeError, TypeError):
            # 如果reviewer_assignments不是字典或无法访问，返回空字典
            return {}
        
        return detail


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


class ReviewFocusConfigSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)

    class Meta:
        model = ReviewFocusConfig
        fields = ['id', 'level', 'level_name', 'focus_points', 'focus_description',
                  'review_standards', 'attention_items', 'is_active', 'created_by',
                  'created_by_name', 'updated_by', 'updated_by_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AIModelConfigSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    provider_display = serializers.SerializerMethodField()
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else ''
    
    def get_updated_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else ''
    
    def get_provider_display(self, obj):
        return obj.get_provider_display() if obj.provider else ''

    class Meta:
        model = AIModelConfig
        fields = ['id', 'name', 'provider', 'provider_display', 'api_key', 'api_base_url',
                  'available_models', 'default_model', 'is_active', 'is_default',
                  'description', 'temperature', 'max_tokens', 'timeout',
                  'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """验证默认模型是否在可用模型列表中"""
        available_models = data.get('available_models', [])
        default_model = data.get('default_model', '')
        
        if default_model and available_models:
            if default_model not in available_models:
                raise serializers.ValidationError({
                    'default_model': '默认模型必须在可用模型列表中'
                })
        
        return data

