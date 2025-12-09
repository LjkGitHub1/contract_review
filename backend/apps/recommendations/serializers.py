from rest_framework import serializers
from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    contract_title = serializers.CharField(source='contract.title', read_only=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'user_name', 'contract', 'contract_title',
                  'recommendation_type', 'recommendation_context', 'item_type',
                  'item_id', 'item_content', 'score', 'reason', 'is_accepted',
                  'created_at']
        read_only_fields = ['created_at']

