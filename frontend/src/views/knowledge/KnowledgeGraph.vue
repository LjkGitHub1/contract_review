<template>
  <div class="knowledge-graph">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识图谱</span>
          <el-button type="primary" @click="refreshGraph">刷新图谱</el-button>
        </div>
      </template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="知识图谱可视化" name="graph">
          <div class="graph-container">
            <v-chart :option="graphOption" style="height: 600px" v-loading="graphLoading" />
          </div>
        </el-tab-pane>
        <el-tab-pane label="实体列表" name="entities">
          <el-table :data="entities" v-loading="loading" style="width: 100%">
            <el-table-column prop="entity_name" label="实体名称" />
            <el-table-column prop="entity_type" label="实体类型" width="120" />
            <el-table-column prop="entity_code" label="实体编码" width="150" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="法律法规" name="regulations">
          <el-table :data="regulations" v-loading="loading" style="width: 100%">
            <el-table-column prop="title" label="法规标题" />
            <el-table-column prop="regulation_no" label="法规编号" width="150" />
            <el-table-column prop="regulation_type" label="法规类型" width="120" />
            <el-table-column prop="publish_date" label="发布日期" width="120" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="案例库" name="cases">
          <el-table :data="cases" v-loading="loading" style="width: 100%">
            <el-table-column prop="case_title" label="案例标题" />
            <el-table-column prop="case_no" label="案例编号" width="150" />
            <el-table-column prop="court" label="审理法院" width="200" />
            <el-table-column prop="judge_date" label="判决日期" width="120" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GraphChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

use([
  CanvasRenderer,
  GraphChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
])

const loading = ref(false)
const graphLoading = ref(false)
const activeTab = ref('graph')
const entities = ref([])
const regulations = ref([])
const cases = ref([])
const relations = ref([])

const fetchEntities = async () => {
  try {
    const response = await api.get('/knowledge/entities/')
    entities.value = response.data.results || []
  } catch (error) {
    ElMessage.error('获取实体列表失败')
  }
}

const fetchRegulations = async () => {
  try {
    const response = await api.get('/knowledge/regulations/')
    regulations.value = response.data.results || []
  } catch (error) {
    ElMessage.error('获取法律法规列表失败')
  }
}

const fetchCases = async () => {
  try {
    const response = await api.get('/knowledge/cases/')
    cases.value = response.data.results || []
  } catch (error) {
    ElMessage.error('获取案例列表失败')
  }
}

const fetchRelations = async () => {
  try {
    const response = await api.get('/knowledge/relations/')
    relations.value = response.data.results || []
  } catch (error) {
    console.error('获取关系列表失败', error)
    relations.value = []
  }
}

const graphOption = computed(() => {
  // 构建节点数据
  const nodes = entities.value.map(entity => ({
    id: entity.id,
    name: entity.entity_name,
    category: entity.entity_type || '其他',
    symbolSize: 30,
    value: entity.entity_name,
  }))

  // 构建边数据
  const links = relations.value.map(relation => ({
    source: relation.source_entity_id,
    target: relation.target_entity_id,
    value: relation.relation_type,
    label: {
      show: true,
      formatter: relation.relation_type,
    },
  }))

  // 按类型分组节点
  const categories = [...new Set(entities.value.map(e => e.entity_type || '其他'))].map(type => ({
    name: type,
  }))

  return {
    title: {
      text: '知识图谱',
      top: 'top',
      left: 'center',
    },
    tooltip: {
      formatter: (params) => {
        if (params.dataType === 'node') {
          return `${params.data.name}<br/>类型: ${params.data.category}`
        } else {
          return `${params.data.source} → ${params.data.target}<br/>关系: ${params.data.value}`
        }
      },
    },
    legend: {
      data: categories.map(c => c.name),
      orient: 'vertical',
      left: 'left',
      top: 'middle',
    },
    series: [
      {
        name: '知识图谱',
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: links,
        categories: categories,
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
        },
        labelLayout: {
          hideOverlap: true,
        },
        scaleLimit: {
          min: 0.4,
          max: 2,
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3,
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 10,
          },
        },
        force: {
          repulsion: 1000,
          gravity: 0.1,
          edgeLength: 200,
          layoutAnimation: true,
        },
      },
    ],
  }
})

const refreshGraph = async () => {
  graphLoading.value = true
  try {
    await Promise.all([fetchEntities(), fetchRelations()])
    ElMessage.success('图谱已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    graphLoading.value = false
  }
}

onMounted(() => {
  fetchEntities()
  fetchRegulations()
  fetchCases()
  fetchRelations()
})
</script>

<style scoped>
.knowledge-graph {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.graph-container {
  width: 100%;
  min-height: 600px;
}
</style>

