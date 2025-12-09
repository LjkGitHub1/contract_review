from django.contrib import admin
from .models import ReviewTask, ReviewResult, ReviewOpinion, ReviewCycle


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

