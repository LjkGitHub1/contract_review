from rest_framework import serializers
from apps.users.serializers import UserSerializer
from .models import Contract, ContractVersion, Template, UserHabit


class ContractVersionSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = ContractVersion
        fields = ['id', 'contract', 'version', 'content', 'file_path', 
                  'change_summary', 'changed_by', 'changed_by_name', 'created_at']
        read_only_fields = ['created_at']


class ContractSerializer(serializers.ModelSerializer):
    drafter_name = serializers.CharField(source='drafter.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    versions = ContractVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = ['id', 'contract_no', 'title', 'contract_type', 'industry', 
                  'status', 'content', 'file_path', 'file_format', 'template', 
                  'template_name', 'drafter', 'drafter_name', 'current_version',
                  'versions', 'created_at', 'updated_at']
        read_only_fields = ['contract_no', 'created_at', 'updated_at', 'current_version', 'drafter']


class TemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Template
        fields = ['id', 'name', 'contract_type', 'industry', 'category', 
                  'content', 'description', 'tags', 'usage_count', 'is_public',
                  'is_enterprise', 'created_by', 'created_by_name', 
                  'enterprise_id', 'created_at', 'updated_at']
        read_only_fields = ['usage_count', 'created_at', 'updated_at']


class UserHabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHabit
        fields = ['id', 'user', 'habit_type', 'habit_key', 'habit_value',
                  'frequency', 'last_used_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

