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
          <el-select 
            v-model="form.contract_type" 
            placeholder="请选择合同类型" 
            filterable
            style="width: 100%"
          >
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
          <el-select 
            v-model="form.template" 
            placeholder="请选择模板（可选）" 
            clearable 
            filterable
            style="width: 100%"
            @change="handleTemplateChange"
          >
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
          <el-radio-group v-model="contentEditMode" style="margin-bottom: 10px">
            <el-radio label="json">JSON编辑</el-radio>
            <el-radio label="rich">富文本编辑</el-radio>
          </el-radio-group>
          <div v-if="contentEditMode === 'json'" style="width: 100%">
            <el-input
              v-model="contentText"
              type="textarea"
              :rows="10"
              placeholder="请输入JSON格式的合同内容，或上传文件自动解析"
            />
          </div>
          <div v-else class="quill-editor-wrapper">
            <QuillEditor
              v-model:content="richContent"
              contentType="html"
              theme="snow"
              style="height: 300px; margin-bottom: 50px"
            />
          </div>
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
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import api from '@/utils/api'

const router = useRouter()
const route = useRoute()
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

const contentText = ref('')
const richContent = ref('')
const contentEditMode = ref('json')

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

// 将纯文本转换为HTML格式
const convertTextToHtml = (text) => {
  if (!text) return ''
  // 如果已经是HTML格式，直接返回
  if (text.trim().startsWith('<')) {
    return text
  }
  // 将纯文本按行分割，每行用 <p> 标签包裹
  const lines = text.split('\n').filter(line => line.trim())
  return lines.map(line => `<p>${line.trim()}</p>`).join('')
}

// 加载模板并填充表单
const loadTemplate = async (templateId) => {
  if (!templateId) {
    // 如果模板ID为空，清空内容
    contentText.value = ''
    richContent.value = ''
    return
  }
  
  try {
    loading.value = true
    const response = await api.get(`/contracts/templates/${templateId}/`)
    const template = response.data
    
    // 填充表单字段
    if (template.name) {
      form.title = template.name
    }
    if (template.contract_type) {
      form.contract_type = template.contract_type
    }
    if (template.industry) {
      form.industry = template.industry
    }
    
    // 处理模板内容
    if (template.content) {
      let contentHtml = ''
      
      if (typeof template.content === 'object' && template.content !== null) {
        // 如果 content 是对象，检查是否有 HTML 内容
        if (template.content.html) {
          contentHtml = template.content.html
        } else if (template.content.text) {
          // 如果有 text 字段，转换为 HTML
          contentHtml = convertTextToHtml(template.content.text)
        } else {
          // 否则转换为 JSON 字符串
          contentText.value = JSON.stringify(template.content, null, 2)
          contentEditMode.value = 'json'
          return
        }
      } else if (typeof template.content === 'string') {
        // 如果是字符串，检查是否是 HTML
        if (template.content.trim().startsWith('<')) {
          contentHtml = template.content
        } else {
          // 纯文本，转换为 HTML
          contentHtml = convertTextToHtml(template.content)
        }
      }
      
      // 设置富文本内容并切换到富文本模式
      if (contentHtml) {
        richContent.value = contentHtml
        contentEditMode.value = 'rich'
      }
    }
    
    ElMessage.success('模板内容已加载')
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

// 处理模板下拉框变化
const handleTemplateChange = (templateId) => {
  if (templateId) {
    loadTemplate(templateId)
  } else {
    // 清空模板内容
    contentText.value = ''
    richContent.value = ''
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
    let contentHtml = ''
    
    if (typeof response.content === 'object' && response.content !== null) {
      // 检查是否有 HTML 内容
      if (response.content.html) {
        contentHtml = response.content.html
      } else if (response.content.text) {
        // 如果有 text 字段，转换为 HTML
        contentHtml = convertTextToHtml(response.content.text)
      } else {
        // 否则使用 JSON 模式
        contentText.value = JSON.stringify(response.content, null, 2)
        contentEditMode.value = 'json'
        return
      }
    } else if (typeof response.content === 'string') {
      // 如果是字符串，检查是否是 HTML
      if (response.content.trim().startsWith('<')) {
        contentHtml = response.content
      } else {
        // 纯文本，转换为 HTML
        contentHtml = convertTextToHtml(response.content)
      }
    }
    
    // 设置富文本内容并切换到富文本模式
    if (contentHtml) {
      richContent.value = contentHtml
      contentEditMode.value = 'rich'
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
        // 处理 content 字段：根据编辑模式处理内容
        let contentValue = null
        if (contentEditMode.value === 'json') {
          // JSON 模式
          if (contentText.value) {
            const trimmed = contentText.value.trim()
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
          }
        } else {
          // 富文本模式，保存为HTML格式
          if (richContent.value) {
            contentValue = {
              html: richContent.value,
              text: richContent.value.replace(/<[^>]*>/g, ''),
            }
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

onMounted(async () => {
  await fetchTemplates()
  
  // 检查 URL 中是否有 template_id 参数
  const templateId = route.query.template_id
  if (templateId) {
    // 将 template_id 转换为数字
    const id = typeof templateId === 'string' ? parseInt(templateId, 10) : templateId
    if (!isNaN(id) && id > 0) {
      await loadTemplate(id)
    }
  }
})
</script>

<style scoped>
.contract-create {
  padding: 20px;
}

.title-hint {
  margin-top: 5px;
}

.quill-editor-wrapper {
  width: 100%;
}

.quill-editor-wrapper :deep(.ql-container) {
  width: 100%;
}

.quill-editor-wrapper :deep(.ql-editor) {
  width: 100%;
  min-height: 300px;
}

.quill-editor-wrapper :deep(.ql-toolbar) {
  width: 100%;
}
</style>

