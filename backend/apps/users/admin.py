from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department, Role, Permission, AuditLog


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'real_name', 'role', 'department', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'department', 'created_at']
    search_fields = ['username', 'email', 'real_name']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('real_name', 'phone', 'avatar', 'department', 'role')}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'resource', 'action', 'created_at']
    list_filter = ['resource', 'action']
    search_fields = ['name', 'code']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'status', 'created_at']
    list_filter = ['action', 'status', 'created_at']
    search_fields = ['user__username', 'action']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

