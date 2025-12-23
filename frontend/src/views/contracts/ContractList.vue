<template>
  <div class="contract-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>合同列表</span>
          <el-button type="primary" @click="$router.push('/contracts/create')">
            <el-icon><Plus /></el-icon>
            新建合同
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent="handleSearch">
        <el-form-item label="合同类型">
          <el-select 
            v-model="searchForm.contract_type" 
            placeholder="请选择" 
            clearable 
            filterable
            style="min-width: 180px"
            @change="handleSearch"
          >
            <el-option label="采购合同" value="procurement" />
            <el-option label="销售合同" value="sales" />
            <el-option label="劳动合同" value="labor" />
            <el-option label="服务合同" value="service" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="请选择" 
            clearable 
            filterable
            style="min-width: 180px"
            @change="handleSearch"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="审核中" value="reviewing" />
            <el-option label="已审核" value="reviewed" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已签署" value="signed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="contracts" v-loading="loading" style="width: 100%">
        <el-table-column prop="contract_no" label="合同编号" width="180" />
        <el-table-column prop="title" label="合同标题" />
        <el-table-column prop="contract_type" label="合同类型" width="120">
          <template #default="{ row }">
            {{ getContractTypeText(row.contract_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="drafter_name" label="起草人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleReview(row)">审核</el-button>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/date'

const router = useRouter()
const loading = ref(false)
const contracts = ref([])

const searchForm = reactive({
  contract_type: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
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

const getStatusType = (status) => {
  const types = {
    draft: 'info',
    reviewing: 'warning',
    reviewed: 'success',
    approved: 'success',
    rejected: 'danger',
    signed: 'success',
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
  }
  return texts[status] || status
}

const fetchContracts = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    }
    const response = await api.get('/contracts/contracts/', { params })
    contracts.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取合同列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchContracts()
}

const handleReset = () => {
  searchForm.contract_type = ''
  searchForm.status = ''
  handleSearch()
}

const handleSizeChange = () => {
  fetchContracts()
}

const handlePageChange = () => {
  fetchContracts()
}

const handleView = (row) => {
  router.push(`/contracts/${row.id}`)
}

const handleEdit = (row) => {
  router.push(`/contracts/${row.id}?edit=true`)
}

const handleReview = (row) => {
  router.push(`/reviews?contract_id=${row.id}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该合同吗？', '提示', {
      type: 'warning',
    })
    await api.delete(`/contracts/contracts/${row.id}/`)
    ElMessage.success('删除成功')
    fetchContracts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchContracts()
})
</script>

<style scoped>
.contract-list {
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

