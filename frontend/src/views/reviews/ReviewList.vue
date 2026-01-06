<template>
  <div class="review-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isReviewer ? '我的审核任务' : '审核任务列表' }}</span>
          <div style="display: flex; gap: 10px">
            <el-button
              v-if="isReviewer"
              type="success"
              @click="showMyTasksOnly = !showMyTasksOnly"
            >
              {{ showMyTasksOnly ? '显示全部' : '仅显示我的任务' }}
            </el-button>
            <el-button
              v-if="isAdmin || !isReviewer"
              type="danger"
              :disabled="selectedReviews.length === 0"
              @click="handleBatchDelete"
            >
              批量删除 ({{ selectedReviews.length }})
            </el-button>
            <el-button v-if="isAdmin || !isReviewer" type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              新建审核任务
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="AI审核中" value="ai_processing" />
            <el-option label="AI审核完成" value="ai_completed" />
            <el-option label="人工审核中" value="manual_reviewing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        :data="reviews"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="expand">
          <template #default="{ row }">
            <div style="padding: 20px">
              <ReviewWorkflow
                :status="row.status"
                :reviewer-level="row.reviewer_level"
                :review-levels="row.review_levels || ['level1', 'level2', 'level3']"
                :reviewer-assignments="row.reviewer_assignments || {}"
                :reviewer-assignments-detail="row.reviewer_assignments_detail || {}"
                :started-at="row.started_at"
                :completed-at="row.completed_at"
                :error-message="row.error_message"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="contract_title" label="合同标题" />
        <el-table-column prop="status" label="状态" width="120">
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
              :loading="starting[row.id]"
            >
              启动
            </el-button>
            <el-button
              v-if="row.status === 'processing'"
              link
              type="warning"
              @click="handleCompleteManually(row)"
              :loading="completing[row.id]"
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
            <el-button
              link
              type="danger"
              @click="handleDelete(row)"
              :loading="deleting[row.id]"
            >
              删除
            </el-button>
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
            popper-class="contract-select-dropdown"
            :teleported="false"
            clearable
          >
            <el-option
              v-for="contract in contracts"
              :key="contract.id"
              :label="contract.title ? `${contract.contract_no || '未填写编号'} - ${contract.title.length > 25 ? contract.title.substring(0, 25) + '...' : contract.title}` : (contract.contract_no || '未填写编号')"
              :value="contract.id"
            >
              <div style="display: flex; flex-direction: column; padding: 4px 0">
                <div style="font-weight: 500; color: #303133; margin-bottom: 4px">
                  {{ contract.contract_no || '未填写编号' }}
                </div>
                <div 
                  v-if="contract.title && contract.title.trim()" 
                  style="font-size: 12px; color: #909399; word-break: break-word; white-space: normal"
                >
                  {{ contract.title }}
                </div>
                <div 
                  v-else 
                  style="font-size: 12px; color: #C0C4CC; font-style: italic"
                >
                  未填写标题
                </div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item
          label="审核层级"
          prop="review_levels"
        >
          <el-checkbox-group v-model="formData.review_levels" style="width: 100%">
            <el-checkbox label="level1">一级审核员</el-checkbox>
            <el-checkbox label="level2">二级审核员</el-checkbox>
            <el-checkbox label="level3">三级审核员（高级）</el-checkbox>
          </el-checkbox-group>
          <div style="color: #909399; font-size: 12px; margin-top: 5px">
            请选择需要参与的审核层级，至少选择一个。审核流程：先AI自动审核，然后分配给选定的层级进行人工校验
          </div>
        </el-form-item>
        <!-- 审核人员分配 -->
        <template v-if="formData.review_levels && formData.review_levels.length > 0">
          <el-form-item
            v-for="level in formData.review_levels"
            :key="level"
            :label="getLevelLabel(level) + '审核员'"
          >
            <el-select
              v-model="formData.reviewer_assignments[level]"
              :placeholder="`请选择${getLevelLabel(level)}审核员`"
              style="width: 100%"
              filterable
              :loading="loadingReviewers"
            >
              <el-option
                v-for="reviewer in getReviewersByLevel(level)"
                :key="reviewer.id"
                :label="reviewer.real_name || reviewer.username"
                :value="reviewer.id"
              >
                <span>{{ reviewer.real_name || reviewer.username }}</span>
                <span style="color: #8492a6; font-size: 13px; margin-left: 10px">
                  ({{ reviewer.email }})
                </span>
              </el-option>
            </el-select>
          </el-form-item>
        </template>
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
import ReviewWorkflow from '@/components/ReviewWorkflow.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const currentUser = computed(() => userStore.user)
const isReviewer = computed(() => currentUser.value?.role === 'reviewer')
const isAdmin = computed(() => currentUser.value?.role === 'admin')

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const starting = ref({}) // 存储每个任务的启动状态
const completing = ref({}) // 存储每个任务的手动完成状态
const deleting = ref({}) // 存储每个任务的删除状态
const reviews = ref([])
const contracts = ref([])
const reviewers = ref({}) // 存储审核人员列表，按层级分组
const loadingReviewers = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const showMyTasksOnly = ref(true) // 审核员默认只显示自己的任务

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
  priority: 'medium',
  review_levels: ['level1', 'level2', 'level3'], // 默认选择所有层级
  reviewer_assignments: {}, // 存储每个层级对应的审核员ID，格式：{level1: 1, level2: 2}
})

