<template>
  <div class="review-workflow">
    <!-- AI审核阶段 -->
    <el-card shadow="never" v-if="status === 'ai_processing' || status === 'ai_completed' || status === 'pending' || status === 'processing'">
      <template #header>
        <div class="workflow-header">
          <span class="workflow-title">
            <el-icon><Document /></el-icon>
            AI自动审核阶段
          </span>
          <el-tag :type="getStatusType(status)" size="small">{{ getStatusText(status) }}</el-tag>
        </div>
      </template>
      
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step
          v-for="(step, index) in autoSteps"
          :key="index"
          :title="step.title"
          :description="step.description"
          :status="getStepStatus(index)"
        >
          <template #icon>
            <el-icon v-if="getStepStatus(index) === 'success'"><CircleCheck /></el-icon>
            <el-icon v-else-if="getStepStatus(index) === 'process'"><Loading /></el-icon>
            <el-icon v-else-if="getStepStatus(index) === 'error'"><CircleClose /></el-icon>
            <el-icon v-else><InfoFilled /></el-icon>
          </template>
        </el-step>
      </el-steps>
      
      <div v-if="status === 'ai_processing' || status === 'processing'" class="processing-info">
        <el-alert
          :title="`当前正在执行：${autoSteps[currentStep]?.title || 'AI审核中'}`"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
      
      <div v-if="status === 'ai_completed'" class="processing-info">
        <el-alert
          title="AI审核已完成，等待人工审核"
          type="success"
          :closable="false"
          show-icon
        />
      </div>
      
      <div v-if="status === 'failed' && errorMessage" class="error-info">
        <el-alert
          :title="`审核失败：${errorMessage}`"
          type="error"
          :closable="false"
          show-icon
        />
      </div>
    </el-card>

    <!-- 人工审核阶段 -->
    <el-card shadow="never" v-if="status === 'manual_reviewing' || status === 'completed' || (status === 'processing' && reviewerLevel)">
      <template #header>
        <div class="workflow-header">
          <span class="workflow-title">
            <el-icon><User /></el-icon>
            人工审核流程（多级审核）
          </span>
          <el-tag :type="getStatusType(status)" size="small">{{ getStatusText(status) }}</el-tag>
        </div>
      </template>
      
      <el-timeline>
        <el-timeline-item
          v-for="(step, index) in manualSteps"
          :key="index"
          :timestamp="step.timestamp || ''"
          :type="getTimelineType(index)"
          placement="top"
        >
          <template #icon>
            <el-icon>
              <CircleClose v-if="getTimelineIcon(index) === 'CircleClose'" />
              <CircleCheck v-else-if="getTimelineIcon(index) === 'CircleCheck'" />
              <Loading v-else-if="getTimelineIcon(index) === 'Loading'" />
              <InfoFilled v-else />
            </el-icon>
          </template>
          <el-card shadow="hover">
            <div class="timeline-step">
              <div class="step-header">
                <h4>{{ step.title }}</h4>
                <div style="display: flex; align-items: center; gap: 10px">
                  <el-tag v-if="isAdmin && step.reviewer" type="info" size="small">
                    <el-icon style="margin-right: 4px"><User /></el-icon>
                    {{ step.reviewer.real_name || step.reviewer.username }}
                  </el-tag>
                  <el-tag :type="getStepTagType(index)" size="small">
                    {{ getStepTagText(index) }}
                  </el-tag>
                </div>
              </div>
              <p class="step-description">{{ step.description }}</p>
              <div v-if="step.details" class="step-details">
                <el-descriptions :column="2" size="small" border>
                  <el-descriptions-item
                    v-for="(detail, key) in step.details"
                    :key="key"
                    :label="key"
                  >
                    {{ detail }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      
      <div v-if="status === 'processing'" class="processing-info">
        <el-alert
          :title="`当前审核层级：${getCurrentReviewLevel()}`"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Document, User, CircleCheck, CircleClose, InfoFilled, Loading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const currentUser = computed(() => userStore.user)
const isAdmin = computed(() => currentUser.value?.role === 'admin')
const currentUserId = computed(() => currentUser.value?.id)

const props = defineProps({
  status: {
    type: String,
    required: true,
    default: 'pending'
  },
  reviewerLevel: {
    type: String,
    default: null
  },
  reviewLevels: {
    type: Array,
    default: () => ['level1', 'level2', 'level3']
  },
  reviewerAssignments: {
    type: Object,
    default: () => ({})
  },
  reviewerAssignmentsDetail: {
    type: Object,
    default: () => ({})
  },
  startedAt: {
    type: String,
    default: null
  },
  completedAt: {
    type: String,
    default: null
  },
  errorMessage: {
    type: String,
    default: ''
  }
})

// 自动审核流程步骤
const autoSteps = [
  { title: '规则引擎扫描', description: '匹配通用/行业/企业规则' },
  { title: '大模型语义理解', description: 'AI进行语义分析和理解' },
  { title: '条款识别', description: '识别关键条款（主体、标的、期限等）' },
  { title: '风险识别', description: '多维度风险识别（合法性、合规性、完整性、财务风险）' },
  { title: '风险量化分级', description: '计算风险分数和风险等级' },
  { title: '逐条扫描对比评分', description: '逐条扫描合同条款，与规则库对比评分' },
  { title: '输出修改建议', description: '生成可执行的修改建议' },
  { title: '生成审核报告', description: '生成包含合同信息、风险概览、修改建议、法律依据的审核报告' }
]

// 人工审核流程步骤
const manualSteps = computed(() => {
  const levelConfig = {
    level1: {
      title: '一级审核员审核',
      description: '重点：格式规范、基础条款完整性、基本信息准确性',
      focus: '格式规范、基础条款完整性、基本信息准确性'
    },
    level2: {
      title: '二级审核员审核',
      description: '重点：法律合规性、风险识别、条款合理性、权利义务平衡',
      focus: '法律合规性、风险识别、条款合理性、权利义务平衡'
    },
    level3: {
      title: '三级审核员审核（高级）',
      description: '重点：重大风险、战略层面、商业决策、最终批准',
      focus: '重大风险、战略层面、商业决策、最终批准'
    }
  }
  
  const steps = [
    {
      title: '分配审核任务',
      description: '根据配置的审核层级分配任务',
      timestamp: props.startedAt || '',
      level: null,
      reviewer: null
    }
  ]
  
  // 根据配置的审核层级动态生成步骤
  const configuredLevels = props.reviewLevels || ['level1', 'level2', 'level3']
  const levelOrder = ['level1', 'level2', 'level3']
  
  levelOrder.forEach((level) => {
    if (configuredLevels.includes(level)) {
      const config = levelConfig[level]
      
      // 获取该层级对应的审核员信息
      const reviewerDetail = props.reviewerAssignmentsDetail?.[level] || null
      const reviewerId = props.reviewerAssignments?.[level] || null
      
      // 判断当前用户是否有权限查看此节点
      let canView = false
      if (isAdmin.value) {
        // 管理员可以查看所有节点
        canView = true
      } else if (currentUser.value?.role === 'reviewer') {
        // 审核员只能查看分配给自己的节点
        if (reviewerId === currentUserId.value) {
          canView = true
        } else {
          // 审核员没有权限查看此节点，跳过
          return
        }
      } else {
        // 其他角色（如起草人）不能查看审核节点
        return
      }
      
      const details = {}
      if (props.reviewerLevel === level) {
        details['审核重点'] = config.focus
        details['AI辅助'] = '基于审核重点配置生成针对性建议'
      }
      
      // 如果是管理员，显示审核员信息
      if (isAdmin.value && reviewerDetail) {
        details['审核员'] = reviewerDetail.real_name || reviewerDetail.username
        details['邮箱'] = reviewerDetail.email
      }
      
      steps.push({
        title: config.title,
        description: config.description,
        timestamp: props.reviewerLevel === level ? '进行中' : '',
        level: level,
        reviewer: reviewerDetail,
        reviewerId: reviewerId,
        canView: canView,
        details: Object.keys(details).length > 0 ? details : null
      })
    }
  })
  
  // 添加审核意见闭环步骤（所有人都可以看到）
  steps.push({
    title: '审核意见闭环',
    description: '汇总审核意见、反馈给起草人、修改后重新提交',
    timestamp: props.completedAt || '',
    level: null,
    reviewer: null,
    canView: true
  })
  
  return steps
})

// 计算当前步骤（AI审核）
const currentStep = computed(() => {
  const status = props.status
  if (status === 'pending') return 0
  if (status === 'failed') return -1
  if (status === 'ai_completed' || status === 'manual_reviewing' || status === 'completed') {
    return autoSteps.length - 1
  }
  if (status === 'ai_processing' || status === 'processing') {
    // AI处理中时，显示为进行中
    return 0
  }
  return 0
})

// 获取步骤状态（AI审核）
const getStepStatus = (index) => {
  const status = props.status
  if (status === 'failed') {
    return index <= currentStep.value ? 'error' : 'wait'
  }
  if (status === 'ai_completed' || status === 'manual_reviewing' || status === 'completed') {
    return 'success'
  }
  if (status === 'ai_processing' || status === 'processing') {
    if (index < currentStep.value) return 'success'
    if (index === currentStep.value) return 'process'
    return 'wait'
  }
  return 'wait'
}

// 获取时间线类型（人工审核）
const getTimelineType = (index) => {
  if (props.status === 'failed') return 'danger'
  const step = manualSteps.value[index]
  if (props.status === 'completed' && step && step.title === '审核意见闭环') return 'success'
  if (props.status === 'processing') {
    if (step && step.level === props.reviewerLevel) return 'primary'
    if (index < getCurrentStepIndex()) return 'success'
  }
  return 'info'
}

// 获取时间线图标（人工审核）
const getTimelineIcon = (index) => {
  if (props.status === 'failed') return 'CircleClose'
  const step = manualSteps.value[index]
  if (props.status === 'completed' && step && step.title === '审核意见闭环') return 'CircleCheck'
  if (props.status === 'processing') {
    if (step && step.level === props.reviewerLevel) return 'Loading'
    if (index < getCurrentStepIndex()) return 'CircleCheck'
  }
  return 'InfoFilled'
}

// 获取当前步骤索引（人工审核）
const getCurrentStepIndex = () => {
  if (!props.reviewerLevel) return 0
  const index = manualSteps.value.findIndex(step => step.level === props.reviewerLevel)
  if (index !== -1) return index
  if (props.status === 'completed') return manualSteps.value.length - 1
  return 0
}

// 获取步骤标签类型（人工审核）
const getStepTagType = (index) => {
  if (props.status === 'failed') return 'danger'
  const step = manualSteps.value[index]
  if (props.status === 'completed' && step && step.title === '审核意见闭环') return 'success'
  if (props.status === 'processing') {
    if (step && step.level === props.reviewerLevel) return 'warning'
    if (index < getCurrentStepIndex()) return 'success'
  }
  return 'info'
}

// 获取步骤标签文本（人工审核）
const getStepTagText = (index) => {
  if (props.status === 'failed') return '失败'
  const step = manualSteps.value[index]
  if (props.status === 'completed' && step && step.title === '审核意见闭环') return '已完成'
  if (props.status === 'processing') {
    if (step && step.level === props.reviewerLevel) return '进行中'
    if (index < getCurrentStepIndex()) return '已完成'
  }
  return '待处理'
}

// 获取当前审核层级文本
const getCurrentReviewLevel = () => {
  const levelMap = {
    level1: '一级审核员',
    level2: '二级审核员',
    level3: '三级审核员（高级）'
  }
  return levelMap[props.reviewerLevel] || '待分配'
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    pending: 'info',
    processing: 'warning', // 向后兼容旧状态
    ai_processing: 'warning',
    ai_completed: 'success',
    manual_reviewing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    processing: '处理中', // 向后兼容旧状态
    ai_processing: 'AI审核中',
    ai_completed: 'AI审核完成',
    manual_reviewing: '人工审核中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}
</script>

<style scoped>
.review-workflow {
  margin-bottom: 20px;
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.workflow-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.processing-info,
.error-info {
  margin-top: 20px;
}

.timeline-step {
  padding: 10px 0;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.step-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.step-description {
  margin: 10px 0;
  color: #606266;
  line-height: 1.6;
}

.step-details {
  margin-top: 15px;
}

:deep(.el-steps) {
  padding: 20px 0;
}

:deep(.el-step__title) {
  font-size: 14px;
  font-weight: 500;
}

:deep(.el-step__description) {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  font-size: 13px;
}
</style>

