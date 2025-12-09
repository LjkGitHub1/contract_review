from django.contrib import admin
from .models import ComparisonTask, ComparisonDiff


@admin.register(ComparisonTask)
class ComparisonTaskAdmin(admin.ModelAdmin):
    list_display = ['task_type', 'status', 'created_by', 'created_at']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['source_contract__title', 'target_contract__title']


@admin.register(ComparisonDiff)
class ComparisonDiffAdmin(admin.ModelAdmin):
    list_display = ['comparison_task', 'diff_type', 'diff_level', 'risk_level', 'created_at']
    list_filter = ['diff_type', 'diff_level', 'risk_level', 'created_at']
    search_fields = ['source_content', 'target_content']