const formRules = {
  contract: [{ required: true, message: '请选择合同', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  review_levels: [
    {
      validator: (rule, value, callback) => {
        if (!value || value.length === 0) {
          callback(new Error('请至少选择一个审核层级'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
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
  // 如果是数字，转换为文本
  if (typeof priority === 'number') {
    const numToText = {
      2: '高',
      1: '中',
      0: '低'
    }
    return numToText[priority] || '中'
  }
  // 如果是字符串，直接返回
  const texts = {
    high: '高',
    medium: '中',
    low: '低',
  }
  return texts[priority] || priority
}

// 将优先级数字转换为字符串
const getPriorityString = (priority) => {
  if (typeof priority === 'number') {
    const numToString = {
      2: 'high',
      1: 'medium',
      0: 'low'
    }
    return numToString[priority] || 'medium'
  }
  return priority || 'medium'
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
    // 获取所有合同，使用分页循环加载
    let allContracts = []
    let page = 1
    let hasMore = true
    
    while (hasMore) {
      const response = await api.get('/contracts/contracts/', { 
        params: { 
          page: page,
          page_size: 100  // 每次加载100条
        } 
      })
      
      const results = response.data.results || []
      allContracts = allContracts.concat(results)
      
      // 检查是否还有更多数据
      const total = response.data.count || 0
      hasMore = allContracts.length < total && results.length > 0
      page++
      
      // 防止无限循环
      if (page > 100) {
        console.warn('合同数量过多，已加载前100页')
        break
      }
    }
    
    contracts.value = allContracts
    console.log(`已加载 ${allContracts.length} 个合同`)
  } catch (error) {
    console.error('获取合同列表失败', error)
    ElMessage.error('获取合同列表失败: ' + (error.response?.data?.detail || error.message))
  }
}

const fetchReviewers = async () => {
  loadingReviewers.value = true
  try {
    const response = await api.get('/reviews/tasks/reviewers/')
    reviewers.value = response.data.grouped || {}
  } catch (error) {
    console.error('获取审核人员列表失败', error)
    ElMessage.error('获取审核人员列表失败')
  } finally {
    loadingReviewers.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchReviews()
}

const handleReset = () => {
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
  fetchReviewers() // 总是获取审核人员列表
  dialogVisible.value = true
}

// 移除handleTaskTypeChange，不再需要

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, {
    id: row.id,
    contract: row.contract,
    priority: getPriorityString(row.priority),
    review_levels: row.review_levels || ['level1', 'level2', 'level3'],
    reviewer_assignments: row.reviewer_assignments || {},
  })
  fetchReviewers() // 总是获取审核人员列表
  dialogVisible.value = true
}

const selectedReviews = ref([])

const handleSelectionChange = (selection) => {
  selectedReviews.value = selection
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该审核任务吗？', '提示', {
      type: 'warning',
    })
    deleting.value[row.id] = true
    try {
      await api.delete(`/reviews/tasks/${row.id}/`)
      ElMessage.success('删除成功')
      fetchReviews()
    } catch (error) {
      ElMessage.error('删除失败')
    } finally {
      deleting.value[row.id] = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      // 用户取消
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedReviews.value.length === 0) {
    ElMessage.warning('请选择要删除的审核任务')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedReviews.value.length} 个审核任务吗？`,
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
    
    for (const review of selectedReviews.value) {
      try {
        deleting.value[review.id] = true
        await api.delete(`/reviews/tasks/${review.id}/`)
        successCount++
      } catch (error) {
        failCount++
        console.error(`删除审核任务 ${review.id} 失败:`, error)
      } finally {
        deleting.value[review.id] = false
      }
    }
    
    if (failCount === 0) {
      ElMessage.success(`成功删除 ${successCount} 个审核任务`)
    } else {
      ElMessage.warning(`成功删除 ${successCount} 个审核任务，失败 ${failCount} 个`)
    }
    
    selectedReviews.value = []
    fetchReviews()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value = false
  }
}

const handleView = (row) => {
  router.push(`/reviews/${row.id}`)
}

// 检查审核员是否可以审核该任务
const canReviewTask = (task) => {
  if (!isReviewer.value || !currentUser.value) return false
  
  // 检查是否分配给当前用户
  if (task.reviewer === currentUser.value.id) return true
  
  // 检查reviewer_assignments中是否包含当前用户
  if (task.reviewer_assignments && typeof task.reviewer_assignments === 'object') {
    const userLevel = currentUser.value.reviewer_level
    if (userLevel && task.reviewer_assignments[userLevel] === currentUser.value.id) {
      return true
    }
  }
  
  return false
}

// 审核员开始审核
const handleStartReview = (row) => {
  router.push(`/reviews/${row.id}?action=review`)
}

const handleStart = async (row) => {
  starting.value[row.id] = true
  try {
    await api.post(`/reviews/tasks/${row.id}/start/`)
    ElMessage.success('审核任务已启动')
    fetchReviews()
  } catch (error) {
    ElMessage.error('启动审核任务失败')
  } finally {
    starting.value[row.id] = false
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
    completing.value[row.id] = true
    try {
      await api.post(`/reviews/tasks/${row.id}/complete_manually/`)
      ElMessage.success('任务已手动完成')
      fetchReviews()
    } catch (error) {
      const errorMsg = error.response?.data?.error || '手动完成失败'
      ElMessage.error(errorMsg)
    } finally {
      completing.value[row.id] = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      // 用户取消
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        // 准备提交数据
        const submitData = {
          contract: formData.contract,
          priority: getPriorityValue(formData.priority),
          review_levels: formData.review_levels || ['level1', 'level2', 'level3'],
        }
        
        // 添加审核层级配置和审核员分配
        // 只提交已选择的层级对应的审核员
        const assignments = {}
        formData.review_levels.forEach(level => {
          if (formData.reviewer_assignments[level]) {
            assignments[level] = formData.reviewer_assignments[level]
          }
        })
        if (Object.keys(assignments).length > 0) {
          submitData.reviewer_assignments = assignments
        }
        
        if (isEdit.value) {
          await api.patch(`/reviews/tasks/${formData.id}/`, submitData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/reviews/tasks/', submitData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchReviews()
      } catch (error) {
        const errorMsg = error.response?.data?.detail || error.response?.data?.error || (isEdit.value ? '更新失败' : '创建失败')
        ElMessage.error(errorMsg)
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 将优先级字符串转换为数字
const getPriorityValue = (priority) => {
  const priorityMap = {
    high: 2,
    medium: 1,
    low: 0
  }
  return priorityMap[priority] || 1
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetForm()
}

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    contract: null,
    priority: 'medium',
    review_levels: ['level1', 'level2', 'level3'],
    reviewer_assignments: {},
  })
}

const getLevelLabel = (level) => {
  const labels = {
    level1: '一级',
    level2: '二级',
    level3: '三级（高级）',
  }
  return labels[level] || level
}

const getReviewersByLevel = (level) => {
  return reviewers.value[level] || []
}


onMounted(() => {
  fetchReviews()
  fetchContracts()
  // 总是获取审核人员列表
  fetchReviewers()
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

/* 合同选择下拉框样式优化 */
:deep(.contract-select-dropdown) {
  min-width: 400px !important;
}

:deep(.contract-select-dropdown .el-select-dropdown__item) {
  height: auto !important;
  padding: 8px 20px !important;
  line-height: normal !important;
}

:deep(.contract-select-dropdown .el-select-dropdown__item:hover) {
  background-color: #f5f7fa;
}

:deep(.contract-select-dropdown .el-select-dropdown__item.is-selected) {
  background-color: #ecf5ff;
}

:deep(.contract-select-dropdown .el-select-dropdown__item .el-select-dropdown__item) {
  padding: 0 !important;
}
</style>

