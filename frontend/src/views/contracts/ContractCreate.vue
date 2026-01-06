<template>
  <div class="contract-create">
    <el-card>
      <template #header>
        <span>新建合同</span>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="合同标题" prop="title">
          <el-input 
            v-model="form.title" 
            placeholder="请输入合同标题，或上传文件自动提取"
            @input="handleTitleInput"
          >
            <template #append>
              <el-button 
                v-if="form.title && autoFilledTitle" 
                @click="handleClearTitle" 
                title="清除自动填充的标题"
              >
                <el-icon><Close /></el-icon>
              </el-button>
            </template>
          </el-input>
          <div v-if="autoFilledTitle" class="title-hint">
            <el-text type="info" size="small">标题已从上传文档自动提取</el-text>
          </div>
        </el-form-item>
        <el-form-item label="合同类型" prop="contract_type">
          <el-select v-model="form.contract_type" placeholder="请选择合同类型">
            <el-option label="采购合同" value="procurement" />
            <el-option label="销售合同" value="sales" />
            <el-option label="劳动合同" value="labor" />
            <el-option label="服务合同" value="service" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属行业" prop="industry">
          <el-input v-model="form.industry" placeholder="请输入所属行业" />
        </el-form-item>
        <el-form-item label="使用模板">
          <el-select v-model="form.template" placeholder="请选择模板（可选）" clearable filterable>
            <el-option
              v-for="template in templates"
              :key="template.id"
              :label="template.name"
              :value="template.id"
            />
          </el-select>
        </el-form-item>
        
        <!-- AI生成合同内容 -->
        <el-form-item label="AI智能生成">
          <el-card shadow="never" style="width: 100%">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>填写基本信息，AI将自动生成合同内容</span>
                <el-button 
                  type="primary" 
                  :icon="MagicStick" 
                  @click="showBasicInfoDialog = true"
                  :disabled="!form.contract_type"
                >
                  填写基本信息
                </el-button>
              </div>
            </template>
            <el-button 
              type="success" 
              :icon="MagicStick" 
              @click="handleAIGenerate"
              :loading="aiGenerating"
              :disabled="!form.contract_type || !basicInfo.party_a || !basicInfo.party_b"
              style="width: 100%"
            >
              {{ aiGenerating ? 'AI生成中，请稍候（可能需要2-3分钟）...' : 'AI生成合同内容' }}
            </el-button>
            <div v-if="aiGenerating" style="margin-top: 10px;">
              <el-alert
                title="AI正在生成详细的合同内容，这可能需要2-3分钟，请耐心等待，不要关闭页面..."
                type="info"
                :closable="false"
                show-icon
              />
            </div>
            <div v-if="aiGeneratedContent" style="margin-top: 10px;">
              <el-alert
                title="AI已生成合同内容，您可以在此基础上进行编辑"
                type="success"
                :closable="false"
                show-icon
              />
            </div>
          </el-card>
        </el-form-item>
        
        <el-form-item label="上传文件">
          <el-upload
            class="upload-demo"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleFileSuccess"
            :on-error="handleFileError"
            :before-upload="beforeUpload"
            :file-list="fileList"
            accept=".doc,.docx,.pdf"
            :limit="1"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持上传 Word (.doc, .docx) 或 PDF (.pdf) 文件，最大 10MB</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="合同内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="请输入合同内容（支持JSON格式），或上传文件自动解析"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 基本信息填写对话框 -->
    <el-dialog
      v-model="showBasicInfoDialog"
      title="填写合同基本信息"
      width="600px"
    >
      <el-form :model="basicInfo" label-width="120px">
        <el-form-item label="甲方（采购方）">
          <el-input v-model="basicInfo.party_a" placeholder="请输入甲方名称" />
        </el-form-item>
        <el-form-item label="乙方（供应方）">
          <el-input v-model="basicInfo.party_b" placeholder="请输入乙方名称" />
        </el-form-item>
        <el-form-item label="标的物/服务">
          <el-input v-model="basicInfo.subject" placeholder="请输入标的物或服务内容" />
        </el-form-item>
        <el-form-item label="合同金额">
          <el-input v-model="basicInfo.amount" placeholder="请输入合同金额，如：100万元" />
        </el-form-item>
        <el-form-item label="交付地点">
          <el-input v-model="basicInfo.delivery_location" placeholder="请输入交付地点（可选）" />
        </el-form-item>
        <el-form-item label="交付时间">
          <el-input v-model="basicInfo.delivery_time" placeholder="请输入交付时间（可选）" />
        </el-form-item>
        <el-form-item label="付款方式">
          <el-input v-model="basicInfo.payment_method" placeholder="请输入付款方式（可选）" />
        </el-form-item>
        <el-form-item label="付款时间">
          <el-input v-model="basicInfo.payment_time" placeholder="请输入付款时间（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBasicInfoDialog = false">取消</el-button>
        <el-button type="primary" @click="showBasicInfoDialog = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close, MagicStick } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const templates = ref([])
