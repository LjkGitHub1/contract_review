<template>
  <div class="permission-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门和人员权限配置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 部门管理 -->
        <el-tab-pane label="部门管理" name="departments">
          <div class="tab-content">
            <div class="toolbar">
              <el-button
                type="danger"
                :disabled="selectedDepartments.length === 0"
                @click="handleBatchDeleteDepartments"
              >
                批量删除 ({{ selectedDepartments.length }})
              </el-button>
              <el-button type="primary" @click="handleCreateDepartment">
                <el-icon><Plus /></el-icon>
                新建部门
              </el-button>
            </div>
            <el-table
              :data="departments"
              v-loading="departmentsLoading"
              style="width: 100%"
              @selection-change="handleDepartmentSelectionChange"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="code" label="部门编码" width="150" />
              <el-table-column prop="name" label="部门名称" />
              <el-table-column prop="parent_name" label="父部门" width="150">
                <template #default="{ row }">
                  {{ row.parent_name || '无' }}
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="handleEditDepartment(row)">编辑</el-button>
                  <el-button link type="danger" @click="handleDeleteDepartment(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 用户管理 -->
        <el-tab-pane label="用户管理" name="users">
          <div class="tab-content">
            <div class="toolbar">
              <el-form :inline="true" :model="userSearchForm" class="search-form">
                <el-form-item label="用户名">
                  <el-input v-model="userSearchForm.username" placeholder="请输入用户名" clearable />
                </el-form-item>
                <el-form-item label="部门">
                  <el-select v-model="userSearchForm.department" placeholder="请选择部门" clearable style="width: 200px">
                    <el-option
                      v-for="dept in allDepartments"
                      :key="dept.id"
                      :label="dept.name"
                      :value="dept.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSearchUsers">搜索</el-button>
                  <el-button @click="handleResetUserSearch">重置</el-button>
                </el-form-item>
              </el-form>
              <el-button
                type="danger"
                :disabled="selectedUsers.length === 0"
                @click="handleBatchDeleteUsers"
              >
                批量删除 ({{ selectedUsers.length }})
              </el-button>
              <el-button type="primary" @click="handleCreateUser">
                <el-icon><Plus /></el-icon>
                新建用户
              </el-button>
            </div>
            <el-table
              :data="users"
              v-loading="usersLoading"
              style="width: 100%"
              @selection-change="handleUserSelectionChange"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="username" label="用户名" />
              <el-table-column prop="real_name" label="真实姓名" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="department_name" label="部门" />
              <el-table-column prop="role" label="角色" width="100">
                <template #default="{ row }">
                  <el-tag>{{ getRoleText(row.role) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="自定义角色" width="150">
                <template #default="{ row }">
                  <el-tag v-for="role in row.roles" :key="role.id" style="margin-right: 5px">
                    {{ role.name }}
                  </el-tag>
                  <span v-if="!row.roles || row.roles.length === 0">-</span>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'">
                    {{ row.is_active ? '激活' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="250" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="handleEditUser(row)">编辑</el-button>
                  <el-button link type="primary" @click="handleAssignRoles(row)">分配角色</el-button>
                  <el-button link type="danger" @click="handleDeleteUser(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="userPagination.page"
              v-model:page-size="userPagination.pageSize"
              :total="userPagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleUserSizeChange"
              @current-change="handleUserPageChange"
              style="margin-top: 20px; justify-content: flex-end"
            />
          </div>
        </el-tab-pane>

        <!-- 角色管理 -->
        <el-tab-pane label="角色管理" name="roles">
          <div class="tab-content">
            <div class="toolbar">
              <el-button
                type="danger"
                :disabled="selectedRoles.length === 0"
                @click="handleBatchDeleteRoles"
              >
                批量删除 ({{ selectedRoles.length }})
              </el-button>
              <el-button type="primary" @click="handleCreateRole">
                <el-icon><Plus /></el-icon>
                新建角色
              </el-button>
            </div>
            <el-table
              :data="roles"
              v-loading="rolesLoading"
              style="width: 100%"
              @selection-change="handleRoleSelectionChange"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="code" label="角色编码" width="150" />
              <el-table-column prop="name" label="角色名称" />
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column label="权限数量" width="120">
                <template #default="{ row }">
                  <el-tag>{{ row.permissions ? row.permissions.length : 0 }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="250" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="handleEditRole(row)">编辑</el-button>
                  <el-button link type="primary" @click="handleAssignPermissions(row)">分配权限</el-button>
                  <el-button link type="danger" @click="handleDeleteRole(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 权限管理 -->
        <el-tab-pane label="权限管理" name="permissions">
          <div class="tab-content">
            <div class="toolbar">
              <el-button
                type="danger"
                :disabled="selectedPermissions.length === 0"
                @click="handleBatchDeletePermissions"
              >
                批量删除 ({{ selectedPermissions.length }})
              </el-button>
              <el-button type="primary" @click="handleCreatePermission">
                <el-icon><Plus /></el-icon>
                新建权限
              </el-button>
            </div>
            <el-table
              :data="permissions"
              v-loading="permissionsLoading"
              style="width: 100%"
              @selection-change="handlePermissionSelectionChange"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="code" label="权限编码" width="200" />
              <el-table-column prop="name" label="权限名称" />
              <el-table-column prop="resource" label="资源类型" width="150" />
              <el-table-column prop="action" label="操作类型" width="150" />
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="handleEditPermission(row)">编辑</el-button>
                  <el-button link type="danger" @click="handleDeletePermission(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 部门对话框 -->
    <el-dialog
      v-model="departmentDialogVisible"
      :title="departmentDialogTitle"
      width="600px"
      @close="handleDepartmentDialogClose"
    >
      <el-form
        ref="departmentFormRef"
        :model="departmentFormData"
        :rules="departmentFormRules"
        label-width="120px"
      >
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="departmentFormData.name" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="departmentFormData.code" placeholder="可选，如不填写将自动生成" />
        </el-form-item>
        <el-form-item label="父部门" prop="parent">
          <el-select
            v-model="departmentFormData.parent"
            placeholder="请选择父部门（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="dept in parentDepartments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
              :disabled="dept.id === departmentFormData.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="部门描述" prop="description">
          <el-input v-model="departmentFormData.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="departmentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitDepartment" :loading="departmentSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 用户对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="userDialogTitle"
      width="600px"
      @close="handleUserDialogClose"
    >
      <el-form
        ref="userFormRef"
        :model="userFormData"
        :rules="userFormRules"
        label-width="120px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userFormData.username" :disabled="isEditUser" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userFormData.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEditUser">
          <el-input v-model="userFormData.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="userFormData.real_name" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userFormData.phone" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-select v-model="userFormData.department" placeholder="请选择部门" clearable style="width: 100%">
            <el-option
              v-for="dept in allDepartments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userFormData.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="审核员" value="reviewer" />
            <el-option label="起草人" value="drafter" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核员层级" prop="reviewer_level" v-if="userFormData.role === 'reviewer'">
          <el-select v-model="userFormData.reviewer_level" placeholder="请选择审核员层级" style="width: 100%">
            <el-option label="一级审核员" value="level1" />
            <el-option label="二级审核员" value="level2" />
            <el-option label="三级审核员（高级）" value="level3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="userFormData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitUser" :loading="userSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配角色对话框 -->
    <el-dialog
      v-model="assignRolesDialogVisible"
      title="分配角色"
      width="500px"
    >
      <el-checkbox-group v-model="selectedRoleIds">
        <el-checkbox
          v-for="role in allRoles"
          :key="role.id"
          :label="role.id"
        >
          {{ role.name }} ({{ role.code }})
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="assignRolesDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitAssignRoles" :loading="assignRolesSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 角色对话框 -->
    <el-dialog
      v-model="roleDialogVisible"
      :title="roleDialogTitle"
      width="600px"
      @close="handleRoleDialogClose"
    >
      <el-form
        ref="roleFormRef"
        :model="roleFormData"
        :rules="roleFormRules"
        label-width="120px"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleFormData.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="roleFormData.code" />
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input v-model="roleFormData.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitRole" :loading="roleSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配权限对话框 -->
    <el-dialog
      v-model="assignPermissionsDialogVisible"
      title="分配权限"
      width="600px"
    >
      <el-checkbox-group v-model="selectedPermissionIds">
        <el-checkbox
          v-for="permission in allPermissions"
          :key="permission.id"
          :label="permission.id"
        >
          {{ permission.name }} ({{ permission.code }})
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="assignPermissionsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitAssignPermissions" :loading="assignPermissionsSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 权限对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      :title="permissionDialogTitle"
      width="600px"
      @close="handlePermissionDialogClose"
    >
      <el-form
        ref="permissionFormRef"
        :model="permissionFormData"
        :rules="permissionFormRules"
        label-width="120px"
      >
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="permissionFormData.name" />
        </el-form-item>
        <el-form-item label="权限编码" prop="code">
          <el-input v-model="permissionFormData.code" />
        </el-form-item>
        <el-form-item label="资源类型" prop="resource">
          <el-input v-model="permissionFormData.resource" />
        </el-form-item>
        <el-form-item label="操作类型" prop="action">
          <el-input v-model="permissionFormData.action" />
        </el-form-item>
        <el-form-item label="权限描述" prop="description">
          <el-input v-model="permissionFormData.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitPermission" :loading="permissionSubmitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const activeTab = ref('departments')

// 部门相关
const departments = ref([])
const departmentsLoading = ref(false)
const departmentDialogVisible = ref(false)
const isEditDepartment = ref(false)
const departmentFormRef = ref(null)
const departmentSubmitting = ref(false)
const allDepartments = ref([])
const selectedDepartments = ref([])

const departmentFormData = reactive({
  id: null,
  name: '',
  code: '',
  parent: null,
  description: '',
})

const departmentFormRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
}

const departmentDialogTitle = computed(() => (isEditDepartment.value ? '编辑部门' : '新建部门'))
const parentDepartments = computed(() => {
  if (isEditDepartment.value && departmentFormData.id) {
    return allDepartments.value.filter(dept => dept.id !== departmentFormData.id)
  }
  return allDepartments.value
})

// 用户相关
const users = ref([])
const usersLoading = ref(false)
const userDialogVisible = ref(false)
const isEditUser = ref(false)
const userFormRef = ref(null)
const userSubmitting = ref(false)
const assignRolesDialogVisible = ref(false)
const assignRolesSubmitting = ref(false)
const currentAssignUser = ref(null)
const selectedRoleIds = ref([])
const allRoles = ref([])
const selectedUsers = ref([])

const userSearchForm = reactive({
  username: '',
  department: null,
})

const userPagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const userFormData = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  real_name: '',
  phone: '',
  department: null,
  role: 'drafter',
  reviewer_level: null,
  is_active: true,
})

const userFormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur', validator: (rule, value, callback) => {
      if (!isEditUser.value && !value) {
        callback(new Error('请输入密码'))
      } else {
        callback()
      }
    }},
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const userDialogTitle = computed(() => (isEditUser.value ? '编辑用户' : '新建用户'))

