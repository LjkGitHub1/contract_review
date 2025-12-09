<template>
  <div class="review-detail">
    <el-card v-loading="loading">
      <template #header>
        <span>审核详情</span>
      </template>
      <div v-if="result">
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
          <el-descriptions-item label="创建时间">{{ result.created_at }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>审核摘要</el-divider>
        <p>{{ result.summary || '暂无摘要' }}</p>

        <el-divider>
          <el-button
            v-if="result.report_path"
            type="primary"
            @click="downloadReport"
            style="margin-right: 10px"
          >
            下载审核报告
          </el-button>
          <el-button
            v-if="result.report_path"
            type="info"
            @click="previewReport"
          >
            预览报告
          </el-button>
        </el-divider>

        <el-divider>审核意见</el-divider>
        <el-table :data="result.opinions" style="width: 100%">
          <el-table-column prop="opinion_type" label="意见类型" width="120" />
          <el-table-column prop="risk_level" label="风险等级" width="100">
            <template #default="{ row }">
              <el-tag :type="getRiskType(row.risk_level)">{{ getRiskText(row.risk_level) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="opinion_content" label="意见内容" />
          <el-table-column prop="suggestion" label="修改建议" />
        </el-table>
      </div>
      <el-empty v-else description="暂无审核结果" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const route = useRoute()
const loading = ref(false)
const result = ref(null)

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

const fetchReviewResult = async () => {
  loading.value = true
  try {
    const response = await api.get(`/reviews/tasks/${route.params.id}/`)
    result.value = response.data.result
  } catch (error) {
    ElMessage.error('获取审核结果失败')
  } finally {
    loading.value = false
  }
}

const downloadReport = async () => {
  if (!result.value?.report_path) {
    ElMessage.warning('报告文件不存在')
    return
  }
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

onMounted(() => {
  fetchReviewResult()
})
</script>

<style scoped>
.review-detail {
  padding: 20px;
}
</style>

