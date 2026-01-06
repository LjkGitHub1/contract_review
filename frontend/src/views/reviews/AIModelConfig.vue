<template>
  <div class="ai-model-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI模型配置</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
        </div>
      </template>

      <el-alert
        title="说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p>配置AI大模型接口，支持硅基流动等模型服务。可以创建多个配置，但只能有一个作为系统默认配置。</p>
      </el-alert>

      <el-table :data="configs" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="配置名称" width="200" />
        <el-table-column prop="provider_display" label="服务提供商" width="120" />
        <el-table-column prop="default_model" label="默认模型" width="200" />
        <el-table-column prop="api_base_url" label="API地址" min-width="250" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_default" label="系统默认" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="warning">默认</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="warning" @click="handleSetDefault(row)" v-if="!row.is_default">
              设为默认
            </el-button>
            <el-button link type="info" @click="handleTestConnection(row)">测试连接</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
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
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入配置名称" />
        </el-form-item>

        <el-form-item label="服务提供商" prop="provider">
          <el-select v-model="formData.provider" placeholder="请选择服务提供商" @change="handleProviderChange">
            <el-option label="硅基流动" value="siliconflow" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="formData.api_key"
            type="password"
            show-password
            placeholder="请输入API密钥"
          />
          <div class="form-item-tip">
            <el-link
              v-if="formData.provider === 'siliconflow'"
              href="https://siliconflow.cn"
              target="_blank"
              type="primary"
            >
              获取硅基流动API密钥
            </el-link>
          </div>
        </el-form-item>

        <el-form-item label="API基础地址" prop="api_base_url">
          <el-input
            v-model="formData.api_base_url"
            placeholder="请输入API基础地址"
          />
          <div class="form-item-tip">
            <span v-if="formData.provider === 'siliconflow'">
              硅基流动默认地址：https://api.siliconflow.cn/v1
            </span>
          </div>
        </el-form-item>

        <el-form-item label="可用模型" prop="available_models">
          <div style="width: 100%">
            <el-button
              type="primary"
              size="small"
              @click="showModelSelector = true"
              style="margin-bottom: 10px"
            >
              选择模型
            </el-button>
            <el-tag
              v-for="(model, index) in formData.available_models"
              :key="index"
              closable
              @close="removeModel(index)"
              style="margin-right: 8px; margin-bottom: 8px"
            >
              {{ model }}
            </el-tag>
            <div v-if="formData.available_models.length === 0" class="empty-tip">
              请选择至少一个模型
            </div>
          </div>
        </el-form-item>

        <el-form-item label="默认模型" prop="default_model">
          <el-select
            v-model="formData.default_model"
            placeholder="请选择默认模型"
            :disabled="formData.available_models.length === 0"
          >
            <el-option
              v-for="model in formData.available_models"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="温度参数" prop="temperature">
          <el-slider
            v-model="formData.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
            :show-input-controls="false"
          />
          <div class="form-item-tip">控制输出的随机性，范围0-2，默认0.7</div>
        </el-form-item>

        <el-form-item label="最大Token数" prop="max_tokens">
          <el-input-number
            v-model="formData.max_tokens"
            :min="100"
            :max="8000"
            :step="100"
            style="width: 100%"
          />
          <div class="form-item-tip">生成内容的最大长度，默认2000</div>
        </el-form-item>

        <el-form-item label="超时时间（秒）" prop="timeout">
          <el-input-number
            v-model="formData.timeout"
            :min="10"
            :max="120"
            :step="5"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="配置描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述（可选）"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>

        <el-form-item label="系统默认">
          <el-switch
            v-model="formData.is_default"
            active-text="设为默认"
            inactive-text="否"
            :disabled="!formData.is_active"
          />
          <div class="form-item-tip">只能有一个配置为系统默认</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 模型选择对话框 -->
    <el-dialog
      v-model="showModelSelector"
      title="选择模型"
      width="600px"
    >
      <div v-loading="loadingModels">
        <el-checkbox-group v-model="selectedModels">
          <el-checkbox
            v-for="model in availableModelsList"
            :key="model.value"
            :label="model.value"
            style="display: block; margin-bottom: 10px"
          >
            {{ model.label }}
          </el-checkbox>
        </el-checkbox-group>
      </div>
      <template #footer>
        <el-button @click="showModelSelector = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmModels">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const loading = ref(false)
const loadingModels = ref(false)
const submitting = ref(false)
const configs = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建配置')
const isEdit = ref(false)
const showModelSelector = ref(false)
const availableModelsList = ref([])
const selectedModels = ref([])

const formRef = ref(null)
const formData = reactive({
  id: null,
  name: '',
  provider: 'siliconflow',
  api_key: '',
  api_base_url: 'https://api.siliconflow.cn/v1',
  available_models: [],
  default_model: '',
  temperature: 0.7,
  max_tokens: 2000,
  timeout: 30,
  description: '',
  is_active: true,
  is_default: false
})

