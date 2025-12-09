from django.contrib import admin
from .models import Contract, ContractVersion, Template, UserHabit


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_no', 'title', 'contract_type', 'status', 'drafter', 'created_at']
    list_filter = ['contract_type', 'status', 'created_at']
    search_fields = ['contract_no', 'title']
    date_hierarchy = 'created_at'


@admin.register(ContractVersion)
class ContractVersionAdmin(admin.ModelAdmin):
    list_display = ['contract', 'version', 'changed_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['contract__title']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'contract_type', 'industry', 'usage_count', 'is_public', 'created_at']
    list_filter = ['contract_type', 'industry', 'is_public', 'created_at']
    search_fields = ['name', 'description']


@admin.register(UserHabit)
class UserHabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'habit_type', 'habit_key', 'frequency', 'last_used_at']
    list_filter = ['habit_type', 'last_used_at']
    search_fields = ['user__username']

