<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建用户
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent="handleSearch">
        <el-form-item label="用户名">
          <el-input 
            v-model="searchForm.username" 
            placeholder="请输入用户名" 
            clearable 
            @keyup.enter="handleSearch"
            style="min-width: 180px"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select 
            v-model="searchForm.role" 
            placeholder="请选择" 
            clearable 
            filterable
            style="min-width: 180px"
            @change="handleSearch"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="审核员" value="reviewer" />
            <el-option label="起草人" value="drafter" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag>{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department_name" label="部门" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="formData.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="password" v-if="isEdit">
          <el-input v-model="formData.password" type="password" show-password placeholder="留空则不修改密码" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="formData.real_name" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="formData.phone" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-select 
            v-model="formData.department" 
            placeholder="请选择部门" 
            clearable 
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select 
            v-model="formData.role" 
            placeholder="请选择角色" 
            filterable
            style="width: 100%"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="审核员" value="reviewer" />
            <el-option label="起草人" value="drafter" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const departments = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  username: '',
  role: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const formData = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  real_name: '',
  phone: '',
  department: null,
  role: 'drafter',
  is_active: true,
})

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur', validator: (rule, value, callback) => {
      if (!isEdit.value && !value) {
        callback(new Error('请输入密码'))
      } else {
        callback()
      }
    }},
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const dialogTitle = computed(() => (isEdit.value ? '编辑用户' : '新建用户'))

const getRoleText = (role) => {
  const roles = {
    admin: '管理员',
    reviewer: '审核员',
    drafter: '起草人',
  }
  return roles[role] || role
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    }
    const response = await api.get('/users/users/', { params })
    users.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const response = await api.get('/users/departments/')
    departments.value = response.data.results || []
  } catch (error) {
    console.error('获取部门列表失败', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchUsers()
}

const handleReset = () => {
  searchForm.username = ''
  searchForm.role = ''
  handleSearch()
}

const handleSizeChange = () => {
  fetchUsers()
}

const handlePageChange = () => {
  fetchUsers()
}

const handleCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, {
    id: row.id,
    username: row.username,
    email: row.email,
    password: '',
    real_name: row.real_name || '',
    phone: row.phone || '',
    department: row.department || null,
    role: row.role,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
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

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData = { ...formData }
        if (isEdit.value && !submitData.password) {
          delete submitData.password
        }
        if (isEdit.value) {
          await api.patch(`/users/users/${formData.id}/`, submitData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/users/', submitData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetForm()
}

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    username: '',
    email: '',
    password: '',
    real_name: '',
    phone: '',
    department: null,
    role: 'drafter',
    is_active: true,
  })
}

onMounted(() => {
  fetchUsers()
  fetchDepartments()
})
</script>

<style scoped>
.user-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>

