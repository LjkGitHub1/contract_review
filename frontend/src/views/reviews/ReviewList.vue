<template>
  <div class="review-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审核任务列表</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建审核任务
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="任务类型">
          <el-select v-model="searchForm.task_type" placeholder="请选择" clearable>
            <el-option label="自动审核" value="auto" />
            <el-option label="人工审核" value="manual" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="reviews" v-loading="loading" style="width: 100%">
        <el-table-column prop="contract_title" label="合同标题" />
        <el-table-column prop="task_type" label="任务类型" width="120">
          <template #default="{ row }">
            {{ row.task_type === 'auto' ? '自动审核' : '人工审核' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            {{ getPriorityText(row.priority) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button
              v-if="row.status === 'pending'"
              link
              type="success"
              @click="handleStart(row)"
            >
              启动
            </el-button>
            <el-button
              v-if="row.status === 'processing'"
              link
              type="warning"
              @click="handleCompleteManually(row)"
            >
              手动完成
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              link
              type="primary"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
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
        <el-form-item label="合同" prop="contract">
          <el-select
            v-model="formData.contract"
            placeholder="请选择合同"
            filterable
            style="width: 100%"
            :disabled="isEdit"
          >
            <el-option
              v-for="contract in contracts"
              :key="contract.id"
              :label="`${contract.contract_no} - ${contract.title}`"
              :value="contract.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务类型" prop="task_type">
          <el-select v-model="formData.task_type" placeholder="请选择任务类型" style="width: 100%">
            <el-option label="自动审核" value="auto" />
            <el-option label="人工审核" value="manual" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/date'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const reviews = ref([])
const contracts = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  task_type: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const formData = reactive({
  id: null,
  contract: null,
  task_type: 'auto',
  priority: 'medium',
})

const formRules = {
  contract: [{ required: true, message: '请选择合同', trigger: 'change' }],
  task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
}

const dialogTitle = computed(() => (isEdit.value ? '编辑审核任务' : '新建审核任务'))

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

const getPriorityText = (priority) => {
  const texts = {
    high: '高',
    medium: '中',
    low: '低',
  }
  return texts[priority] || priority
}

const fetchReviews = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    }
    const response = await api.get('/reviews/tasks/', { params })
    reviews.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取审核任务列表失败')
  } finally {
    loading.value = false
  }
}

const fetchContracts = async () => {
  try {
    const response = await api.get('/contracts/contracts/', { params: { page_size: 1000 } })
    contracts.value = response.data.results || []
  } catch (error) {
    console.error('获取合同列表失败', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchReviews()
}

const handleReset = () => {
  searchForm.task_type = ''
  searchForm.status = ''
  handleSearch()
}

const handleSizeChange = () => {
  fetchReviews()
}

const handlePageChange = () => {
  fetchReviews()
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
    contract: row.contract,
    task_type: row.task_type,
    priority: row.priority || 'medium',
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该审核任务吗？', '提示', {
      type: 'warning',
    })
    await api.delete(`/reviews/tasks/${row.id}/`)
    ElMessage.success('删除成功')
    fetchReviews()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleView = (row) => {
  router.push(`/reviews/${row.id}`)
}

const handleStart = async (row) => {
  try {
    await api.post(`/reviews/tasks/${row.id}/start/`)
    ElMessage.success('审核任务已启动')
    fetchReviews()
  } catch (error) {
    ElMessage.error('启动审核任务失败')
  }
}

const handleCompleteManually = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定要手动完成该审核任务吗？这将尝试同步执行审核任务。',
      '提示',
      {
        type: 'warning',
      }
    )
    await api.post(`/reviews/tasks/${row.id}/complete_manually/`)
    ElMessage.success('任务已手动完成')
    fetchReviews()
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || '手动完成失败'
      ElMessage.error(errorMsg)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.patch(`/reviews/tasks/${formData.id}/`, formData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/reviews/tasks/', formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchReviews()
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
    contract: null,
    task_type: 'auto',
    priority: 'medium',
  })
}

onMounted(() => {
  fetchReviews()
  fetchContracts()
})
</script>

<style scoped>
.review-list {
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

