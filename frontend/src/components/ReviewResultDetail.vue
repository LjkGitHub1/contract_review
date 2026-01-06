<template>
  <div class="review-result-detail" v-if="result">
    <el-row :gutter="20">
      <!-- 左侧菜单 -->
      <el-col :span="6">
        <el-card shadow="never" class="menu-card">
          <template #header>
            <div class="menu-header">
              <el-icon><List /></el-icon>
              <span>审核结果</span>
            </div>
          </template>
          <el-menu
            :default-active="activeMenu"
            @select="handleMenuSelect"
            class="result-menu"
          >
            <el-menu-item index="overview">
              <el-icon><DataAnalysis /></el-icon>
              <span>审核概览</span>
            </el-menu-item>
            <el-menu-item index="rule_scan">
              <el-icon><Search /></el-icon>
              <span class="menu-item-text">
                <span>规则引擎扫描</span>
                <el-badge
                  v-if="getRuleScanCount() > 0"
                  :value="getRuleScanCount()"
                  class="menu-badge"
                />
              </span>
            </el-menu-item>
            <el-menu-item index="clause_identification">
              <el-icon><Document /></el-icon>
              <span class="menu-item-text">
                <span>条款识别</span>
                <el-badge
                  v-if="getClauseCount() > 0"
                  :value="getClauseCount()"
                  class="menu-badge"
                />
              </span>
            </el-menu-item>
            <el-menu-item index="risk_identification">
              <el-icon><Warning /></el-icon>
              <span class="menu-item-text">
                <span>风险识别</span>
                <el-badge
                  v-if="result.risk_count > 0"
                  :value="result.risk_count"
                  :type="getRiskBadgeType()"
                  class="menu-badge"
                />
              </span>
            </el-menu-item>
            <el-menu-item index="risk_quantification">
              <el-icon><DataAnalysis /></el-icon>
              <span>风险量化分级</span>
            </el-menu-item>
            <el-menu-item index="scoring">
              <el-icon><Star /></el-icon>
              <span>逐条扫描对比评分</span>
            </el-menu-item>
            <el-menu-item index="suggestions">
              <el-icon><Document /></el-icon>
              <span class="menu-item-text">
                <span>修改建议</span>
                <el-badge
                  v-if="getSuggestionsCount() > 0"
                  :value="getSuggestionsCount()"
                  class="menu-badge"
                />
              </span>
            </el-menu-item>
            <el-menu-item index="opinions">
              <el-icon><ChatDotRound /></el-icon>
              <span class="menu-item-text">
                <span>审核意见</span>
                <el-badge
                  v-if="result.opinions && result.opinions.length > 0"
                  :value="result.opinions.length"
                  class="menu-badge"
                />
              </span>
            </el-menu-item>
            <el-menu-item index="legal_basis">
              <el-icon><DocumentCopy /></el-icon>
              <span>法律依据</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <!-- 右侧内容 -->
      <el-col :span="18">
        <el-card shadow="never" class="content-card" v-loading="contentLoading">
          <!-- 审核概览 -->
          <div v-if="activeMenu === 'overview'" class="content-section">
            <h3 class="section-title">审核概览</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="总体评分">
                <el-tag type="success" size="large">{{ result.overall_score }}分</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="风险等级">
                <el-tag :type="getRiskType(result.risk_level)" size="large">
                  {{ getRiskText(result.risk_level) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="风险数量">{{ result.risk_count }}</el-descriptions-item>
              <el-descriptions-item label="审核时间">{{ formatDateTime(result.created_at) }}</el-descriptions-item>
            </el-descriptions>
            <el-divider>审核摘要</el-divider>
            <p class="summary-text">{{ result.summary || '暂无摘要' }}</p>
          </div>

          <!-- 规则引擎扫描 -->
          <div v-else-if="activeMenu === 'rule_scan'" class="content-section">
            <h3 class="section-title">规则引擎扫描结果</h3>
            <div v-if="ruleScanData">
              <el-descriptions :column="2" border style="margin-bottom: 20px">
                <el-descriptions-item label="匹配规则数">
                  {{ ruleScanData.matches?.length || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="总体评分">
                  <el-tag type="success">{{ ruleScanData.overall_score || 0 }}分</el-tag>
                </el-descriptions-item>
              </el-descriptions>
              <el-table :data="ruleScanData.matches || []" border>
                <el-table-column prop="rule_name" label="规则名称" width="200" />
                <el-table-column prop="rule_type" label="规则类型" width="120">
                  <template #default="{ row }">
                    {{ getRuleTypeText(row.rule_type) }}
                  </template>
                </el-table-column>
                <el-table-column prop="match_content" label="匹配内容" />
                <el-table-column prop="score" label="评分" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getScoreType(row.score)">{{ row.score }}分</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="legal_basis" label="法律依据" />
              </el-table>
            </div>
            <el-empty v-else description="暂无规则扫描数据" />
          </div>

          <!-- 条款识别 -->
          <div v-else-if="activeMenu === 'clause_identification'" class="content-section">
            <h3 class="section-title">条款识别结果</h3>
            <div v-if="clauseData && clauseData.clauses">
              <el-descriptions :column="2" border style="margin-bottom: 20px">
                <el-descriptions-item label="识别条款数">
                  {{ clauseData.clauses?.length || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="关键条款数">
                  {{ getKeyClausesCount() }}
                </el-descriptions-item>
              </el-descriptions>
              <el-table :data="clauseData.clauses || []" border>
                <el-table-column prop="clause_type" label="条款类型" width="150">
                  <template #default="{ row }">
                    <el-tag>{{ getClauseTypeText(row.clause_type) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="clause_content" label="条款内容" />
                <el-table-column prop="is_key" label="是否关键" width="100">
                  <template #default="{ row }">
                    <el-tag v-if="row.is_key" type="warning">关键</el-tag>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="confidence" label="置信度" width="100">
                  <template #default="{ row }">
                    {{ (row.confidence * 100).toFixed(1) }}%
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty v-else description="暂无条款识别数据" />
          </div>

          <!-- 风险识别 -->
          <div v-else-if="activeMenu === 'risk_identification'" class="content-section">
            <h3 class="section-title">风险识别结果</h3>
            <div v-if="riskData && riskData.risks">
              <el-descriptions :column="2" border style="margin-bottom: 20px">
                <el-descriptions-item label="风险总数">
                  {{ riskData.risks?.length || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="高风险">
                  <el-tag type="danger">{{ getRiskCountByLevel('high') }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="中风险">
                  <el-tag type="warning">{{ getRiskCountByLevel('medium') }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="低风险">
                  <el-tag type="success">{{ getRiskCountByLevel('low') }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
              <el-table :data="riskData.risks || []" border>
                <el-table-column prop="risk_type" label="风险类型" width="150">
                  <template #default="{ row }">
                    {{ getRiskTypeText(row.risk_type) }}
                  </template>
                </el-table-column>
                <el-table-column prop="risk_category" label="风险分类" width="120">
                  <template #default="{ row }">
                    {{ getRiskCategoryText(row.risk_category) }}
                  </template>
                </el-table-column>
                <el-table-column prop="risk_level" label="风险等级" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getRiskType(row.risk_level)">
                      {{ getRiskText(row.risk_level) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="risk_description" label="风险描述" />
                <el-table-column prop="risk_location" label="风险位置" width="150" />
              </el-table>
            </div>
            <el-empty v-else description="暂无风险识别数据" />
          </div>

          <!-- 风险量化分级 -->
          <div v-else-if="activeMenu === 'risk_quantification'" class="content-section">
            <h3 class="section-title">风险量化分级结果</h3>
            <div v-if="riskQuantData">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="总体风险等级">
                  <el-tag :type="getRiskType(riskQuantData.overall_risk_level)" size="large">
                    {{ getRiskText(riskQuantData.overall_risk_level) }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="风险分数">
                  <el-tag type="info" size="large">{{ riskQuantData.risk_score || 0 }}分</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="高风险数量">
                  <el-tag type="danger">{{ riskQuantData.high_risk_count || 0 }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="中风险数量">
                  <el-tag type="warning">{{ riskQuantData.medium_risk_count || 0 }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="低风险数量">
                  <el-tag type="success">{{ riskQuantData.low_risk_count || 0 }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="风险分布">
                  <div class="risk-distribution">
                    <el-progress
                      :percentage="getRiskPercentage('high')"
                      :color="getRiskColor('high')"
                      :stroke-width="20"
                    />
                    <el-progress
                      :percentage="getRiskPercentage('medium')"
                      :color="getRiskColor('medium')"
                      :stroke-width="20"
                    />
                    <el-progress
                      :percentage="getRiskPercentage('low')"
                      :color="getRiskColor('low')"
                      :stroke-width="20"
                    />
                  </div>
                </el-descriptions-item>
              </el-descriptions>
            </div>
            <el-empty v-else description="暂无风险量化数据" />
          </div>

          <!-- 逐条扫描对比评分 -->
          <div v-else-if="activeMenu === 'scoring'" class="content-section">
            <h3 class="section-title">逐条扫描对比评分结果</h3>
            <div v-if="scoringData && scoringData.clause_scores">
              <el-descriptions :column="2" border style="margin-bottom: 20px">
                <el-descriptions-item label="评分条款数">
                  {{ scoringData.clause_scores?.length || 0 }}
                </el-descriptions-item>
                <el-descriptions-item label="平均分">
                  <el-tag type="success">{{ getAverageScore() }}分</el-tag>
                </el-descriptions-item>
              </el-descriptions>
              <el-table :data="scoringData.clause_scores || []" border>
                <el-table-column prop="clause_type" label="条款类型" width="150" />
                <el-table-column prop="clause_content" label="条款内容" />
                <el-table-column prop="score" label="评分" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getScoreType(row.score)">{{ row.score }}分</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="matched_rules" label="匹配规则数" width="120">
                  <template #default="{ row }">
                    {{ row.matched_rules?.length || 0 }}
                  </template>
                </el-table-column>
                <el-table-column prop="comments" label="评语" />
              </el-table>
            </div>
            <el-empty v-else description="暂无评分数据" />
          </div>

          <!-- 修改建议 -->
          <div v-else-if="activeMenu === 'suggestions'" class="content-section">
            <h3 class="section-title">修改建议</h3>
            <div v-if="suggestionsData && suggestionsData.length > 0">
              <el-table :data="suggestionsData" border>
                <el-table-column prop="type" label="建议类型" width="150">
                  <template #default="{ row }">
                    <el-tag>{{ getSuggestionTypeText(row.type) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="priority" label="优先级" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getPriorityType(row.priority)">
                      {{ getPriorityText(row.priority) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="问题描述" />
                <el-table-column prop="suggestion" label="修改建议" />
              </el-table>
            </div>
            <el-empty v-else description="暂无修改建议" />
          </div>

          <!-- 审核意见 -->
          <div v-else-if="activeMenu === 'opinions'" class="content-section">
            <h3 class="section-title">审核意见</h3>
            <div v-if="result.opinions && result.opinions.length > 0">
              <el-table :data="result.opinions" border>
                <el-table-column prop="opinion_type" label="意见类型" width="120">
                  <template #default="{ row }">
                    {{ getOpinionTypeText(row.opinion_type) }}
                  </template>
                </el-table-column>
                <el-table-column prop="risk_level" label="风险等级" width="100">
                  <template #default="{ row }">
                    <el-tag v-if="row.risk_level" :type="getRiskType(row.risk_level)">
                      {{ getRiskText(row.risk_level) }}
                    </el-tag>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="opinion_content" label="意见内容" />
                <el-table-column prop="suggestion" label="修改建议" />
                <el-table-column prop="legal_basis" label="法律依据" />
              </el-table>
            </div>
            <el-empty v-else description="暂无审核意见" />
          </div>

          <!-- 法律依据 -->
          <div v-else-if="activeMenu === 'legal_basis'" class="content-section">
            <h3 class="section-title">法律依据</h3>
            <div v-if="legalBasisData && legalBasisData.length > 0">
              <el-card
                v-for="(basis, index) in legalBasisData"
                :key="index"
                shadow="hover"
                style="margin-bottom: 15px"
              >
                <p class="legal-basis-text">{{ basis }}</p>
              </el-card>
            </div>
            <el-empty v-else description="暂无法律依据" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  List,
  DataAnalysis,
  Search,
  Document,
  Warning,
  Star,
  ChatDotRound,
  DocumentCopy
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'

const props = defineProps({
  result: {
    type: Object,
    required: true
  }
})

const activeMenu = ref('overview')
const contentLoading = ref(false)

// 从 review_data 中提取各个部分的数据
const reviewData = computed(() => props.result?.review_data || {})
const detailedData = computed(() => reviewData.value?.detailed_data || {})

const ruleScanData = computed(() => detailedData.value?.rule_scan_result)
const clauseData = computed(() => detailedData.value?.clause_identification_result)
const riskData = computed(() => detailedData.value?.risk_identification_result)
const riskQuantData = computed(() => detailedData.value?.risk_quantification_result)
const scoringData = computed(() => detailedData.value?.scoring_result)
const suggestionsData = computed(() => reviewData.value?.modification_suggestions || [])
const legalBasisData = computed(() => reviewData.value?.legal_basis || [])

const handleMenuSelect = (key) => {
  // 切换菜单时显示加载效果
  contentLoading.value = true
  activeMenu.value = key
  // 模拟加载，实际场景中可以根据数据加载情况调整
  setTimeout(() => {
    contentLoading.value = false
  }, 200)
}

// 获取规则扫描数量
const getRuleScanCount = () => {
  return ruleScanData.value?.matches?.length || 0
}

// 获取条款数量
const getClauseCount = () => {
  return clauseData.value?.clauses?.length || 0
}

// 获取关键条款数量
const getKeyClausesCount = () => {
  if (!clauseData.value?.clauses) return 0
  return clauseData.value.clauses.filter(c => c.is_key).length
}

// 获取修改建议数量
const getSuggestionsCount = () => {
  return suggestionsData.value?.length || 0
}

// 获取风险数量（按等级）
const getRiskCountByLevel = (level) => {
  if (!riskData.value?.risks) return 0
  return riskData.value.risks.filter(r => r.risk_level === level).length
}

// 获取风险百分比
const getRiskPercentage = (level) => {
  if (!riskQuantData.value) return 0
  const total = (riskQuantData.value.high_risk_count || 0) +
                (riskQuantData.value.medium_risk_count || 0) +
                (riskQuantData.value.low_risk_count || 0)
  if (total === 0) return 0
  const count = riskQuantData.value[`${level}_risk_count`] || 0
  return Math.round((count / total) * 100)
}

// 获取风险颜色
const getRiskColor = (level) => {
  const colors = {
    high: '#f56c6c',
    medium: '#e6a23c',
    low: '#67c23a'
  }
  return colors[level] || '#909399'
}

// 获取平均分
const getAverageScore = () => {
  if (!scoringData.value?.clause_scores) return 0
  const scores = scoringData.value.clause_scores
  if (scores.length === 0) return 0
  const sum = scores.reduce((acc, item) => acc + (item.score || 0), 0)
  return (sum / scores.length).toFixed(1)
}

// 获取风险徽章类型
const getRiskBadgeType = () => {
  if (props.result.risk_level === 'high') return 'danger'
  if (props.result.risk_level === 'medium') return 'warning'
  return 'success'
}

// 工具函数
const getRiskType = (level) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return types[level] || 'info'
}

const getRiskText = (level) => {
  const texts = {
    high: '高风险',
    medium: '中风险',
    low: '低风险'
  }
  return texts[level] || level
}

const getRuleTypeText = (type) => {
  const texts = {
    general: '通用规则',
    industry: '行业规则',
    enterprise: '企业规则'
  }
  return texts[type] || type
}

const getClauseTypeText = (type) => {
  const texts = {
    subject: '主体',
    object: '标的',
    term: '期限',
    responsibility: '责任',
    payment: '付款',
    breach: '违约责任',
    dispute: '争议解决'
  }
  return texts[type] || type
}

const getRiskTypeText = (type) => {
  const texts = {
    invalid: '无效条款',
    missing: '缺失条款',
    illegal: '违法条款',
    non_compliant: '不合规条款'
  }
  return texts[type] || type
}

const getRiskCategoryText = (category) => {
  const texts = {
    legality: '合法性',
    compliance: '合规性',
    completeness: '完整性',
    financial: '财务风险'
  }
  return texts[category] || category
}

const getScoreType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const getSuggestionTypeText = (type) => {
  const texts = {
    risk_suggestion: '风险建议',
    clause_suggestion: '条款建议',
    format_suggestion: '格式建议'
  }
  return texts[type] || type
}

const getPriorityType = (priority) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || priority
}

const getOpinionTypeText = (type) => {
  const texts = {
    risk: '风险',
    suggestion: '建议',
    warning: '警告'
  }
  return texts[type] || type
}
</script>

<style scoped>
.review-result-detail {
  margin-top: 20px;
}

.menu-card {
  height: 100%;
}

.menu-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.result-menu {
  border-right: none;
}

.menu-badge {
  margin-left: auto;
}

.content-card {
  min-height: 600px;
}

.content-section {
  padding: 10px;
}

.section-title {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.summary-text {
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}

.risk-distribution {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legal-basis-text {
  line-height: 1.8;
  color: #606266;
  margin: 0;
}

:deep(.el-menu-item) {
  position: relative;
  display: flex !important;
  align-items: center !important;
  height: 56px;
}

:deep(.el-menu-item > .el-icon) {
  margin-right: 8px;
  flex-shrink: 0;
}

.menu-item-text {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  width: 100%;
  flex: 1;
  height: 100%;
}

:deep(.el-menu-item .menu-badge) {
  margin-left: auto;
  margin-right: 10px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
}

:deep(.el-menu-item .el-badge) {
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
}

:deep(.el-menu-item .el-badge__content) {
  position: static;
  transform: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
}
</style>

