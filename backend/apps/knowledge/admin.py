from django.contrib import admin
from .models import KnowledgeEntity, KnowledgeRelation, Regulation, Case


@admin.register(KnowledgeEntity)
class KnowledgeEntityAdmin(admin.ModelAdmin):
    list_display = ['entity_name', 'entity_type', 'entity_code', 'created_at']
    list_filter = ['entity_type', 'created_at']
    search_fields = ['entity_name', 'entity_code']


@admin.register(KnowledgeRelation)
class KnowledgeRelationAdmin(admin.ModelAdmin):
    list_display = ['source_entity', 'relation_type', 'target_entity', 'confidence', 'created_at']
    list_filter = ['relation_type', 'created_at']
    search_fields = ['source_entity__entity_name', 'target_entity__entity_name']


@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    list_display = ['title', 'regulation_no', 'regulation_type', 'publish_date', 'is_active', 'created_at']
    list_filter = ['regulation_type', 'is_active', 'publish_date', 'created_at']
    search_fields = ['title', 'regulation_no']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['case_title', 'case_no', 'case_type', 'court', 'judge_date', 'created_at']
    list_filter = ['case_type', 'judge_date', 'created_at']
    search_fields = ['case_title', 'case_no']

