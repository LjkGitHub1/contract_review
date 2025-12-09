from rest_framework import serializers
from .models import KnowledgeEntity, KnowledgeRelation, Regulation, Case


class KnowledgeEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeEntity
        fields = ['id', 'entity_type', 'entity_name', 'entity_code', 'description',
                  'properties', 'source', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class KnowledgeRelationSerializer(serializers.ModelSerializer):
    source_entity_name = serializers.CharField(source='source_entity.entity_name', read_only=True)
    target_entity_name = serializers.CharField(source='target_entity.entity_name', read_only=True)
    source_entity_id = serializers.IntegerField(source='source_entity.id', read_only=True)
    target_entity_id = serializers.IntegerField(source='target_entity.id', read_only=True)

    class Meta:
        model = KnowledgeRelation
        fields = ['id', 'source_entity', 'source_entity_id', 'source_entity_name', 
                  'target_entity', 'target_entity_id', 'target_entity_name', 
                  'relation_type', 'relation_properties', 'confidence', 
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class RegulationSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.entity_name', read_only=True)

    class Meta:
        model = Regulation
        fields = ['id', 'title', 'regulation_no', 'regulation_type', 'publish_date',
                  'effective_date', 'expiry_date', 'content', 'source_url', 'entity',
                  'entity_name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CaseSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.entity_name', read_only=True)

    class Meta:
        model = Case
        fields = ['id', 'case_no', 'case_title', 'case_type', 'court', 'judge_date',
                  'case_summary', 'case_content', 'related_clauses', 'entity',
                  'entity_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

