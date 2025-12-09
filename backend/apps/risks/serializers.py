from rest_framework import serializers
from .models import RiskIdentification


class RiskIdentificationSerializer(serializers.ModelSerializer):
    handled_by_name = serializers.CharField(source='handled_by.username', read_only=True)
    clause_content = serializers.CharField(source='clause.clause_content', read_only=True)

    class Meta:
        model = RiskIdentification
        fields = ['id', 'review_result', 'contract_id', 'clause', 'clause_content',
                  'risk_type', 'risk_category', 'risk_level', 'risk_description',
                  'risk_location', 'legal_basis', 'suggestion', 'status',
                  'handled_by', 'handled_by_name', 'handled_at', 'created_at']
        read_only_fields = ['created_at']

