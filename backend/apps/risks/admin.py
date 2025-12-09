from django.contrib import admin
from .models import RiskIdentification


@admin.register(RiskIdentification)
class RiskIdentificationAdmin(admin.ModelAdmin):
    list_display = ['contract_id', 'risk_type', 'risk_category', 'risk_level', 'status', 'created_at']
    list_filter = ['risk_type', 'risk_category', 'risk_level', 'status', 'created_at']
    search_fields = ['risk_description']