// 角色相关
const roles = ref([])
const rolesLoading = ref(false)
const roleDialogVisible = ref(false)
const isEditRole = ref(false)
const roleFormRef = ref(null)
const roleSubmitting = ref(false)
const assignPermissionsDialogVisible = ref(false)
const assignPermissionsSubmitting = ref(false)
const currentAssignRole = ref(null)
const selectedPermissionIds = ref([])
const allPermissions = ref([])
const selectedRoles = ref([])

const roleFormData = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
})

const roleFormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

const roleDialogTitle = computed(() => (isEditRole.value ? '编辑角色' : '新建角色'))

// 权限相关
const permissions = ref([])
const permissionsLoading = ref(false)
const permissionDialogVisible = ref(false)
const isEditPermission = ref(false)
const permissionFormRef = ref(null)
const permissionSubmitting = ref(false)
const selectedPermissions = ref([])

const permissionFormData = reactive({
  id: null,
  name: '',
  code: '',
  resource: '',
  action: '',
  description: '',
})

const permissionFormRules = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }],
}

const permissionDialogTitle = computed(() => (isEditPermission.value ? '编辑权限' : '新建权限'))

// Tab切换
const handleTabChange = (tabName) => {
  if (tabName === 'departments') {
    fetchDepartments()
  } else if (tabName === 'users') {
    fetchUsers()
  } else if (tabName === 'roles') {
    fetchRoles()
  } else if (tabName === 'permissions') {
    fetchPermissions()
  }
}

