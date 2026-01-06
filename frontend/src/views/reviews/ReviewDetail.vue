<template>
  <div class="review-detail">
    <!-- 审核流程展示 -->
    <ReviewWorkflow
      v-if="task"
      :status="task.status"
      :reviewer-level="task.reviewer_level"
      :review-levels="task.review_levels || ['level1', 'level2', 'level3']"
      :reviewer-assignments="task.reviewer_assignments || {}"
      :reviewer-assignments-detail="task.reviewer_assignments_detail || {}"
      :started-at="task.started_at"
      :completed-at="task.completed_at"
      :error-message="task.error_message"
    />

    <el-card v-loading="loading">
      <template #header>
        <span>审核详情</span>
      </template>
      
      <!-- 任务基本信息 -->
      <div v-if="task" style="margin-bottom: 20px">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="合同标题">{{ task.contract_title }}</el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="getStatusType(task.status)">{{ getStatusText(task.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="审核层级">
            <el-tag v-for="level in (task.review_levels || [])" :key="level" style="margin-right: 5px">
              {{ getLevelLabel(level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(task.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间" v-if="task.started_at">
            {{ formatDateTime(task.started_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间" v-if="task.completed_at">
            {{ formatDateTime(task.completed_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="错误信息" v-if="task.error_message" :span="2">
            <el-alert :title="task.error_message" type="error" :closable="false" />
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 审核结果详情展示 -->
      <div v-if="result">
        <!-- 报告操作按钮 -->
        <div style="margin-bottom: 20px; text-align: right">
          <el-button
            v-if="result.report_path"
            type="primary"
            @click="downloadReport"
            :loading="downloading"
          >
            <el-icon><Download /></el-icon>
            下载审核报告
          </el-button>
          <el-button
            v-if="result.report_path"
            type="info"
            @click="previewReport"
          >
            <el-icon><View /></el-icon>
            预览报告
          </el-button>
        </div>

        <ReviewResultDetail :result="result" />
        
        <!-- AI审核建议（针对当前审核层级） -->
        <el-card v-if="task && task.status === 'manual_reviewing' && currentUser?.role === 'reviewer' && aiSuggestions" shadow="never" style="margin-top: 20px">
          <template #header>
            <div style="display: flex; align-items: center; gap: 10px">
              <el-icon style="color: #409EFF"><InfoFilled /></el-icon>
              <span>AI审核建议（{{ getLevelLabel(task.reviewer_level) }}）</span>
            </div>
          </template>
          <div v-if="aiSuggestions.error" style="color: #F56C6C">
            {{ aiSuggestions.error }}
          </div>
          <div v-else>
            <el-descriptions :column="1" border style="margin-bottom: 20px">
              <el-descriptions-item label="审核层级">
                {{ aiSuggestions.reviewer_level_name }}
              </el-descriptions-item>
              <el-descriptions-item label="审核重点">
                <el-tag v-for="(point, index) in aiSuggestions.focus_config?.focus_points" :key="index" style="margin-right: 5px; margin-bottom: 5px">
                  {{ point }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
            
            <div v-if="aiSuggestions.suggestions">
              <el-divider>AI建议内容</el-divider>
              <div v-html="aiSuggestions.suggestions.summary || aiSuggestions.suggestions.text || '暂无建议'"></div>
              
              <div v-if="aiSuggestions.suggestions.issues && aiSuggestions.suggestions.issues.length > 0" style="margin-top: 20px">
                <el-divider>重点关注事项</el-divider>
                <el-table :data="aiSuggestions.suggestions.issues" style="width: 100%">
                  <el-table-column prop="clause_id" label="条款ID" width="100" />
                  <el-table-column prop="clause_content" label="条款内容" />
                  <el-table-column prop="issue_description" label="问题描述" />
                  <el-table-column prop="risk_level" label="风险等级" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getRiskType(row.risk_level)">{{ getRiskText(row.risk_level) }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="suggestion" label="修改建议" />
                </el-table>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 审核意见闭环功能 -->
        <el-divider>
          <span>审核意见闭环</span>
        </el-divider>
        <el-space direction="vertical" style="width: 100%" size="large">
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>意见汇总与反馈</span>
                <el-button type="primary" @click="handleSummarizeOpinions" :loading="summarizing">
                  汇总审核意见
                </el-button>
              </div>
            </template>
            <div v-if="summaryTable">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="总意见数">{{ summaryTable.statistics?.total_opinions || 0 }}</el-descriptions-item>
                <el-descriptions-item label="高风险">
                  <el-tag type="danger">{{ summaryTable.statistics?.high_risk_count || 0 }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="中风险">
                  <el-tag type="warning">{{ summaryTable.statistics?.medium_risk_count || 0 }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="低风险">
                  <el-tag type="success">{{ summaryTable.statistics?.low_risk_count || 0 }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
              
              <el-tabs v-model="opinionTab" style="margin-top: 20px">
                <el-tab-pane label="一级审核意见" name="level1">
                  <el-table :data="summaryTable.level1_opinions" style="width: 100%">
                    <el-table-column prop="type" label="类型" width="100" />
                    <el-table-column prop="risk_level" label="风险等级" width="100" />
                    <el-table-column prop="content" label="意见内容" />
                    <el-table-column prop="suggestion" label="修改建议" />
                  </el-table>
                </el-tab-pane>
                <el-tab-pane label="二级审核意见" name="level2">
                  <el-table :data="summaryTable.level2_opinions" style="width: 100%">
                    <el-table-column prop="type" label="类型" width="100" />
                    <el-table-column prop="risk_level" label="风险等级" width="100" />
                    <el-table-column prop="content" label="意见内容" />
                    <el-table-column prop="suggestion" label="修改建议" />
                  </el-table>
                </el-tab-pane>
                <el-tab-pane label="三级审核意见" name="level3">
                  <el-table :data="summaryTable.level3_opinions" style="width: 100%">
                    <el-table-column prop="type" label="类型" width="100" />
                    <el-table-column prop="risk_level" label="风险等级" width="100" />
                    <el-table-column prop="content" label="意见内容" />
                    <el-table-column prop="suggestion" label="修改建议" />
                  </el-table>
                </el-tab-pane>
                <el-tab-pane label="全部意见" name="all">
                  <el-table :data="summaryTable.all_opinions" style="width: 100%">
                    <el-table-column prop="reviewer_level" label="审核层级" width="100" />
                    <el-table-column prop="type" label="类型" width="100" />
                    <el-table-column prop="risk_level" label="风险等级" width="100" />
                    <el-table-column prop="content" label="意见内容" />
                    <el-table-column prop="suggestion" label="修改建议" />
                  </el-table>
                </el-tab-pane>
              </el-tabs>
              
              <div style="margin-top: 20px">
                <el-button type="success" @click="handleFeedbackToDrafter" :loading="feedbacking">
                  反馈给起草人
                </el-button>
                <el-button type="primary" @click="handleResubmit" :loading="resubmitting">
                  重新提交审核
                </el-button>
              </div>
            </div>
            <el-empty v-else description="请先汇总审核意见" />
          </el-card>
        </el-space>
      </div>
      <div v-else-if="task">
        <el-alert
          v-if="task.status === 'pending'"
          title="审核任务待处理"
          description="任务已创建，等待启动审核流程"
          type="info"
          :closable="false"
          show-icon
        />
        <!-- AI审核进度显示 -->
        <el-card v-else-if="task.status === 'ai_processing'" shadow="never" style="margin-bottom: 20px">
          <template #header>
            <div style="display: flex; align-items: center; gap: 10px">
              <el-icon class="is-loading" style="color: #409EFF"><Loading /></el-icon>
              <span>AI审核进行中</span>
            </div>
          </template>
          <div v-if="task.progress">
            <div style="margin-bottom: 20px">
              <div style="display: flex; justify-content: space-between; margin-bottom: 10px">
                <span style="font-weight: 500">{{ task.progress.current_step || '处理中...' }}</span>
                <span style="color: #409EFF">{{ task.progress.progress || 0 }}%</span>
              </div>
              <el-progress 
                :percentage="task.progress.progress || 0" 
                :status="task.progress.progress === 100 ? 'success' : undefined"
                :stroke-width="20"
              />
              <div style="margin-top: 10px; color: #909399; font-size: 14px">
                {{ task.progress.message || '正在处理中...' }}
              </div>
            </div>
            <el-divider />
            <div>
              <div style="font-weight: 500; margin-bottom: 10px">审核步骤：</div>
              <el-timeline v-if="task.progress.steps && task.progress.steps.length > 0">
                <el-timeline-item
                  v-for="(step, index) in task.progress.steps"
                  :key="index"
                  :timestamp="step.name"
                  :type="step.status === 'completed' ? 'success' : (step.status === 'processing' ? 'primary' : 'info')"
                  :icon="step.status === 'completed' ? 'Check' : (step.status === 'processing' ? 'Loading' : 'Clock')"
                >
                  <el-tag 
                    :type="step.status === 'completed' ? 'success' : (step.status === 'processing' ? 'primary' : 'info')"
                    size="small"
                  >
                    {{ step.status === 'completed' ? '已完成' : (step.status === 'processing' ? '进行中' : '待处理') }}
                  </el-tag>
                </el-timeline-item>
              </el-timeline>
              <div v-else style="color: #909399; font-size: 14px">暂无步骤信息</div>
            </div>
          </div>
          <div v-else style="text-align: center; padding: 20px">
            <el-icon class="is-loading" style="font-size: 24px; color: #409EFF"><Loading /></el-icon>
            <div style="margin-top: 10px; color: #909399">正在加载进度信息...</div>
          </div>
        </el-card>
        <el-alert
          v-else-if="task.status === 'ai_processing'"
          title="AI审核进行中"
          description="系统正在执行AI自动审核，请稍候..."
          type="warning"
          :closable="false"
          show-icon
        />
        <el-alert
          v-else-if="task.status === 'ai_completed'"
          title="AI审核已完成"
          description="AI审核已完成，等待人工审核阶段开始"
          type="success"
          :closable="false"
          show-icon
        />
        <el-alert
          v-else-if="task.status === 'manual_reviewing'"
          title="人工审核进行中"
          description="任务已进入人工审核阶段，审核结果将在审核完成后显示"
          type="warning"
          :closable="false"
          show-icon
        />
        <el-alert
          v-else-if="task.status === 'failed'"
          :title="`审核失败：${task.error_message || '未知错误'}`"
          type="error"
          :closable="false"
          show-icon
        />
        <el-empty v-else description="暂无审核结果" />
      </div>
      <el-empty v-else description="加载中..." />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, View, InfoFilled, Loading, Check, Clock } from '@element-plus/icons-vue'
import api from '@/utils/api'
import ReviewWorkflow from '@/components/ReviewWorkflow.vue'
import ReviewResultDetail from '@/components/ReviewResultDetail.vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()
const currentUser = computed(() => userStore.user)
const isReviewer = computed(() => currentUser.value?.role === 'reviewer')
const canReview = computed(() => {
  if (!isReviewer.value || !task.value || !currentUser.value) return false
  // 检查是否分配给当前用户
  if (task.value.reviewer === currentUser.value.id) return true
  if (task.value.reviewer_assignments && typeof task.value.reviewer_assignments === 'object') {
    const userLevel = currentUser.value.reviewer_level
    if (userLevel && task.value.reviewer_assignments[userLevel] === currentUser.value.id) {
      return true
    }
  }
  return false
})
const showReviewForm = computed(() => {
  return route.query.action === 'review' && canReview.value
})

const loading = ref(false)
const task = ref(null)
const result = ref(null)
const aiSuggestions = ref(null)
const summaryTable = ref(null)
const summarizing = ref(false)
const feedbacking = ref(false)
const resubmitting = ref(false)
const downloading = ref(false)
const submittingReview = ref(false)
const opinionTab = ref('all')
const contractId = ref(null)
let progressPollingInterval = null

// 审核意见表单
const reviewForm = ref({
  opinions: [
    {
      clause_id: '',
      clause_content: '',
      opinion_type: 'suggestion',
      risk_level: 'low',
      opinion_content: '',
      legal_basis: '',
      suggestion: ''
    }
  ]
})

const getRiskType = (level) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'success',
  }
  return types[level] || 'info'
}

const getRiskText = (level) => {
  const texts = {
    high: '高风险',
    medium: '中风险',
    low: '低风险',
  }
  return texts[level] || level
}

const stopProgressPolling = () => {
  if (progressPollingInterval) {
    clearInterval(progressPollingInterval)
    progressPollingInterval = null
  }
}

const startProgressPolling = () => {
  // 如果已经有轮询在运行，先停止
  stopProgressPolling()
  
  // 如果任务正在AI审核中，开始轮询进度
  if (task.value && task.value.status === 'ai_processing') {
    progressPollingInterval = setInterval(async () => {
      try {
        const response = await api.get(`/reviews/tasks/${route.params.id}/`)
        if (response.data) {
          task.value = response.data
          result.value = response.data.result || null
          
          // 如果状态不再是ai_processing，停止轮询
          if (response.data.status !== 'ai_processing') {
            stopProgressPolling()
            // 如果状态变为ai_completed或completed，刷新完整数据
            if (response.data.status === 'ai_completed' || response.data.status === 'completed') {
              await fetchReviewResult()
            }
          }
        }
      } catch (error) {
        console.error('轮询进度失败:', error)
        // 如果出错，停止轮询
        stopProgressPolling()
      }
    }, 2000) // 每2秒轮询一次
  }
}

const fetchReviewResult = async () => {
  loading.value = true
  try {
    const response = await api.get(`/reviews/tasks/${route.params.id}/`)
    task.value = response.data
    result.value = response.data.result || null
    contractId.value = response.data.contract
    
    // 如果是人工审核阶段，且当前用户是审核员，获取AI建议
    if (task.value.status === 'manual_reviewing' && 
        currentUser.value?.role === 'reviewer' && 
        task.value.reviewer_level &&
        result.value?.review_data?.level_suggestions) {
      const levelSuggestions = result.value.review_data.level_suggestions
      aiSuggestions.value = levelSuggestions[task.value.reviewer_level] || null
    }
    
    // 如果状态是ai_processing，启动轮询；否则停止轮询
    if (task.value.status === 'ai_processing') {
      startProgressPolling()
    } else {
      stopProgressPolling()
    }
  } catch (error) {
    console.error('获取审核结果失败:', error)
    ElMessage.error('获取审核结果失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const getLevelLabel = (level) => {
  const labels = {
    level1: '一级审核员',
    level2: '二级审核员',
    level3: '三级审核员（高级）',
  }
  return labels[level] || level
}

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    ai_processing: 'warning',
    ai_completed: 'success',
    manual_reviewing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    ai_processing: 'AI审核中',
    ai_completed: 'AI审核完成',
    manual_reviewing: '人工审核中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const handleSummarizeOpinions = async () => {
  if (!contractId.value) {
    ElMessage.warning('无法获取合同ID')
    return
  }
  
  summarizing.value = true
  try {
    const response = await api.post('/reviews/cycles/summarize_opinions/', {
      contract_id: contractId.value
    })
    
    if (response.data.success) {
      summaryTable.value = response.data.summary_table
      ElMessage.success('意见汇总成功')
    } else {
      ElMessage.error(response.data.error || '意见汇总失败')
    }
  } catch (error) {
    console.error('意见汇总失败:', error)
    ElMessage.error('意见汇总失败')
  } finally {
    summarizing.value = false
  }
}

const handleFeedbackToDrafter = async () => {
  if (!contractId.value) {
    ElMessage.warning('无法获取合同ID')
    return
  }
  
  feedbacking.value = true
  try {
    const response = await api.post('/reviews/cycles/feedback_to_drafter/', {
      contract_id: contractId.value,
      summary_table: summaryTable.value,
      feedback_message: '请根据审核意见修改合同'
    })
    
    if (response.data.success) {
      ElMessage.success('已反馈给起草人')
    } else {
      ElMessage.error(response.data.error || '反馈失败')
    }
  } catch (error) {
    console.error('反馈失败:', error)
    ElMessage.error('反馈失败')
  } finally {
    feedbacking.value = false
  }
}

const handleResubmit = async () => {
  if (!contractId.value) {
    ElMessage.warning('无法获取合同ID')
    return
  }
  
  try {
    await ElMessageBox.prompt('请输入修改摘要', '重新提交审核', {
      confirmButtonText: '提交',
      cancelButtonText: '取消',
      inputPlaceholder: '请简要说明本次修改的内容'
    })
    
    resubmitting.value = true
    try {
      const response = await api.post('/reviews/cycles/resubmit_for_review/', {
        contract_id: contractId.value,
        change_summary: '根据审核意见修改后重新提交'
      })
      
      if (response.data.success) {
        ElMessage.success('已重新提交审核')
        // 可以跳转到新的审核任务
        if (response.data.review_task_id) {
          setTimeout(() => {
            window.location.href = `/reviews/${response.data.review_task_id}`
          }, 1500)
        }
      } else {
        ElMessage.error(response.data.error || '重新提交失败')
      }
    } catch (error) {
      console.error('重新提交失败:', error)
      ElMessage.error('重新提交失败')
    } finally {
      resubmitting.value = false
    }
  } catch (error) {
    // 用户取消
  }
}

const downloadReport = async () => {
  if (!result.value?.report_path) {
    ElMessage.warning('报告文件不存在')
    return
  }
  downloading.value = true
  try {
    const token = localStorage.getItem('token')
    const url = `/api/reviews/results/${result.value.id}/download_report/`
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '')
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('报告下载已开始')
  } catch (error) {
    ElMessage.error('下载失败')
  } finally {
    setTimeout(() => {
      downloading.value = false
    }, 1000)
  }
}

const previewReport = () => {
  if (!result.value?.report_path) {
    ElMessage.warning('报告文件不存在')
    return
  }
  const url = `/api/reviews/results/${result.value.id}/preview_report/`
  window.open(url, '_blank')
}

const addOpinion = () => {
  reviewForm.value.opinions.push({
    clause_id: '',
    clause_content: '',
    opinion_type: 'suggestion',
    risk_level: 'low',
    opinion_content: '',
    legal_basis: '',
    suggestion: ''
  })
}

const removeOpinion = (index) => {
  reviewForm.value.opinions.splice(index, 1)
}

const handleSubmitReview = async () => {
  // 验证至少有一条意见内容
  const hasContent = reviewForm.value.opinions.some(op => op.opinion_content.trim())
  if (!hasContent) {
    ElMessage.warning('请至少填写一条审核意见')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要提交审核意见吗？', '提示', {
      type: 'warning',
    })
    
    submittingReview.value = true
    try {
      await api.post(`/reviews/tasks/${route.params.id}/submit_review/`, {
        opinions: reviewForm.value.opinions
      })
      ElMessage.success('审核意见已提交')
      // 刷新数据
      await fetchReviewResult()
      // 清除审核表单
      reviewForm.value.opinions = [{
        clause_id: '',
        clause_content: '',
        opinion_type: 'suggestion',
        risk_level: 'low',
        opinion_content: '',
        legal_basis: '',
        suggestion: ''
      }]
    } catch (error) {
      const errorMsg = error.response?.data?.error || '提交审核意见失败'
      ElMessage.error(errorMsg)
    } finally {
      submittingReview.value = false
    }
  } catch (error) {
    // 用户取消
  }
}

onMounted(async () => {
  await fetchReviewResult()
})

onUnmounted(() => {
  stopProgressPolling()
})
</script>

<style scoped>
.review-detail {
  padding: 20px;
}
</style>

