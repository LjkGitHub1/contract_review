from rest_framework import serializers
from .models import ContractClause


class ContractClauseSerializer(serializers.ModelSerializer):
    contract_title = serializers.CharField(source='contract.title', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.username', read_only=True)

    class Meta:
        model = ContractClause
        fields = ['id', 'contract', 'contract_title', 'contract_version', 'clause_no',
                  'clause_type', 'clause_title', 'clause_content', 'start_position',
                  'end_position', 'extracted_data', 'confidence', 'is_confirmed',
                  'confirmed_by', 'confirmed_by_name', 'confirmed_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