// 部门相关方法
const fetchDepartments = async () => {
  departmentsLoading.value = true
  try {
    const response = await api.get('/users/departments/', { params: { page_size: 1000 } })
    const deptList = response.data.results || []
    deptList.forEach(dept => {
      if (dept.parent) {
        const parent = allDepartments.value.find(p => p.id === dept.parent)
        dept.parent_name = parent ? parent.name : ''
      } else {
        dept.parent_name = ''
      }
    })
    departments.value = deptList
  } catch (error) {
    ElMessage.error('获取部门列表失败')
  } finally {
    departmentsLoading.value = false
  }
}

const fetchAllDepartments = async () => {
  try {
    const response = await api.get('/users/departments/', { params: { page_size: 1000 } })
    allDepartments.value = response.data.results || []
  } catch (error) {
    console.error('获取所有部门列表失败', error)
  }
}

const handleCreateDepartment = () => {
  isEditDepartment.value = false
  resetDepartmentForm()
  departmentDialogVisible.value = true
}

const handleEditDepartment = (row) => {
  isEditDepartment.value = true
  Object.assign(departmentFormData, {
    id: row.id,
    name: row.name,
    code: row.code || '',
    parent: row.parent || null,
    description: row.description || '',
  })
  departmentDialogVisible.value = true
}

