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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
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

