<template>
  <div class="contract-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>合同详情</span>
          <div>
            <el-button @click="handleEdit" v-if="!isEditMode">编辑</el-button>
            <el-button @click="handleCancelEdit" v-if="isEditMode">取消</el-button>
            <el-button type="primary" @click="handleSave" v-if="isEditMode">保存</el-button>
            <el-button @click="handleReview" v-if="!isEditMode">提交审核</el-button>
            <el-button type="primary" @click="handleCreateVersion" v-if="!isEditMode">创建新版本</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border v-if="!isEditMode">
        <el-descriptions-item label="合同编号">{{ contract.contract_no }}</el-descriptions-item>
        <el-descriptions-item label="合同标题">{{ contract.title }}</el-descriptions-item>
        <el-descriptions-item label="合同类型">{{ getContractTypeText(contract.contract_type) }}</el-descriptions-item>
        <el-descriptions-item label="所属行业">{{ contract.industry }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(contract.status)">{{ getStatusText(contract.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="当前版本">v{{ contract.current_version }}</el-descriptions-item>
        <el-descriptions-item label="起草人">{{ contract.drafter_name }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(contract.created_at) }}</el-descriptions-item>
      </el-descriptions>

      <el-form
        v-if="isEditMode"
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        style="margin-top: 20px"
      >
        <el-form-item label="合同标题" prop="title">
          <el-input v-model="formData.title" />
        </el-form-item>
        <el-form-item label="合同类型" prop="contract_type">
          <el-select v-model="formData.contract_type" placeholder="请选择合同类型" style="width: 100%">
            <el-option label="采购合同" value="procurement" />
            <el-option label="销售合同" value="sales" />
            <el-option label="劳动合同" value="labor" />
            <el-option label="服务合同" value="service" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属行业" prop="industry">
          <el-input v-model="formData.industry" placeholder="如：制造业、金融业等" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="草稿" value="draft" />
            <el-option label="审核中" value="reviewing" />
            <el-option label="已审核" value="reviewed" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已签署" value="signed" />
          </el-select>
        </el-form-item>
        <el-form-item label="合同内容" prop="content">
          <el-radio-group v-model="contentEditMode" style="margin-bottom: 10px">
            <el-radio label="json">JSON编辑</el-radio>
            <el-radio label="rich">富文本编辑</el-radio>
          </el-radio-group>
          <el-input
            v-if="contentEditMode === 'json'"
            v-model="contentText"
            type="textarea"
            :rows="10"
            placeholder='请输入JSON格式的合同内容'
          />
          <QuillEditor
            v-else
            v-model:content="richContent"
            contentType="html"
            theme="snow"
            style="height: 300px; margin-bottom: 50px"
          />
        </el-form-item>
      </el-form>

      <el-tabs v-model="activeTab" style="margin-top: 20px">
        <el-tab-pane label="合同内容" name="content">
          <pre v-if="contract.content" class="content-preview">{{ JSON.stringify(contract.content, null, 2) }}</pre>
          <el-empty v-else description="暂无内容" />
        </el-tab-pane>
        <el-tab-pane label="版本历史" name="versions">
          <el-timeline>
            <el-timeline-item
              v-for="version in versions"
              :key="version.id"
              :timestamp="formatDateTime(version.created_at)"
              placement="top"
            >
              <el-card>
                <h4>版本 {{ version.version }}</h4>
                <p>{{ version.change_summary || '无变更摘要' }}</p>
                <p>变更人：{{ version.changed_by_name }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/date'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const contract = ref({})
const versions = ref([])
const activeTab = ref('content')
const isEditMode = ref(false)
const formRef = ref(null)

const formData = reactive({
  title: '',
  contract_type: '',
  industry: '',
  status: '',
  content: {},
})

const contentText = ref('')
const richContent = ref('')
const contentEditMode = ref('json')

const formRules = {
  title: [{ required: true, message: '请输入合同标题', trigger: 'blur' }],
  contract_type: [{ required: true, message: '请选择合同类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const isEditQuery = computed(() => route.query.edit === 'true')

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

const fetchContract = async () => {
  loading.value = true
  try {
    const response = await api.get(`/contracts/contracts/${route.params.id}/`)
    contract.value = response.data
    if (isEditQuery.value) {
      handleEdit()
    }
    fetchVersions()
  } catch (error) {
    ElMessage.error('获取合同详情失败')
  } finally {
    loading.value = false
  }
}

const fetchVersions = async () => {
  try {
    const response = await api.get(`/contracts/contracts/${route.params.id}/versions/`)
    versions.value = response.data
  } catch (error) {
    console.error('获取版本历史失败:', error)
  }
}

const handleReview = async () => {
  try {
    await api.post('/reviews/tasks/', {
      contract: contract.value.id,
      task_type: 'auto',
    })
    ElMessage.success('已提交审核')
    router.push('/reviews')
  } catch (error) {
    ElMessage.error('提交审核失败')
  }
}

const handleEdit = () => {
  isEditMode.value = true
  Object.assign(formData, {
    title: contract.value.title || '',
    contract_type: contract.value.contract_type || '',
    industry: contract.value.industry || '',
    status: contract.value.status || 'draft',
    content: contract.value.content || {},
  })
  if (typeof contract.value.content === 'object') {
    contentText.value = JSON.stringify(contract.value.content, null, 2)
    richContent.value = contract.value.content?.html || ''
  } else {
    contentText.value = contract.value.content || ''
    richContent.value = contract.value.content || ''
  }
}

const handleCancelEdit = () => {
  isEditMode.value = false
  formRef.value?.resetFields()
  router.replace({ query: {} })
}

const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData = { ...formData }
        // 处理合同内容
        if (contentEditMode.value === 'json') {
          if (contentText.value) {
            try {
              submitData.content = JSON.parse(contentText.value)
            } catch (e) {
              ElMessage.error('合同内容必须是有效的JSON格式')
              submitting.value = false
              return
            }
          }
        } else {
          // 富文本模式，保存为HTML格式
          submitData.content = {
            html: richContent.value,
            text: richContent.value.replace(/<[^>]*>/g, ''),
          }
        }
        await api.patch(`/contracts/contracts/${route.params.id}/`, submitData)
        ElMessage.success('更新成功')
        isEditMode.value = false
        router.replace({ query: {} })
        fetchContract()
      } catch (error) {
        ElMessage.error('更新失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleCreateVersion = async () => {
  try {
    await api.post(`/contracts/contracts/${route.params.id}/create_version/`, {
      content: contract.value.content,
      change_summary: '手动创建新版本',
    })
    ElMessage.success('已创建新版本')
    fetchContract()
  } catch (error) {
    ElMessage.error('创建版本失败')
  }
}

onMounted(() => {
  fetchContract()
})
</script>

<style scoped>
.contract-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-preview {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}
</style>