const fileList = ref([])
const autoFilledTitle = ref(false) // 标记标题是否自动填充
const uploadUrl = ref('/api/contracts/upload/')
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return {
    Authorization: `Bearer ${token}`,
  }
})
const form = reactive({
  title: '',
  contract_type: '',
  industry: '',
  template: null,
  content: '',
  file_path: '',
})

const basicInfo = reactive({
  party_a: '',
  party_b: '',
  subject: '',
  amount: '',
  delivery_location: '',
  delivery_time: '',
  payment_method: '',
  payment_time: '',
})

const showBasicInfoDialog = ref(false)
const aiGenerating = ref(false)
const aiGeneratedContent = ref(false)

const rules = {
  title: [{ required: true, message: '请输入合同标题', trigger: 'blur' }],
  contract_type: [{ required: true, message: '请选择合同类型', trigger: 'change' }],
}

const fetchTemplates = async () => {
  try {
    const response = await api.get('/contracts/templates/', { params: { page_size: 100 } })
    templates.value = response.data.results || []
  } catch (error) {
    console.error('获取模板列表失败:', error)
  }
}

const beforeUpload = (file) => {
  const isValidType = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传 Word 或 PDF 文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  
  // 如果上传新文件，清除之前的自动填充标记（如果用户没有修改过标题）
  if (autoFilledTitle.value && form.title === autoFilledTitleValue.value) {
    // 保留标记，等待新文件解析结果
  }
  
  return true
}

const handleFileSuccess = async (response, file) => {
  ElMessage.success('文件上传成功')
  if (response.file_path) {
    form.file_path = response.file_path
  }
  
  // 处理文件内容：将解析后的内容对象存储为 JSON 字符串（用于显示和编辑）
  if (response.content) {
    // 如果 content 是对象，转换为格式化的 JSON 字符串以便在文本框中显示
    if (typeof response.content === 'object' && response.content !== null) {
      form.content = JSON.stringify(response.content, null, 2)
    } else {
      form.content = response.content
    }
  }
  
  // 自动填充标题
  if (response.content && typeof response.content === 'object' && response.content.title) {
    const extractedTitle = response.content.title.trim()
    if (extractedTitle) {
      if (!form.title) {
        // 如果当前没有标题，直接填充
        form.title = extractedTitle
        autoFilledTitle.value = true
        autoFilledTitleValue.value = extractedTitle
        ElMessage.info('已自动提取文档标题')
      } else if (form.title !== extractedTitle) {
        // 如果已有标题且不同，询问是否替换
        try {
          await ElMessageBox.confirm(
            `检测到文档标题："${extractedTitle}"\n是否替换当前标题？`,
            '标题提取提示',
            {
              confirmButtonText: '替换',
              cancelButtonText: '保留',
              type: 'info',
            }
          )
          form.title = extractedTitle
          autoFilledTitle.value = true
          autoFilledTitleValue.value = extractedTitle
          ElMessage.success('标题已更新')
        } catch {
          // 用户取消，保留原标题
        }
      }
    }
  }
}

const handleFileError = () => {
  ElMessage.error('文件上传失败')
}

// 存储自动填充的标题，用于检测用户是否手动修改
const autoFilledTitleValue = ref('')

const handleTitleInput = () => {
  // 如果用户修改了自动填充的标题，清除自动填充标记
  if (autoFilledTitle.value && form.title !== autoFilledTitleValue.value) {
    autoFilledTitle.value = false
    autoFilledTitleValue.value = ''
  }
}

