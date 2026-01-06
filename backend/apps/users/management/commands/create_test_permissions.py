from django.core.management.base import BaseCommand
from apps.users.models import Permission, Role, RolePermission, User, UserRole


class Command(BaseCommand):
    help = '创建权限测试数据（权限、角色、角色权限关联、用户角色关联）'

    def handle(self, *args, **options):
        self.stdout.write('开始创建权限测试数据...')

        # 1. 创建权限
        self.stdout.write('\n1. 创建权限...')
        permissions_data = [
            # 合同管理权限
            {'name': '查看合同', 'code': 'contract:view', 'resource': 'contract', 'action': 'view', 'description': '查看合同列表和详情'},
            {'name': '创建合同', 'code': 'contract:create', 'resource': 'contract', 'action': 'create', 'description': '创建新合同'},
            {'name': '编辑合同', 'code': 'contract:edit', 'resource': 'contract', 'action': 'edit', 'description': '编辑合同信息'},
            {'name': '删除合同', 'code': 'contract:delete', 'resource': 'contract', 'action': 'delete', 'description': '删除合同'},
            {'name': '导出合同', 'code': 'contract:export', 'resource': 'contract', 'action': 'export', 'description': '导出合同数据'},
            
            # 审核管理权限
            {'name': '查看审核任务', 'code': 'review:view', 'resource': 'review', 'action': 'view', 'description': '查看审核任务列表和详情'},
            {'name': '创建审核任务', 'code': 'review:create', 'resource': 'review', 'action': 'create', 'description': '创建新的审核任务'},
            {'name': '执行审核', 'code': 'review:execute', 'resource': 'review', 'action': 'execute', 'description': '执行审核任务'},
            {'name': '提交审核意见', 'code': 'review:submit', 'resource': 'review', 'action': 'submit', 'description': '提交审核意见'},
            {'name': '审核通过', 'code': 'review:approve', 'resource': 'review', 'action': 'approve', 'description': '审核通过'},
            {'name': '审核驳回', 'code': 'review:reject', 'resource': 'review', 'action': 'reject', 'description': '审核驳回'},
            
            # 用户管理权限
            {'name': '查看用户', 'code': 'user:view', 'resource': 'user', 'action': 'view', 'description': '查看用户列表和详情'},
            {'name': '创建用户', 'code': 'user:create', 'resource': 'user', 'action': 'create', 'description': '创建新用户'},
            {'name': '编辑用户', 'code': 'user:edit', 'resource': 'user', 'action': 'edit', 'description': '编辑用户信息'},
            {'name': '删除用户', 'code': 'user:delete', 'resource': 'user', 'action': 'delete', 'description': '删除用户'},
            {'name': '分配角色', 'code': 'user:assign_role', 'resource': 'user', 'action': 'assign_role', 'description': '为用户分配角色'},
            
            # 部门管理权限
            {'name': '查看部门', 'code': 'department:view', 'resource': 'department', 'action': 'view', 'description': '查看部门列表和详情'},
            {'name': '创建部门', 'code': 'department:create', 'resource': 'department', 'action': 'create', 'description': '创建新部门'},
            {'name': '编辑部门', 'code': 'department:edit', 'resource': 'department', 'action': 'edit', 'description': '编辑部门信息'},
            {'name': '删除部门', 'code': 'department:delete', 'resource': 'department', 'action': 'delete', 'description': '删除部门'},
            
            # 角色管理权限
            {'name': '查看角色', 'code': 'role:view', 'resource': 'role', 'action': 'view', 'description': '查看角色列表和详情'},
            {'name': '创建角色', 'code': 'role:create', 'resource': 'role', 'action': 'create', 'description': '创建新角色'},
            {'name': '编辑角色', 'code': 'role:edit', 'resource': 'role', 'action': 'edit', 'description': '编辑角色信息'},
            {'name': '删除角色', 'code': 'role:delete', 'resource': 'role', 'action': 'delete', 'description': '删除角色'},
            {'name': '分配权限', 'code': 'role:assign_permission', 'resource': 'role', 'action': 'assign_permission', 'description': '为角色分配权限'},
            
            # 权限管理权限
            {'name': '查看权限', 'code': 'permission:view', 'resource': 'permission', 'action': 'view', 'description': '查看权限列表和详情'},
            {'name': '创建权限', 'code': 'permission:create', 'resource': 'permission', 'action': 'create', 'description': '创建新权限'},
            {'name': '编辑权限', 'code': 'permission:edit', 'resource': 'permission', 'action': 'edit', 'description': '编辑权限信息'},
            {'name': '删除权限', 'code': 'permission:delete', 'resource': 'permission', 'action': 'delete', 'description': '删除权限'},
            
            # 规则管理权限
            {'name': '查看规则', 'code': 'rule:view', 'resource': 'rule', 'action': 'view', 'description': '查看规则列表和详情'},
            {'name': '创建规则', 'code': 'rule:create', 'resource': 'rule', 'action': 'create', 'description': '创建新规则'},
            {'name': '编辑规则', 'code': 'rule:edit', 'resource': 'rule', 'action': 'edit', 'description': '编辑规则信息'},
            {'name': '删除规则', 'code': 'rule:delete', 'resource': 'rule', 'action': 'delete', 'description': '删除规则'},
            
            # 模板管理权限
            {'name': '查看模板', 'code': 'template:view', 'resource': 'template', 'action': 'view', 'description': '查看模板列表和详情'},
            {'name': '创建模板', 'code': 'template:create', 'resource': 'template', 'action': 'create', 'description': '创建新模板'},
            {'name': '编辑模板', 'code': 'template:edit', 'resource': 'template', 'action': 'edit', 'description': '编辑模板信息'},
            {'name': '删除模板', 'code': 'template:delete', 'resource': 'template', 'action': 'delete', 'description': '删除模板'},
            
            # 系统配置权限
            {'name': '查看系统配置', 'code': 'config:view', 'resource': 'config', 'action': 'view', 'description': '查看系统配置'},
            {'name': '编辑系统配置', 'code': 'config:edit', 'resource': 'config', 'action': 'edit', 'description': '编辑系统配置'},
            {'name': '查看操作日志', 'code': 'audit_log:view', 'resource': 'audit_log', 'action': 'view', 'description': '查看操作日志'},
        ]

        created_permissions = {}
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                code=perm_data['code'],
                defaults={
                    'name': perm_data['name'],
                    'resource': perm_data['resource'],
                    'action': perm_data['action'],
                    'description': perm_data['description'],
                }
            )
            created_permissions[perm_data['code']] = permission
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ 创建权限: {permission.name} ({permission.code})'))
            else:
                self.stdout.write(f'  - 权限已存在: {permission.name} ({permission.code})')

        # 2. 创建角色
        self.stdout.write('\n2. 创建角色...')
        roles_data = [
            {
                'name': '超级管理员',
                'code': 'super_admin',
                'description': '拥有所有权限的超级管理员角色',
                'permissions': [code for code in created_permissions.keys()],  # 所有权限
            },
            {
                'name': '合同管理员',
                'code': 'contract_admin',
                'description': '负责合同管理的角色',
                'permissions': [
                    'contract:view', 'contract:create', 'contract:edit', 'contract:delete', 'contract:export',
                    'template:view', 'template:create', 'template:edit', 'template:delete',
                ],
            },
            {
                'name': '高级审核员',
                'code': 'senior_reviewer',
                'description': '高级审核员，可以执行所有审核操作',
                'permissions': [
                    'review:view', 'review:create', 'review:execute', 'review:submit',
                    'review:approve', 'review:reject',
                    'contract:view',
                ],
            },
            {
                'name': '普通审核员',
                'code': 'reviewer',
                'description': '普通审核员，可以查看和执行审核',
                'permissions': [
                    'review:view', 'review:execute', 'review:submit',
                    'contract:view',
                ],
            },
            {
                'name': '合同起草人',
                'code': 'drafter',
                'description': '合同起草人，可以创建和编辑合同',
                'permissions': [
                    'contract:view', 'contract:create', 'contract:edit',
                    'template:view',
                    'review:view',
                ],
            },
            {
                'name': '只读用户',
                'code': 'readonly',
                'description': '只读用户，只能查看数据',
                'permissions': [
                    'contract:view',
                    'review:view',
                    'template:view',
                    'rule:view',
                ],
            },
        ]

        created_roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                code=role_data['code'],
                defaults={
                    'name': role_data['name'],
                    'description': role_data['description'],
                }
            )
            created_roles[role_data['code']] = role
            
            # 分配权限
            permission_codes = role_data.get('permissions', [])
            for perm_code in permission_codes:
                if perm_code in created_permissions:
                    RolePermission.objects.get_or_create(
                        role=role,
                        permission=created_permissions[perm_code]
                    )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ 创建角色: {role.name} ({role.code})，分配了 {len(permission_codes)} 个权限'))
            else:
                # 更新权限
                RolePermission.objects.filter(role=role).delete()
                for perm_code in permission_codes:
                    if perm_code in created_permissions:
                        RolePermission.objects.get_or_create(
                            role=role,
                            permission=created_permissions[perm_code]
                        )
                self.stdout.write(f'  - 更新角色: {role.name} ({role.code})，分配了 {len(permission_codes)} 个权限')

        # 3. 为用户分配角色（可选）
        self.stdout.write('\n3. 为用户分配角色...')
        try:
            # 为管理员用户分配超级管理员角色
            admin_users = User.objects.filter(role='admin', is_deleted=False)
            if admin_users.exists():
                super_admin_role = created_roles.get('super_admin')
                if super_admin_role:
                    for admin_user in admin_users:
                        UserRole.objects.get_or_create(
                            user=admin_user,
                            role=super_admin_role
                        )
                        self.stdout.write(self.style.SUCCESS(f'  ✓ 为用户 {admin_user.username} 分配角色: {super_admin_role.name}'))
            
            # 为审核员用户分配审核员角色
            reviewer_users = User.objects.filter(role='reviewer', is_deleted=False)
            if reviewer_users.exists():
                reviewer_role = created_roles.get('reviewer')
                if reviewer_role:
                    for reviewer_user in reviewer_users[:5]:  # 只分配前5个
                        UserRole.objects.get_or_create(
                            user=reviewer_user,
                            role=reviewer_role
                        )
                        self.stdout.write(self.style.SUCCESS(f'  ✓ 为用户 {reviewer_user.username} 分配角色: {reviewer_role.name}'))
            
            # 为起草人用户分配起草人角色
            drafter_users = User.objects.filter(role='drafter', is_deleted=False)
            if drafter_users.exists():
                drafter_role = created_roles.get('drafter')
                if drafter_role:
                    for drafter_user in drafter_users[:5]:  # 只分配前5个
                        UserRole.objects.get_or_create(
                            user=drafter_user,
                            role=drafter_role
                        )
                        self.stdout.write(self.style.SUCCESS(f'  ✓ 为用户 {drafter_user.username} 分配角色: {drafter_role.name}'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  警告: 分配用户角色时出错: {str(e)}'))

        # 统计信息
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('权限测试数据创建完成！'))
        self.stdout.write('='*50)
        self.stdout.write(f'权限总数: {Permission.objects.filter(is_deleted=False).count()}')
        self.stdout.write(f'角色总数: {Role.objects.filter(is_deleted=False).count()}')
        self.stdout.write(f'角色权限关联总数: {RolePermission.objects.count()}')
        self.stdout.write(f'用户角色关联总数: {UserRole.objects.count()}')
        self.stdout.write('='*50)