const handleDepartmentSelectionChange = (selection) => {
  selectedDepartments.value = selection
}

const handleDeleteDepartment = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该部门吗？', '提示', {
      type: 'warning',
    })
    await api.delete(`/users/departments/${row.id}/`)
    ElMessage.success('删除成功')
    await fetchAllDepartments()
    fetchDepartments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDeleteDepartments = async () => {
  if (selectedDepartments.value.length === 0) {
    ElMessage.warning('请选择要删除的部门')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedDepartments.value.length} 个部门吗？`,
      '批量删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    )
    
    departmentsLoading.value = true
    let successCount = 0
    let failCount = 0
    
    for (const dept of selectedDepartments.value) {
      try {
        await api.delete(`/users/departments/${dept.id}/`)
        successCount++
      } catch (error) {
        failCount++
        console.error(`删除部门 ${dept.name} 失败:`, error)
      }
    }
    
    if (failCount === 0) {
      ElMessage.success(`成功删除 ${successCount} 个部门`)
    } else {
      ElMessage.warning(`成功删除 ${successCount} 个部门，失败 ${failCount} 个`)
    }
    
    selectedDepartments.value = []
    await fetchAllDepartments()
    fetchDepartments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    departmentsLoading.value = false
  }
}

const handleSubmitDepartment = async () => {
  if (!departmentFormRef.value) return
  await departmentFormRef.value.validate(async (valid) => {
    if (valid) {
      departmentSubmitting.value = true
      try {
        const submitData = { ...departmentFormData }
        if (!submitData.code) {
          delete submitData.code
        }
        if (isEditDepartment.value) {
          await api.patch(`/users/departments/${departmentFormData.id}/`, submitData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/departments/', submitData)
          ElMessage.success('创建成功')
        }
        departmentDialogVisible.value = false
        await fetchAllDepartments()
        fetchDepartments()
      } catch (error) {
        ElMessage.error(isEditDepartment.value ? '更新失败' : '创建失败')
      } finally {
        departmentSubmitting.value = false
      }
    }
  })
}

const handleDepartmentDialogClose = () => {
  departmentFormRef.value?.resetFields()
  resetDepartmentForm()
}

const resetDepartmentForm = () => {
  Object.assign(departmentFormData, {
    id: null,
    name: '',
    code: '',
    parent: null,
    description: '',
  })
}

// 用户相关方法
const fetchUsers = async () => {
  usersLoading.value = true
  try {
    const params = {
      page: userPagination.page,
      page_size: userPagination.pageSize,
      ...userSearchForm,
    }
    const response = await api.get('/users/users/', { params })
    users.value = response.data.results || []
    userPagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    usersLoading.value = false
  }
}

const handleSearchUsers = () => {
  userPagination.page = 1
  fetchUsers()
}

const handleResetUserSearch = () => {
  userSearchForm.username = ''
  userSearchForm.department = null
  handleSearchUsers()
}

const handleUserSizeChange = () => {
  fetchUsers()
}

const handleUserPageChange = () => {
  fetchUsers()
}

const handleCreateUser = () => {
  isEditUser.value = false
  resetUserForm()
  userDialogVisible.value = true
}

const handleEditUser = (row) => {
  isEditUser.value = true
  Object.assign(userFormData, {
    id: row.id,
    username: row.username,
    email: row.email,
    password: '',
    real_name: row.real_name || '',
    phone: row.phone || '',
    department: row.department || null,
    role: row.role,
    reviewer_level: row.reviewer_level || null,
    is_active: row.is_active,
  })
  userDialogVisible.value = true
}

const handleUserSelectionChange = (selection) => {
  selectedUsers.value = selection
}

const handleDeleteUser = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      type: 'warning',
    })
    await api.delete(`/users/users/${row.id}/`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDeleteUsers = async () => {
  if (selectedUsers.value.length === 0) {
    ElMessage.warning('请选择要删除的用户')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedUsers.value.length} 个用户吗？`,
      '批量删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    )
    
    usersLoading.value = true
    let successCount = 0
    let failCount = 0
    
    for (const user of selectedUsers.value) {
      try {
        await api.delete(`/users/users/${user.id}/`)
        successCount++
      } catch (error) {
        failCount++
        console.error(`删除用户 ${user.username} 失败:`, error)
      }
    }
    
    if (failCount === 0) {
      ElMessage.success(`成功删除 ${successCount} 个用户`)
    } else {
      ElMessage.warning(`成功删除 ${successCount} 个用户，失败 ${failCount} 个`)
    }
    
    selectedUsers.value = []
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    usersLoading.value = false
  }
}

