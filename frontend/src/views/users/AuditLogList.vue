<template>
  <div class="audit-log-list">
    <el-card>
      <template #header>
        <span>操作日志</span>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="操作类型">
          <el-input v-model="searchForm.action" placeholder="请输入操作类型" clearable />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-input v-model="searchForm.resource_type" placeholder="请输入资源类型" clearable />
        </el-form-item>
        <el-form-item label="操作状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="用户">
          <el-input v-model="searchForm.user" placeholder="请输入用户ID" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="logs" v-loading="loading" style="width: 100%">
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="action" label="操作类型" width="150" />
        <el-table-column prop="resource_type" label="资源类型" width="120" />
        <el-table-column prop="resource_id" label="资源ID" width="100" />
        <el-table-column prop="ip_address" label="IP地址" width="130" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">详情</el-button>
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

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="日志详情" width="800px">
      <el-descriptions :column="2" border v-if="currentLog">
        <el-descriptions-item label="用户">{{ currentLog.user_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">{{ currentLog.action }}</el-descriptions-item>
        <el-descriptions-item label="资源类型">{{ currentLog.resource_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="资源ID">{{ currentLog.resource_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ip_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentLog.status === 'success' ? 'success' : 'danger'">
            {{ currentLog.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作时间" :span="2">
          {{ formatDateTime(currentLog.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2" v-if="currentLog.error_message">
          <el-text type="danger">{{ currentLog.error_message }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="请求数据" :span="2" v-if="currentLog.request_data">
          <pre style="max-height: 200px; overflow: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;">
            {{ JSON.stringify(currentLog.request_data, null, 2) }}
          </pre>
        </el-descriptions-item>
        <el-descriptions-item label="响应数据" :span="2" v-if="currentLog.response_data">
          <pre style="max-height: 200px; overflow: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;">
            {{ JSON.stringify(currentLog.response_data, null, 2) }}
          </pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const logs = ref([])
const detailVisible = ref(false)
const currentLog = ref(null)

const searchForm = reactive({
  action: '',
  resource_type: '',
  status: '',
  user: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const fetchLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    
    // 添加搜索条件
    if (searchForm.action) {
      params.action = searchForm.action
    }
    if (searchForm.resource_type) {
      params.resource_type = searchForm.resource_type
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    if (searchForm.user) {
      params.user = searchForm.user
    }
    
    const response = await api.get('/users/audit-logs/', { params })
    logs.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    console.error('获取日志失败:', error)
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchLogs()
}

const handleReset = () => {
  searchForm.action = ''
  searchForm.resource_type = ''
  searchForm.status = ''
  searchForm.user = ''
  pagination.page = 1
  fetchLogs()
}

const handleSizeChange = () => {
  fetchLogs()
}

const handlePageChange = () => {
  fetchLogs()
}

const handleView = async (row) => {
  try {
    const response = await api.get(`/users/audit-logs/${row.id}/`)
    currentLog.value = response.data
    detailVisible.value = true
  } catch (error) {
    console.error('获取日志详情失败:', error)
    ElMessage.error('获取日志详情失败')
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.audit-log-list {
  padding: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

