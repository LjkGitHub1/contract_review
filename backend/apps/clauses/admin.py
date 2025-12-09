from django.contrib import admin
from .models import ContractClause


@admin.register(ContractClause)
class ContractClauseAdmin(admin.ModelAdmin):
    list_display = ['contract', 'clause_type', 'clause_title', 'is_confirmed', 'confidence', 'created_at']
    list_filter = ['clause_type', 'is_confirmed', 'created_at']
    search_fields = ['contract__title', 'clause_content']