const handleAssignRoles = async (row) => {
  currentAssignUser.value = row
  selectedRoleIds.value = row.roles ? row.roles.map(r => r.id) : []
  assignRolesDialogVisible.value = true
}

const handleSubmitAssignRoles = async () => {
  assignRolesSubmitting.value = true
  try {
    await api.post(`/users/users/${currentAssignUser.value.id}/assign_roles/`, {
      role_ids: selectedRoleIds.value,
    })
    ElMessage.success('分配角色成功')
    assignRolesDialogVisible.value = false
    fetchUsers()
  } catch (error) {
    ElMessage.error('分配角色失败')
  } finally {
    assignRolesSubmitting.value = false
  }
}

const handleSubmitUser = async () => {
  if (!userFormRef.value) return
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      userSubmitting.value = true
      try {
        const submitData = { ...userFormData }
        if (isEditUser.value && !submitData.password) {
          delete submitData.password
        }
        if (isEditUser.value) {
          await api.patch(`/users/users/${userFormData.id}/`, submitData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/users/', submitData)
          ElMessage.success('创建成功')
        }
        userDialogVisible.value = false
        fetchUsers()
      } catch (error) {
        ElMessage.error(isEditUser.value ? '更新失败' : '创建失败')
      } finally {
        userSubmitting.value = false
      }
    }
  })
}

