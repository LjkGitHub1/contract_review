from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Department, Role, Permission, AuditLog, RolePermission, UserRole


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'parent', 'code', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    roles = serializers.SerializerMethodField()
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'real_name', 'phone', 'avatar', 
                  'department', 'department_name', 'role', 'reviewer_level', 'is_active', 
                  'password', 'roles', 'role_ids', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def get_roles(self, obj):
        """获取用户的角色列表"""
        try:
            user_roles = UserRole.objects.filter(user=obj).select_related('role')
            roles = [ur.role for ur in user_roles]
            # 使用简化的序列化，避免循环导入
            return [
                {
                    'id': role.id,
                    'name': role.name,
                    'code': role.code,
                    'description': role.description,
                }
                for role in roles
            ]
        except Exception as e:
            # 如果出错，返回空列表
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'获取用户角色失败: {str(e)}')
            return []

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        role_ids = validated_data.pop('role_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        
        # 更新用户角色
        if role_ids is not None:
            UserRole.objects.filter(user=instance).delete()
            for role_id in role_ids:
                try:
                    role = Role.objects.get(id=role_id)
                    UserRole.objects.get_or_create(user=instance, role=role)
                except Role.DoesNotExist:
                    pass
        
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'real_name', 'phone', 'department', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 'permission_ids', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_permissions(self, obj):
        """获取角色的权限列表"""
        permissions = obj.permissions.all()
        return PermissionSerializer(permissions, many=True).data

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新角色权限
        if permission_ids is not None:
            instance.permissions.clear()
            for perm_id in permission_ids:
                try:
                    permission = Permission.objects.get(id=perm_id)
                    RolePermission.objects.get_or_create(role=instance, permission=permission)
                except Permission.DoesNotExist:
                    pass
        
        return instance

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        # 添加权限
        for perm_id in permission_ids:
            try:
                permission = Permission.objects.get(id=perm_id)
                RolePermission.objects.get_or_create(role=role, permission=permission)
            except Permission.DoesNotExist:
                pass
        
        return role


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'resource', 'action', 'description', 
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action', 'resource_type', 'resource_id',
                  'ip_address', 'user_agent', 'request_data', 'response_data', 
                  'status', 'error_message', 'created_at']
        read_only_fields = ['created_at']
    
    def get_user_name(self, obj):
        """安全地获取用户名，处理 user 为 None 的情况"""
        return obj.user.username if obj.user else '-'

