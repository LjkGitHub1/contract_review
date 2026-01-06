<template>
  <div class="department-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门列表</span>
          <div style="display: flex; gap: 10px">
            <el-button
              type="danger"
              :disabled="selectedDepartments.length === 0"
              @click="handleBatchDelete"
            >
              批量删除 ({{ selectedDepartments.length }})
            </el-button>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建部门
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent="handleSearch">
        <el-form-item label="部门名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入部门名称" 
            clearable 
            @keyup.enter="handleSearch"
            style="min-width: 180px"
          />
        </el-form-item>
        <el-form-item label="部门编码">
          <el-input 
            v-model="searchForm.code" 
            placeholder="请输入部门编码" 
            clearable 
            @keyup.enter="handleSearch"
            style="min-width: 180px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        :data="departments"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
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
        label-width="120px"
      >
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="formData.code" placeholder="可选，如不填写将自动生成" />
        </el-form-item>
        <el-form-item label="父部门" prop="parent">
          <el-select
            v-model="formData.parent"
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
              :disabled="dept.id === formData.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="部门描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="4" />
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
const departments = ref([])
const allDepartments = ref([]) // 用于查找父部门名称
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const selectedDepartments = ref([])

const searchForm = reactive({
  name: '',
  code: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const formData = reactive({
  id: null,
  name: '',
  code: '',
  parent: null,
  description: '',
})

const formRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
}

const dialogTitle = computed(() => (isEdit.value ? '编辑部门' : '新建部门'))

const parentDepartments = computed(() => {
  // 编辑时，排除自己（避免循环引用）
  if (isEdit.value && formData.id) {
    return allDepartments.value.filter(dept => dept.id !== formData.id)
  }
  return allDepartments.value
})

const fetchAllDepartments = async () => {
  try {
    const response = await api.get('/users/departments/', { params: { page_size: 1000 } })
    allDepartments.value = response.data.results || []
  } catch (error) {
    console.error('获取所有部门列表失败', error)
  }
}

const fetchDepartments = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    }
    const response = await api.get('/users/departments/', { params })
    // 处理父部门名称显示
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
    pagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取部门列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchDepartments()
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.code = ''
  handleSearch()
}

const handleSizeChange = () => {
  fetchDepartments()
}

const handlePageChange = () => {
  fetchDepartments()
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
    name: row.name,
    code: row.code || '',
    parent: row.parent || null,
    description: row.description || '',
  })
  dialogVisible.value = true
}

const handleSelectionChange = (selection) => {
  selectedDepartments.value = selection
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该部门吗？删除后该部门下的用户将无法关联到此部门。', '提示', {
      type: 'warning',
    })
    await api.delete(`/users/departments/${row.id}/`)
    ElMessage.success('删除成功')
    fetchDepartments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedDepartments.value.length === 0) {
    ElMessage.warning('请选择要删除的部门')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedDepartments.value.length} 个部门吗？删除后这些部门下的用户将无法关联到这些部门。`,
      '批量删除',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
      }
    )
    
    loading.value = true
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
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData = { ...formData }
        // 如果编码为空，则不传（让后端自动生成）
        if (!submitData.code) {
          delete submitData.code
        }
        if (isEdit.value) {
          await api.patch(`/users/departments/${formData.id}/`, submitData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/departments/', submitData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        await fetchAllDepartments() // 刷新所有部门列表
        fetchDepartments()
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
    name: '',
    code: '',
    parent: null,
    description: '',
  })
}

onMounted(async () => {
  await fetchAllDepartments()
  fetchDepartments()
})
</script>

<style scoped>
.department-list {
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