const handleUserDialogClose = () => {
  userFormRef.value?.resetFields()
  resetUserForm()
}

const resetUserForm = () => {
  Object.assign(userFormData, {
    id: null,
    username: '',
    email: '',
    password: '',
    real_name: '',
    phone: '',
    department: null,
    role: 'drafter',
    reviewer_level: null,
    is_active: true,
  })
}

const getRoleText = (role) => {
  const roles = {
    admin: '管理员',
    reviewer: '审核员',
    drafter: '起草人',
  }
  return roles[role] || role
}

// 角色相关方法
const fetchRoles = async () => {
  rolesLoading.value = true
  try {
    const response = await api.get('/users/roles/', { params: { page_size: 1000 } })
    roles.value = response.data.results || []
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    rolesLoading.value = false
  }
}

const fetchAllRoles = async () => {
  try {
    const response = await api.get('/users/roles/', { params: { page_size: 1000 } })
    allRoles.value = response.data.results || []
  } catch (error) {
    console.error('获取所有角色列表失败', error)
  }
}

const handleCreateRole = () => {
  isEditRole.value = false
  resetRoleForm()
  roleDialogVisible.value = true
}

const handleEditRole = (row) => {
  isEditRole.value = true
  Object.assign(roleFormData, {
    id: row.id,
    name: row.name,
    code: row.code,
    description: row.description || '',
  })
  roleDialogVisible.value = true
}

const handleRoleSelectionChange = (selection) => {
  selectedRoles.value = selection
}

