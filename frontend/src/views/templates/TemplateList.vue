<template>
  <div class="template-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模板列表</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建模板
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="合同类型">
          <el-select v-model="searchForm.contract_type" placeholder="请选择" clearable>
            <el-option label="采购合同" value="procurement" />
            <el-option label="销售合同" value="sales" />
            <el-option label="劳动合同" value="labor" />
            <el-option label="服务合同" value="service" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否公开">
          <el-select v-model="searchForm.is_public" placeholder="请选择" clearable>
            <el-option label="公开" :value="true" />
            <el-option label="私有" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="templates" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="模板名称" />
        <el-table-column prop="contract_type" label="合同类型" width="120">
          <template #default="{ row }">
            {{ getContractTypeText(row.contract_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="industry" label="适用行业" width="120" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="usage_count" label="使用次数" width="100" />
        <el-table-column prop="is_public" label="是否公开" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'">
              {{ row.is_public ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleUse(row)">使用</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
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

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="合同类型" prop="contract_type">
          <el-select v-model="formData.contract_type" placeholder="请选择合同类型" style="width: 100%">
            <el-option label="采购合同" value="procurement" />
            <el-option label="销售合同" value="sales" />
            <el-option label="劳动合同" value="labor" />
            <el-option label="服务合同" value="service" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用行业" prop="industry">
          <el-input v-model="formData.industry" placeholder="如：制造业、金融业等" />
        </el-form-item>
        <el-form-item label="模板分类" prop="category">
          <el-input v-model="formData.category" placeholder="如：标准模板、定制模板等" />
        </el-form-item>
        <el-form-item label="模板内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="10"
            placeholder="请输入模板内容"
          />
        </el-form-item>
        <el-form-item label="模板描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-input
            v-model="tagsText"
            type="textarea"
            :rows="2"
            placeholder="请输入标签，多个标签用逗号分隔"
          />
        </el-form-item>
        <el-form-item label="是否公开" prop="is_public">
          <el-switch v-model="formData.is_public" />
        </el-form-item>
        <el-form-item label="是否企业模板" prop="is_enterprise">
          <el-switch v-model="formData.is_enterprise" />
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

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const templates = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  contract_type: '',
  is_public: null,
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const formData = reactive({
  id: null,
  name: '',
  contract_type: 'procurement',
  industry: '',
  category: '',
  content: '',
  description: '',
  tags: [],
  is_public: false,
  is_enterprise: false,
})

const tagsText = ref('')

const formRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  contract_type: [{ required: true, message: '请选择合同类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入模板内容', trigger: 'blur' }],
}

const dialogTitle = computed(() => (isEdit.value ? '编辑模板' : '新建模板'))

const getContractTypeText = (type) => {
  const types = {
    procurement: '采购合同',
    sales: '销售合同',
    labor: '劳动合同',
    service: '服务合同',
  }
  return types[type] || type
}

const fetchTemplates = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    }
    const response = await api.get('/contracts/templates/', { params })
    templates.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchTemplates()
}

const handleReset = () => {
  searchForm.contract_type = ''
  searchForm.is_public = null
  handleSearch()
}

const handleSizeChange = () => {
  fetchTemplates()
}

const handlePageChange = () => {
  fetchTemplates()
}

const handleCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    contract_type: row.contract_type,
    industry: row.industry || '',
    category: row.category || '',
    content: row.content || '',
    description: row.description || '',
    tags: row.tags || [],
    is_public: row.is_public || false,
    is_enterprise: row.is_enterprise || false,
  })
  tagsText.value = Array.isArray(row.tags) ? row.tags.join(',') : ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
      type: 'warning',
    })
    await api.delete(`/contracts/templates/${row.id}/`)
    ElMessage.success('删除成功')
    fetchTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleUse = async (row) => {
  try {
    await api.post(`/contracts/templates/${row.id}/use/`)
    router.push({
      path: '/contracts/create',
      query: { template_id: row.id },
    })
  } catch (error) {
    ElMessage.error('使用模板失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData = { ...formData }
        // 处理标签
        if (tagsText.value) {
          submitData.tags = tagsText.value.split(',').map(tag => tag.trim()).filter(tag => tag)
        } else {
          submitData.tags = []
        }
        if (isEdit.value) {
          await api.patch(`/contracts/templates/${formData.id}/`, submitData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/contracts/templates/', submitData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchTemplates()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetForm()
}

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    name: '',
    contract_type: 'procurement',
    industry: '',
    category: '',
    content: '',
    description: '',
    tags: [],
    is_public: false,
    is_enterprise: false,
  })
  tagsText.value = ''
}

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.template-list {
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

