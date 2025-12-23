<template>
  <div class="rule-match-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>规则匹配记录</span>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent="handleSearch">
        <el-form-item label="审核任务">
          <el-input 
            v-model="searchForm.review_task" 
            placeholder="请输入审核任务ID" 
            clearable 
            @keyup.enter="handleSearch"
            style="min-width: 180px"
          />
        </el-form-item>
        <el-form-item label="规则">
          <el-input 
            v-model="searchForm.rule" 
            placeholder="请输入规则ID" 
            clearable 
            @keyup.enter="handleSearch"
            style="min-width: 180px"
          />
        </el-form-item>
        <el-form-item label="合同ID">
          <el-input 
            v-model="searchForm.contract_id" 
            placeholder="请输入合同ID" 
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

      <el-table :data="matches" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="review_task" label="审核任务ID" width="120" />
        <el-table-column prop="rule_name" label="规则名称" min-width="200" />
        <el-table-column prop="contract_id" label="合同ID" width="120" />
        <el-table-column prop="match_score" label="匹配分数" width="120" sortable="custom">
          <template #default="{ row }">
            <el-tag :type="getScoreType(row.match_score)">
              {{ row.match_score ? parseFloat(row.match_score).toFixed(2) : '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="matched_clause" label="匹配的条款" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.matched_clause">{{ row.matched_clause }}</span>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)">查看详情</el-button>
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

    <!-- 詳情對話框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="规则匹配详情"
      width="800px"
    >
      <el-descriptions :column="2" border v-if="currentMatch">
        <el-descriptions-item label="ID">{{ currentMatch.id }}</el-descriptions-item>
        <el-descriptions-item label="审核任务ID">{{ currentMatch.review_task }}</el-descriptions-item>
        <el-descriptions-item label="规则ID">{{ currentMatch.rule }}</el-descriptions-item>
        <el-descriptions-item label="规则名称">{{ currentMatch.rule_name }}</el-descriptions-item>
        <el-descriptions-item label="合同ID">{{ currentMatch.contract_id }}</el-descriptions-item>
        <el-descriptions-item label="匹配分數">
          <el-tag :type="getScoreType(currentMatch.match_score)">
            {{ currentMatch.match_score ? parseFloat(currentMatch.match_score).toFixed(2) : '-' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">
          {{ formatDateTime(currentMatch.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="匹配的条款" :span="2">
          <div v-if="currentMatch.matched_clause" style="max-height: 150px; overflow-y: auto; padding: 10px; background: #f5f7fa; border-radius: 4px;">
            {{ currentMatch.matched_clause }}
          </div>
          <span v-else style="color: #909399;">-</span>
        </el-descriptions-item>
        <el-descriptions-item label="匹配结果" :span="2">
          <div v-if="currentMatch.match_result" style="max-height: 300px; overflow-y: auto;">
            <pre style="margin: 0; padding: 10px; background: #f5f7fa; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word;">{{ formatJSON(currentMatch.match_result) }}</pre>
          </div>
          <span v-else style="color: #909399;">-</span>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">關閉</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const matches = ref([])
const detailDialogVisible = ref(false)
const currentMatch = ref(null)

const searchForm = reactive({
  review_task: '',
  rule: '',
  contract_id: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const getScoreType = (score) => {
  if (!score) return 'info'
  const numScore = parseFloat(score)
  if (numScore >= 0.8) return 'danger'
  if (numScore >= 0.5) return 'warning'
  return 'success'
}

const formatJSON = (obj) => {
  if (!obj) return ''
  try {
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return String(obj)
  }
}

const fetchMatches = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    
    // 添加過濾參數
    if (searchForm.review_task) {
      params.review_task = searchForm.review_task
    }
    if (searchForm.rule) {
      params.rule = searchForm.rule
    }
    if (searchForm.contract_id) {
      params.contract_id = searchForm.contract_id
    }
    
    const response = await api.get('/rules/matches/', { params })
    matches.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取规则匹配记录失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchMatches()
}

const handleReset = () => {
  searchForm.review_task = ''
  searchForm.rule = ''
  searchForm.contract_id = ''
  handleSearch()
}

const handleSizeChange = () => {
  fetchMatches()
}

const handlePageChange = () => {
  fetchMatches()
}

const handleViewDetail = (row) => {
  currentMatch.value = row
  detailDialogVisible.value = true
}

onMounted(() => {
  fetchMatches()
})
</script>

<style scoped>
.rule-match-list {
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
