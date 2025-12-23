<template>
  <div class="rule-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审核规则列表</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建规则
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent="handleSearch">
        <el-form-item label="规则类型">
          <el-select 
            v-model="searchForm.rule_type" 
            placeholder="请选择" 
            clearable 
            filterable
            style="min-width: 180px"
            @change="handleSearch"
          >
            <el-option label="通用规则" value="general" />
            <el-option label="行业规则" value="industry" />
            <el-option label="企业规则" value="enterprise" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select 
            v-model="searchForm.risk_level" 
            placeholder="请选择" 
            clearable 
            filterable
            style="min-width: 180px"
            @change="handleSearch"
          >
            <el-option label="高风险" value="high" />
            <el-option label="中风险" value="medium" />
            <el-option label="低风险" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="searchForm.is_active" 
            placeholder="请选择" 
            clearable 
            filterable
            style="min-width: 180px"
            @change="handleSearch"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="rules" v-loading="loading" style="width: 100%">
        <el-table-column prop="rule_code" label="规则编码" width="150" />
        <el-table-column prop="rule_name" label="规则名称" />
        <el-table-column prop="rule_type" label="规则类型" width="120">
          <template #default="{ row }">
            {{ getRuleTypeText(row.rule_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="industry" label="适用行业" width="120" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk_level)">{{ getRiskText(row.risk_level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
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
        <el-form-item label="规则编码" prop="rule_code">
          <el-input v-model="formData.rule_code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="规则名称" prop="rule_name">
          <el-input v-model="formData.rule_name" />
        </el-form-item>
        <el-form-item label="规则类型" prop="rule_type">
          <el-select 
            v-model="formData.rule_type" 
            placeholder="请选择规则类型" 
            filterable
            style="width: 100%"
          >
            <el-option label="通用规则" value="general" />
            <el-option label="行业规则" value="industry" />
            <el-option label="企业规则" value="enterprise" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用行业" prop="industry">
          <el-input v-model="formData.industry" placeholder="如：制造业、金融业等" />
        </el-form-item>
        <el-form-item label="规则分类" prop="category">
          <el-input v-model="formData.category" placeholder="如：合同条款、风险控制等" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="formData.priority" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="风险等级" prop="risk_level">
          <el-select 
            v-model="formData.risk_level" 
            placeholder="请选择风险等级" 
            filterable
            style="width: 100%"
          >
            <el-option label="高风险" value="high" />
            <el-option label="中风险" value="medium" />
            <el-option label="低风险" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="规则内容" prop="rule_content">
          <el-input
            v-model="ruleContentText"
            type="textarea"
            :rows="6"
            placeholder='请输入JSON格式的规则内容，例如：{"condition": "...", "action": "..."}'
          />
        </el-form-item>
        <el-form-item label="法律依据" prop="legal_basis">
          <el-input v-model="formData.legal_basis" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="规则描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="formData.is_active" />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const submitting = ref(false)
const rules = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  rule_type: '',
  risk_level: '',
  is_active: null,
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const formData = reactive({
  id: null,
  rule_code: '',
  rule_name: '',
  rule_type: 'general',
  industry: '',
  category: '',
  priority: 0,
  rule_content: {},
  risk_level: '',
  legal_basis: '',
  description: '',
  is_active: true,
})

const ruleContentText = ref('')

const formRules = {
  rule_code: [{ required: true, message: '请输入规则编码', trigger: 'blur' }],
  rule_name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  rule_type: [{ required: true, message: '请选择规则类型', trigger: 'change' }],
}

const dialogTitle = computed(() => (isEdit.value ? '编辑规则' : '新建规则'))

const getRuleTypeText = (type) => {
  const types = {
    general: '通用规则',
    industry: '行业规则',
    enterprise: '企业规则',
  }
  return types[type] || type
}

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

const fetchRules = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    }
    const response = await api.get('/rules/rules/', { params })
    rules.value = response.data.results || []
    pagination.total = response.data.count || 0
  } catch (error) {
    ElMessage.error('获取规则列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchRules()
}

const handleReset = () => {
  searchForm.rule_type = ''
  searchForm.risk_level = ''
  searchForm.is_active = null
  handleSearch()
}

const handleSizeChange = () => {
  fetchRules()
}

const handlePageChange = () => {
  fetchRules()
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
    rule_code: row.rule_code,
    rule_name: row.rule_name,
    rule_type: row.rule_type,
    industry: row.industry || '',
    category: row.category || '',
    priority: row.priority || 0,
    rule_content: row.rule_content || {},
    risk_level: row.risk_level || '',
    legal_basis: row.legal_basis || '',
    description: row.description || '',
    is_active: row.is_active,
  })
  ruleContentText.value = typeof row.rule_content === 'object' 
    ? JSON.stringify(row.rule_content, null, 2) 
    : row.rule_content || ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该规则吗？', '提示', {
      type: 'warning',
    })
    await api.delete(`/rules/rules/${row.id}/`)
    ElMessage.success('删除成功')
    fetchRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData = { ...formData }
        // 解析规则内容JSON
        if (ruleContentText.value) {
          try {
            submitData.rule_content = JSON.parse(ruleContentText.value)
          } catch (e) {
            ElMessage.error('规则内容必须是有效的JSON格式')
            submitting.value = false
            return
          }
        }
        if (isEdit.value) {
          await api.patch(`/rules/rules/${formData.id}/`, submitData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/rules/rules/', submitData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchRules()
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
    rule_code: '',
    rule_name: '',
    rule_type: 'general',
    industry: '',
    category: '',
    priority: 0,
    rule_content: {},
    risk_level: '',
    legal_basis: '',
    description: '',
    is_active: true,
  })
  ruleContentText.value = ''
}

onMounted(() => {
  fetchRules()
})
</script>

<style scoped>
.rule-list {
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