const handleClearTitle = () => {
  form.title = ''
  autoFilledTitle.value = false
  autoFilledTitleValue.value = ''
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      let requestData = null // 在外部定义，以便在 catch 中使用
      try {
        // 处理 content 字段：确保是 JSON 对象或 null
        let contentValue = null
        if (form.content) {
          if (typeof form.content === 'string') {
            const trimmed = form.content.trim()
            if (trimmed) {
              if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
                try {
                  contentValue = JSON.parse(trimmed)
                } catch (e) {
                  ElMessage.error('合同内容格式错误，请检查JSON格式')
                  loading.value = false
                  return
                }
              } else {
                // 如果不是 JSON 格式的字符串，包装成对象存储
                contentValue = { text: trimmed }
              }
            }
          } else if (typeof form.content === 'object' && form.content !== null) {
            contentValue = form.content
          }
        }
        
        // 构建提交数据，确保字段格式正确
        // 注意：不包含 drafter 字段，后端会自动设置
        requestData = {
          title: form.title.trim(),
          contract_type: form.contract_type,
        }
        
        // 可选字段：只在有值时才添加
        if (form.industry && form.industry.trim()) {
          requestData.industry = form.industry.trim()
        }
        
        if (contentValue !== null) {
          requestData.content = contentValue
        }
        
        if (form.file_path && form.file_path.trim()) {
          requestData.file_path = form.file_path.trim()
        }
        
        // template 字段：只在有有效值时才添加
        if (form.template && form.template !== '' && form.template !== 0 && form.template !== '0') {
          requestData.template = form.template
        }
        
        const response = await api.post('/contracts/contracts/', requestData)
        ElMessage.success('创建成功')
        router.push(`/contracts/${response.data.id}`)
      } catch (error) {
        console.error('创建合同失败:', error)
        console.error('错误详情:', error.response?.data)
        if (requestData) {
          console.error('请求数据:', requestData)
        }
        
        if (error.response?.data) {
          // 显示后端返回的具体错误信息
          const errorData = error.response.data
          if (typeof errorData === 'object') {
            const errorMessages = Object.entries(errorData)
              .map(([key, value]) => {
                if (Array.isArray(value)) {
                  return `${key}: ${value.join(', ')}`
                } else if (typeof value === 'object') {
                  return `${key}: ${JSON.stringify(value)}`
                }
                return `${key}: ${value}`
              })
              .join('\n')
            ElMessage({
              message: `创建失败：\n${errorMessages}`,
              type: 'error',
              duration: 5000,
              showClose: true,
            })
          } else {
            ElMessage.error(`创建失败：${errorData}`)
          }
        } else {
          ElMessage.error('创建失败，请检查网络连接')
        }
      } finally {
        loading.value = false
      }
    }
  })
}

const handleAIGenerate = async () => {
  if (!form.contract_type) {
    ElMessage.warning('请先选择合同类型')
    return
  }
  
  if (!basicInfo.party_a || !basicInfo.party_b) {
    ElMessage.warning('请先填写甲方和乙方信息')
    showBasicInfoDialog.value = true
    return
  }
  
  aiGenerating.value = true
  try {
    // AI生成合同需要更长时间，设置超时时间为180秒（3分钟）
    const response = await api.post('/contracts/contracts/generate_content/', {
      contract_type: form.contract_type,
      industry: form.industry || '',
      template_id: form.template || null,
      basic_info: basicInfo
    }, {
      timeout: 180000 // 180秒（3分钟）超时，因为AI生成详细合同需要较长时间
    })
    
    console.log('AI生成响应:', response.data)
    
    if (response.data.success) {
      const content = response.data.content
      if (content && content.text) {
        form.content = content.text
        aiGeneratedContent.value = true
        ElMessage.success('AI生成成功！请检查并编辑生成的内容')
      } else if (content && content.html) {
        // 如果只有HTML，提取文本
        const tempDiv = document.createElement('div')
        tempDiv.innerHTML = content.html
        form.content = tempDiv.textContent || tempDiv.innerText || ''
        aiGeneratedContent.value = true
        ElMessage.success('AI生成成功！请检查并编辑生成的内容')
      } else {
        // 如果content是字符串，直接使用
        if (typeof content === 'string' && content.trim()) {
          form.content = content
          aiGeneratedContent.value = true
          ElMessage.success('AI生成成功！请检查并编辑生成的内容')
        } else {
          ElMessage.warning('生成的内容为空，请检查配置')
        }
      }
    } else {
      // 即使不成功，也尝试使用返回的内容
      if (response.data.content) {
        const content = response.data.content
        if (content && content.text) {
          form.content = content.text
          aiGeneratedContent.value = true
        } else if (typeof content === 'string' && content.trim()) {
          form.content = content
          aiGeneratedContent.value = true
        }
      }
      ElMessage.warning(response.data.message || 'AI生成失败，已使用模板生成')
    }
  } catch (error) {
    console.error('AI生成失败:', error)
    console.error('错误详情:', error.response?.data)
    
    // 处理超时错误
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.error({
        message: 'AI生成超时，生成详细合同需要较长时间（可能需要3-5分钟）。建议：1. 检查网络连接 2. 稍后重试 3. 或联系管理员检查AI服务配置',
        duration: 8000,
        showClose: true
      })
    } else {
      const errorMsg = error.response?.data?.error || 
                      error.response?.data?.detail || 
                      error.message || 
                      'AI生成失败，请稍后重试'
      ElMessage.error(errorMsg)
    }
  } finally {
    aiGenerating.value = false
  }
}

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.contract-create {
  padding: 20px;
}

.title-hint {
  margin-top: 5px;
}
</style>