const formRules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择服务提供商', trigger: 'change' }],
  api_key: [{ required: true, message: '请输入API密钥', trigger: 'blur' }],
  api_base_url: [{ required: true, message: '请输入API基础地址', trigger: 'blur' }],
  available_models: [
    { required: true, type: 'array', min: 1, message: '请至少选择一个模型', trigger: 'change' }
  ],
  default_model: [{ required: true, message: '请选择默认模型', trigger: 'change' }],
  temperature: [{ required: true, message: '请输入温度参数', trigger: 'blur' }],
  max_tokens: [{ required: true, message: '请输入最大Token数', trigger: 'blur' }],
  timeout: [{ required: true, message: '请输入超时时间', trigger: 'blur' }]
}

// 获取配置列表
const fetchConfigs = async () => {
  loading.value = true
  try {
    const response = await api.get('/reviews/ai-model-configs/')
    configs.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取配置列表失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 获取可用模型列表
const fetchAvailableModels = async (provider = 'siliconflow') => {
  loadingModels.value = true
  try {
    const response = await api.get(`/reviews/ai-model-configs/get_available_models/?provider=${provider}`)
    availableModelsList.value = response.data.models || []
  } catch (error) {
    ElMessage.error('获取模型列表失败：' + (error.response?.data?.detail || error.message))
    // 如果API失败，使用默认列表
    if (provider === 'siliconflow') {
      availableModelsList.value = [
        { value: 'deepseek-chat', label: 'DeepSeek Chat' },
        { value: 'deepseek-coder', label: 'DeepSeek Coder' },
        { value: 'qwen-plus', label: 'Qwen Plus' },
        { value: 'qwen-turbo', label: 'Qwen Turbo' },
        { value: 'qwen-max', label: 'Qwen Max' },
        { value: 'glm-4', label: 'GLM-4' },
        { value: 'chatgpt-3.5-turbo', label: 'ChatGPT-3.5 Turbo' },
        { value: 'gpt-4', label: 'GPT-4' }
      ]
    }
  } finally {
    loadingModels.value = false
  }
}

// 处理服务提供商变更
const handleProviderChange = (provider) => {
  if (provider === 'siliconflow') {
    formData.api_base_url = 'https://api.siliconflow.cn/v1'
  } else if (provider === 'openai') {
    formData.api_base_url = 'https://api.openai.com/v1'
  }
  fetchAvailableModels(provider)
}

// 新建配置
const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新建配置'
  resetForm()
  fetchAvailableModels('siliconflow')
  dialogVisible.value = true
}

// 编辑配置
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑配置'
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    provider: row.provider,
    api_key: row.api_key,
    api_base_url: row.api_base_url,
    available_models: row.available_models || [],
    default_model: row.default_model || '',
    temperature: row.temperature || 0.7,
    max_tokens: row.max_tokens || 2000,
    timeout: row.timeout || 30,
    description: row.description || '',
    is_active: row.is_active,
    is_default: row.is_default
  })
  selectedModels.value = [...formData.available_models]
  fetchAvailableModels(row.provider)
  dialogVisible.value = true
}

// 删除配置
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该配置吗？', '提示', {
      type: 'warning'
    })
    await api.delete(`/reviews/ai-model-configs/${row.id}/`)
    ElMessage.success('删除成功')
    fetchConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

// 设为默认
const handleSetDefault = async (row) => {
  try {
    await api.post(`/reviews/ai-model-configs/${row.id}/set_default/`)
    ElMessage.success('已设置为系统默认配置')
    fetchConfigs()
  } catch (error) {
    ElMessage.error('设置失败：' + (error.response?.data?.detail || error.message))
  }
}

// 测试连接
const handleTestConnection = async (row) => {
  try {
    const response = await api.post(`/reviews/ai-model-configs/${row.id}/test_connection/`)
    if (response.data.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error('连接测试失败：' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('连接测试失败：' + (error.response?.data?.detail || error.message))
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const data = { ...formData }
    
    if (isEdit.value) {
      await api.patch(`/reviews/ai-model-configs/${formData.id}/`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post('/reviews/ai-model-configs/', data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchConfigs()
  } catch (error) {
    if (error.response?.status !== 400) {
      ElMessage.error('操作失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    submitting.value = false
  }
}

// 确认选择模型
const handleConfirmModels = () => {
  formData.available_models = [...selectedModels.value]
  if (formData.available_models.length > 0 && !formData.available_models.includes(formData.default_model)) {
    formData.default_model = formData.available_models[0]
  }
  showModelSelector.value = false
}

// 移除模型
const removeModel = (index) => {
  const removed = formData.available_models[index]
  formData.available_models.splice(index, 1)
  if (formData.default_model === removed) {
    formData.default_model = formData.available_models[0] || ''
  }
  selectedModels.value = [...formData.available_models]
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    id: null,
    name: '',
    provider: 'siliconflow',
    api_key: '',
    api_base_url: 'https://api.siliconflow.cn/v1',
    available_models: [],
    default_model: '',
    temperature: 0.7,
    max_tokens: 2000,
    timeout: 30,
    description: '',
    is_active: true,
    is_default: false
  })
  selectedModels.value = []
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchConfigs()
})
</script>

<style scoped>
.ai-model-config {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.empty-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
</style>

