from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommendation_type', 'recommendation_context', 'score', 'is_accepted', 'created_at']
    list_filter = ['recommendation_type', 'recommendation_context', 'is_accepted', 'created_at']
    search_fields = ['user__username', 'item_content']

