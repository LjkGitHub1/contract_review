from django.contrib import admin
from .models import ReviewTask, ReviewResult, ReviewOpinion, ReviewCycle, ReviewFocusConfig, AIModelConfig


@admin.register(ReviewTask)
class ReviewTaskAdmin(admin.ModelAdmin):
    list_display = ['contract', 'task_type', 'status', 'created_by', 'created_at']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['contract__title']


@admin.register(ReviewResult)
class ReviewResultAdmin(admin.ModelAdmin):
    list_display = ['contract', 'overall_score', 'risk_level', 'risk_count', 'created_at']
    list_filter = ['risk_level', 'created_at']
    search_fields = ['contract__title']


@admin.register(ReviewOpinion)
class ReviewOpinionAdmin(admin.ModelAdmin):
    list_display = ['review_result', 'opinion_type', 'risk_level', 'status', 'created_at']
    list_filter = ['opinion_type', 'risk_level', 'status', 'created_at']
    search_fields = ['opinion_content']


@admin.register(ReviewCycle)
class ReviewCycleAdmin(admin.ModelAdmin):
    list_display = ['contract', 'cycle_no', 'status', 'submitted_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['contract__title']


@admin.register(ReviewFocusConfig)
class ReviewFocusConfigAdmin(admin.ModelAdmin):
    list_display = ['level', 'level_name', 'is_active', 'created_by', 'updated_at']
    list_filter = ['level', 'is_active', 'created_at']
    search_fields = ['level_name', 'focus_description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'default_model', 'is_active', 'is_default', 'created_at']
    list_filter = ['provider', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'provider', 'description')
        }),
        ('API配置', {
            'fields': ('api_key', 'api_base_url')
        }),
        ('模型配置', {
            'fields': ('available_models', 'default_model', 'temperature', 'max_tokens', 'timeout')
        }),
        ('状态', {
            'fields': ('is_active', 'is_default')
        }),
        ('其他', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