const handleDeleteRole = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该角色吗？', '提示', {
      type: 'warning',
    })
    await api.delete(`/users/roles/${row.id}/`)
    ElMessage.success('删除成功')
    fetchRoles()
    fetchAllRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDeleteRoles = async () => {
  if (selectedRoles.value.length === 0) {
    ElMessage.warning('请选择要删除的角色')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRoles.value.length} 个角色吗？`,
      '批量删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    )
    
    rolesLoading.value = true
    let successCount = 0
    let failCount = 0
    
    for (const role of selectedRoles.value) {
      try {
        await api.delete(`/users/roles/${role.id}/`)
        successCount++
      } catch (error) {
        failCount++
        console.error(`删除角色 ${role.name} 失败:`, error)
      }
    }
    
    if (failCount === 0) {
      ElMessage.success(`成功删除 ${successCount} 个角色`)
    } else {
      ElMessage.warning(`成功删除 ${successCount} 个角色，失败 ${failCount} 个`)
    }
    
    selectedRoles.value = []
    fetchRoles()
    fetchAllRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    rolesLoading.value = false
  }
}

const handleAssignPermissions = async (row) => {
  currentAssignRole.value = row
  selectedPermissionIds.value = row.permissions ? row.permissions.map(p => p.id) : []
  assignPermissionsDialogVisible.value = true
}

const handleSubmitAssignPermissions = async () => {
  assignPermissionsSubmitting.value = true
  try {
    await api.patch(`/users/roles/${currentAssignRole.value.id}/`, {
      permission_ids: selectedPermissionIds.value,
    })
    ElMessage.success('分配权限成功')
    assignPermissionsDialogVisible.value = false
    fetchRoles()
  } catch (error) {
    ElMessage.error('分配权限失败')
  } finally {
    assignPermissionsSubmitting.value = false
  }
}

const handleSubmitRole = async () => {
  if (!roleFormRef.value) return
  await roleFormRef.value.validate(async (valid) => {
    if (valid) {
      roleSubmitting.value = true
      try {
        if (isEditRole.value) {
          await api.patch(`/users/roles/${roleFormData.id}/`, roleFormData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/roles/', roleFormData)
          ElMessage.success('创建成功')
        }
        roleDialogVisible.value = false
        fetchRoles()
        fetchAllRoles()
      } catch (error) {
        ElMessage.error(isEditRole.value ? '更新失败' : '创建失败')
      } finally {
        roleSubmitting.value = false
      }
    }
  })
}

const handleRoleDialogClose = () => {
  roleFormRef.value?.resetFields()
  resetRoleForm()
}

const resetRoleForm = () => {
  Object.assign(roleFormData, {
    id: null,
    name: '',
    code: '',
    description: '',
  })
}

// 权限相关方法
const handlePermissionSelectionChange = (selection) => {
  selectedPermissions.value = selection
}

const fetchPermissions = async () => {
  permissionsLoading.value = true
  try {
    const response = await api.get('/users/permissions/', { params: { page_size: 1000 } })
    permissions.value = response.data.results || []
    allPermissions.value = response.data.results || []
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    permissionsLoading.value = false
  }
}

const handleCreatePermission = () => {
  isEditPermission.value = false
  resetPermissionForm()
  permissionDialogVisible.value = true
}

const handleEditPermission = (row) => {
  isEditPermission.value = true
  Object.assign(permissionFormData, {
    id: row.id,
    name: row.name,
    code: row.code,
    resource: row.resource || '',
    action: row.action || '',
    description: row.description || '',
  })
  permissionDialogVisible.value = true
}

const handleDeletePermission = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该权限吗？', '提示', {
      type: 'warning',
    })
    await api.delete(`/users/permissions/${row.id}/`)
    ElMessage.success('删除成功')
    fetchPermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDeletePermissions = async () => {
  if (selectedPermissions.value.length === 0) {
    ElMessage.warning('请选择要删除的权限')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedPermissions.value.length} 个权限吗？`,
      '批量删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    )
    
    permissionsLoading.value = true
    let successCount = 0
    let failCount = 0
    
    for (const permission of selectedPermissions.value) {
      try {
        await api.delete(`/users/permissions/${permission.id}/`)
        successCount++
      } catch (error) {
        failCount++
        console.error(`删除权限 ${permission.name} 失败:`, error)
      }
    }
    
    if (failCount === 0) {
      ElMessage.success(`成功删除 ${successCount} 个权限`)
    } else {
      ElMessage.warning(`成功删除 ${successCount} 个权限，失败 ${failCount} 个`)
    }
    
    selectedPermissions.value = []
    fetchPermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    permissionsLoading.value = false
  }
}

const handleSubmitPermission = async () => {
  if (!permissionFormRef.value) return
  await permissionFormRef.value.validate(async (valid) => {
    if (valid) {
      permissionSubmitting.value = true
      try {
        if (isEditPermission.value) {
          await api.patch(`/users/permissions/${permissionFormData.id}/`, permissionFormData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/permissions/', permissionFormData)
          ElMessage.success('创建成功')
        }
        permissionDialogVisible.value = false
        fetchPermissions()
      } catch (error) {
        ElMessage.error(isEditPermission.value ? '更新失败' : '创建失败')
      } finally {
        permissionSubmitting.value = false
      }
    }
  })
}

const handlePermissionDialogClose = () => {
  permissionFormRef.value?.resetFields()
  resetPermissionForm()
}

const resetPermissionForm = () => {
  Object.assign(permissionFormData, {
    id: null,
    name: '',
    code: '',
    resource: '',
    action: '',
    description: '',
  })
}

onMounted(async () => {
  await fetchAllDepartments()
  await fetchAllRoles()
  fetchDepartments()
  fetchPermissions()
})
</script>

<style scoped>
.permission-config {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tab-content {
  padding: 20px 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-form {
  margin: 0;
}
</style>

