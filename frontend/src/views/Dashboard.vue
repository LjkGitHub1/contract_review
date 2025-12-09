<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.contracts }}</div>
              <div class="stat-label">合同总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon><Search /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.reviews }}</div>
              <div class="stat-label">审核任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.risks }}</div>
              <div class="stat-label">风险数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon><Files /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.templates }}</div>
              <div class="stat-label">模板数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>合同状态分布</span>
          </template>
          <v-chart :option="contractStatusChartOption" style="height: 300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>审核任务状态分布</span>
          </template>
          <v-chart :option="reviewStatusChartOption" style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>合同类型分布</span>
          </template>
          <v-chart :option="contractTypeChartOption" style="height: 300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>月度合同趋势</span>
          </template>
          <v-chart :option="monthlyTrendChartOption" style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近合同</span>
          </template>
          <el-table :data="recentContracts" style="width: 100%">
            <el-table-column prop="title" label="合同标题" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>审核任务</span>
          </template>
          <el-table :data="recentReviews" style="width: 100%">
            <el-table-column prop="contract_title" label="合同" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/date'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

const stats = ref({
  contracts: 0,
  reviews: 0,
  risks: 0,
  templates: 0,
})

const recentContracts = ref([])
const recentReviews = ref([])
const contractStatusData = ref({})
const reviewStatusData = ref({})
const contractTypeData = ref({})
const monthlyTrendData = ref([])

const getStatusType = (status) => {
  const types = {
    draft: 'info',
    reviewing: 'warning',
    reviewed: 'success',
    approved: 'success',
    rejected: 'danger',
    signed: 'success',
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    reviewing: '审核中',
    reviewed: '已审核',
    approved: '已批准',
    rejected: '已拒绝',
    signed: '已签署',
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

const contractStatusChartOption = computed(() => {
  const data = Object.entries(contractStatusData.value).map(([name, value]) => ({
    value,
    name: getStatusText(name),
  }))
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '合同状态',
        type: 'pie',
        radius: '50%',
        data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }
})

const reviewStatusChartOption = computed(() => {
  const data = Object.entries(reviewStatusData.value).map(([name, value]) => ({
    value,
    name: getReviewStatusText(name),
  }))
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '审核状态',
        type: 'pie',
        radius: '50%',
        data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }
})

const contractTypeChartOption = computed(() => {
  const data = Object.entries(contractTypeData.value).map(([name, value]) => ({
    value,
    name: getContractTypeText(name),
  }))
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '合同类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '30',
            fontWeight: 'bold',
          },
        },
        labelLine: {
          show: false,
        },
        data,
      },
    ],
  }
})

const monthlyTrendChartOption = computed(() => {
  const months = monthlyTrendData.value.map(item => item.month)
  const values = monthlyTrendData.value.map(item => item.count)
  return {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: months,
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '合同数量',
        type: 'line',
        data: values,
        smooth: true,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' },
            ],
          },
        },
      },
    ],
  }
})

const getContractTypeText = (type) => {
  const types = {
    procurement: '采购合同',
    sales: '销售合同',
    labor: '劳动合同',
    service: '服务合同',
  }
  return types[type] || type
}

const getReviewStatusText = (status) => {
  const texts = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

const fetchData = async () => {
  try {
    // 获取统计数据
    const [contractsRes, reviewsRes, templatesRes] = await Promise.all([
      api.get('/contracts/contracts/', { params: { page_size: 1 } }),
      api.get('/reviews/tasks/', { params: { page_size: 1 } }),
      api.get('/contracts/templates/', { params: { page_size: 1 } }),
    ])

    stats.value.contracts = contractsRes.data.count || 0
    stats.value.reviews = reviewsRes.data.count || 0
    stats.value.templates = templatesRes.data.count || 0

    // 获取所有合同用于统计
    const allContracts = await api.get('/contracts/contracts/', { params: { page_size: 1000 } })
    const contracts = allContracts.data.results || []
    
    // 统计合同状态分布
    contractStatusData.value = {}
    contracts.forEach(contract => {
      contractStatusData.value[contract.status] = (contractStatusData.value[contract.status] || 0) + 1
    })

    // 统计合同类型分布
    contractTypeData.value = {}
    contracts.forEach(contract => {
      contractTypeData.value[contract.contract_type] = (contractTypeData.value[contract.contract_type] || 0) + 1
    })

    // 获取所有审核任务用于统计
    const allReviews = await api.get('/reviews/tasks/', { params: { page_size: 1000 } })
    const reviews = allReviews.data.results || []
    
    // 统计审核状态分布
    reviewStatusData.value = {}
    reviews.forEach(review => {
      reviewStatusData.value[review.status] = (reviewStatusData.value[review.status] || 0) + 1
    })

    // 生成月度趋势数据（模拟数据，实际应从后端获取）
    const now = new Date()
    monthlyTrendData.value = []
    for (let i = 5; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const month = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      const count = contracts.filter(c => {
        const created = new Date(c.created_at)
        return created.getFullYear() === date.getFullYear() && created.getMonth() === date.getMonth()
      }).length
      monthlyTrendData.value.push({ month, count })
    }

    // 获取最近合同
    recentContracts.value = contracts.slice(0, 5)

    // 获取最近审核任务
    recentReviews.value = reviews.slice(0, 5)

    // 统计风险数量（从审核结果中获取）
    stats.value.risks = reviews.filter(r => r.result?.risk_level === 'high').length
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>

