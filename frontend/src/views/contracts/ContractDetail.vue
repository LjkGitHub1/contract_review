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
          <div style="margin-top: 10px;">
            <el-checkbox v-model="createNewVersionOnSave">
              保存时创建新版本（如果内容有变化）
            </el-checkbox>
          </div>
          <el-input
            v-if="contentEditMode === 'json'"
            v-model="contentText"
            type="textarea"
            :rows="10"
            placeholder='请输入JSON格式的合同内容'
          />
          <div v-else class="quill-editor-wrapper">
            <QuillEditor
              v-model:content="richContent"
              contentType="html"
              theme="snow"
              :options="quillOptions"
            />
          </div>
        </el-form-item>
      </el-form>

      <el-tabs v-model="activeTab" style="margin-top: 20px">
        <el-tab-pane label="合同内容" name="content">
          <div v-if="contract.content" class="content-display">
            <!-- 如果内容有HTML格式，使用HTML显示 -->
            <div v-if="displayContentType === 'html'" 
                 class="content-html" 
                 v-html="formattedContent">
            </div>
            <!-- 如果是纯文本，使用文本显示 -->
            <div v-else-if="displayContentType === 'text'" 
                 class="content-text">
              {{ formattedContent }}
            </div>
            <!-- 如果是JSON对象，使用格式化JSON显示 -->
            <pre v-else class="content-json">{{ formattedContent }}</pre>
          </div>
          <el-empty v-else description="暂无内容" />
        </el-tab-pane>
        <el-tab-pane label="版本历史" name="versions">
          <div v-if="versions.length > 0" class="versions-container">
            <div class="version-controls" style="margin-bottom: 20px;">
              <el-select 
                v-model="compareVersion1" 
                placeholder="选择版本1" 
                style="width: 150px; margin-right: 10px;"
                @change="handleVersionCompare"
              >
                <el-option
                  v-for="v in versions"
                  :key="v.id"
                  :label="`版本 ${v.version}`"
                  :value="v.version"
                />
              </el-select>
              <span style="margin: 0 10px;">与</span>
              <el-select 
                v-model="compareVersion2" 
                placeholder="选择版本2" 
                style="width: 150px; margin-right: 10px;"
                @change="handleVersionCompare"
              >
                <el-option
                  v-for="v in versions"
                  :key="v.id"
                  :label="`版本 ${v.version}`"
                  :value="v.version"
                />
              </el-select>
              <el-button 
                type="primary" 
                @click="handleVersionCompare"
                :disabled="!compareVersion1 || !compareVersion2"
              >
                对比版本
              </el-button>
              <el-button 
                v-if="showDiff"
                @click="showDiff = false"
              >
                关闭对比
              </el-button>
            </div>

            <!-- 版本差异显示 -->
            <el-card v-if="showDiff && diffResult" style="margin-bottom: 20px;">
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <div>
                    <span style="font-weight: 500;">版本对比：</span>
                    <el-tag type="info" size="small" style="margin-right: 5px;">版本 {{ compareVersion1 }}</el-tag>
                    <span style="margin: 0 5px;">vs</span>
                    <el-tag type="success" size="small">版本 {{ compareVersion2 }}</el-tag>
                  </div>
                  <div style="display: flex; gap: 10px; align-items: center;">
                    <el-tag v-if="diffResult.stats.added > 0" type="success" size="small">
                      +{{ diffResult.stats.added }} 新增
                    </el-tag>
                    <el-tag v-if="diffResult.stats.removed > 0" type="danger" size="small">
                      -{{ diffResult.stats.removed }} 删除
                    </el-tag>
                    <el-tag v-if="diffResult.stats.modified > 0" type="warning" size="small">
                      ~{{ diffResult.stats.modified }} 修改
                    </el-tag>
                    <el-tag v-if="diffResult.stats.added === 0 && diffResult.stats.removed === 0 && diffResult.stats.modified === 0" type="info" size="small">
                      无差异
                    </el-tag>
                  </div>
                </div>
              </template>
              <div class="diff-container">
                <div class="diff-content">
                  <div 
                    v-for="(line, index) in diffResult.lines" 
                    :key="index"
                    :class="['diff-line', `diff-${line.type}`]"
                  >
                    <span class="diff-line-number">{{ line.oldLine || '' }}</span>
                    <span class="diff-line-number">{{ line.newLine || '' }}</span>
                    <span class="diff-content-text">
                      <template v-if="line.type === 'modified'">
                        <span class="diff-old-content" v-html="line.content"></span>
                        <span class="diff-arrow">→</span>
                        <span class="diff-new-content" v-html="line.newContent"></span>
                      </template>
                      <span v-else v-html="line.content"></span>
                    </span>
                  </div>
                </div>
              </div>
            </el-card>

            <!-- 版本列表 -->
            <el-timeline>
              <el-timeline-item
                v-for="(version, index) in versions"
                :key="version.id"
                :timestamp="formatDateTime(version.created_at)"
                placement="top"
                :type="index === 0 && contract.current_version === version.version ? 'success' : 'primary'"
              >
                <el-card>
                  <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                      <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <h4 style="margin: 0; margin-right: 10px;">版本 {{ version.version }}</h4>
                        <el-tag 
                          v-if="index === 0 && contract.current_version === version.version" 
                          type="success" 
                          size="small"
                        >
                          当前版本
                        </el-tag>
                      </div>
                      
                      <!-- 版本信息详情 -->
                      <el-descriptions :column="2" border size="small" style="margin-bottom: 10px;">
                        <el-descriptions-item label="版本号">
                          <el-tag type="info" size="small">v{{ version.version }}</el-tag>
                        </el-descriptions-item>
                        <el-descriptions-item label="变更时间">
                          <el-icon style="margin-right: 5px; color: #909399;"><Clock /></el-icon>
                          {{ formatDateTime(version.created_at) }}
                        </el-descriptions-item>
                        <el-descriptions-item label="变更人">
                          <el-icon style="margin-right: 5px; color: #909399;"><User /></el-icon>
                          {{ version.changed_by_name }}
                        </el-descriptions-item>
                        <el-descriptions-item label="变更摘要" :span="2">
                          <div style="max-width: 600px; word-wrap: break-word; line-height: 1.6;">
                            <el-icon style="margin-right: 5px; color: #909399; vertical-align: middle;"><EditPen /></el-icon>
                            <span>{{ version.change_summary || '无变更摘要' }}</span>
                          </div>
                        </el-descriptions-item>
                      </el-descriptions>
                      
                      <!-- 操作按钮 -->
                      <div style="display: flex; gap: 10px; margin-top: 10px; flex-wrap: wrap;">
                        <el-button 
                          size="small" 
                          @click="viewVersionContent(version)"
                        >
                          <el-icon style="margin-right: 5px;"><View /></el-icon>
                          查看内容
                        </el-button>
                        <!-- 显示与上一个版本的对比 -->
                        <el-button 
                          v-if="index < versions.length - 1"
                          size="small" 
                          type="primary"
                          plain
                          @click="quickCompare(version.version, versions[index + 1].version)"
                        >
                          <el-icon style="margin-right: 5px;"><DocumentCopy /></el-icon>
                          对比版本 {{ versions[index + 1].version }}
                        </el-button>
                        <!-- 回滚到该版本 -->
                        <el-button 
                          v-if="index > 0 || contract.current_version !== version.version"
                          size="small" 
                          type="warning"
                          plain
                          @click="handleRollback(version)"
                        >
                          <el-icon style="margin-right: 5px;"><RefreshLeft /></el-icon>
                          回滚到此版本
                        </el-button>
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
          <el-empty v-else description="暂无版本历史" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
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
const compareVersion1 = ref(null)
const compareVersion2 = ref(null)
const showDiff = ref(false)
const diffResult = ref(null)
const viewingVersion = ref(null)

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
const createNewVersionOnSave = ref(true) // 默认保存时创建新版本

const quillOptions = {
  placeholder: '请输入合同内容...',
  modules: {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'font': [] }],
      [{ 'size': [] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'script': 'sub' }, { 'script': 'super' }],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      [{ 'indent': '-1' }, { 'indent': '+1' }],
      [{ 'direction': 'rtl' }],
      [{ 'align': [] }],
      ['link', 'image', 'video'],
      ['clean']
    ]
  }
}

const formRules = {
  title: [{ required: true, message: '请输入合同标题', trigger: 'blur' }],
  contract_type: [{ required: true, message: '请选择合同类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const isEditQuery = computed(() => route.query.edit === 'true')

// 格式化合同内容用于显示
const displayContentType = computed(() => {
  if (!contract.value.content) return 'empty'
  
  const content = contract.value.content
  
  // 如果是字符串
  if (typeof content === 'string') {
    // 检查是否包含HTML标签
    if (content.includes('<') && content.includes('>')) {
      return 'html'
    }
    return 'text'
  }
  
  // 如果是对象
  if (typeof content === 'object' && content !== null) {
    // 如果有html字段，使用HTML显示
    if (content.html) {
      return 'html'
    }
    // 如果有text字段，使用文本显示
    if (content.text) {
      return 'text'
    }
    // 否则使用JSON显示
    return 'json'
  }
  
  return 'json'
})

// 格式化后的内容
const formattedContent = computed(() => {
  if (!contract.value.content) return ''
  
  const content = contract.value.content
  
  // 如果是字符串
  if (typeof content === 'string') {
    // 如果是HTML，直接返回
    if (content.includes('<') && content.includes('>')) {
      return content
    }
    // 否则处理换行符
    return content.replace(/\\n/g, '\n')
  }
  
  // 如果是对象
  if (typeof content === 'object' && content !== null) {
    // 如果有html字段，使用HTML
    if (content.html) {
      return content.html
    }
    // 如果有text字段，处理换行符
    if (content.text) {
      return content.text.replace(/\\n/g, '\n')
    }
    // 否则格式化为JSON
    return JSON.stringify(content, null, 2)
  }
  
  return String(content)
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

// 将文本转换为 HTML 格式
const textToHtml = (text) => {
  if (!text) return ''
  // 将 \n\n 转换为段落分隔
  // 将单个 \n 转换为 <br>
  return text
    .split(/\n\s*\n/) // 按双换行分割段落
    .map(para => para.trim())
    .filter(para => para.length > 0)
    .map(para => {
      // 将段落内的单个换行转换为 <br>
      const lines = para.split('\n')
      return `<p>${lines.join('<br>')}</p>`
    })
    .join('')
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
  
  // 处理合同内容
  if (typeof contract.value.content === 'object' && contract.value.content !== null) {
    // 如果内容对象有 html 字段，使用富文本模式
    if (contract.value.content.html) {
      contentEditMode.value = 'rich'
      richContent.value = contract.value.content.html || ''
      contentText.value = JSON.stringify(contract.value.content, null, 2)
    } else if (contract.value.content.text) {
      // 如果有 text 字段但没有 html，将 text 转换为 HTML
      contentEditMode.value = 'rich'
      richContent.value = textToHtml(contract.value.content.text)
      // 更新 contentText 以包含转换后的 HTML
      const updatedContent = {
        ...contract.value.content,
        html: richContent.value
      }
      contentText.value = JSON.stringify(updatedContent, null, 2)
    } else {
      // 否则使用 JSON 模式
      contentEditMode.value = 'json'
      contentText.value = JSON.stringify(contract.value.content, null, 2)
      richContent.value = ''
    }
  } else if (contract.value.content) {
    // 如果内容是字符串，尝试判断是否为 HTML
    const contentStr = String(contract.value.content)
    if (contentStr.includes('<') && contentStr.includes('>')) {
      // 看起来像 HTML，使用富文本模式
      contentEditMode.value = 'rich'
      richContent.value = contentStr
      contentText.value = contentStr
    } else {
      // 普通文本，转换为 HTML 并使用富文本模式
      contentEditMode.value = 'rich'
      richContent.value = textToHtml(contentStr)
      // 同时更新 JSON 格式
      const contentObj = {
        text: contentStr,
        html: richContent.value
      }
      contentText.value = JSON.stringify(contentObj, null, 2)
    }
  } else {
    // 没有内容，默认使用 JSON 模式
    contentEditMode.value = 'json'
    contentText.value = ''
    richContent.value = ''
  }
}

const handleCancelEdit = () => {
  isEditMode.value = false
  formRef.value?.resetFields()
  router.replace({ query: {} })
}

// 检查内容是否有变化
const hasContentChanged = () => {
  const originalContent = contract.value.content
  let newContent = null
  
  // 获取新内容
  if (contentEditMode.value === 'json') {
    if (contentText.value) {
      try {
        newContent = JSON.parse(contentText.value)
      } catch (e) {
        return false // JSON格式错误，不处理
      }
    }
  } else {
    // 富文本模式
    newContent = {
      html: richContent.value,
      text: richContent.value.replace(/<[^>]*>/g, ''),
    }
  }
  
  // 比较内容是否变化
  if (!originalContent && !newContent) {
    return false
  }
  if (!originalContent || !newContent) {
    return true
  }
  
  // 深度比较内容
  const originalStr = JSON.stringify(originalContent)
  const newStr = JSON.stringify(newContent)
  return originalStr !== newStr
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
        
        // 检查内容是否有变化
        const contentChanged = hasContentChanged()
        
        // 如果内容有变化且用户选择创建新版本，先创建新版本
        if (contentChanged && createNewVersionOnSave.value) {
          try {
            await api.post(`/contracts/contracts/${route.params.id}/create_version/`, {
              content: submitData.content,
              change_summary: '编辑合同内容',
            })
          } catch (error) {
            console.error('创建新版本失败:', error)
            // 即使创建版本失败，也继续保存
          }
        }
        
        // 更新合同
        await api.patch(`/contracts/contracts/${route.params.id}/`, submitData)
        
        if (contentChanged && createNewVersionOnSave.value) {
          ElMessage.success('保存成功，已创建新版本')
        } else {
          ElMessage.success('更新成功')
        }
        
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

// 已移除 handleCreateVersion 方法，改为在保存时自动创建新版本

// 监听编辑模式切换，同步内容
watch(contentEditMode, async (newMode) => {
  if (!isEditMode.value) return
  
  await nextTick()
  
  if (newMode === 'rich') {
    // 切换到富文本模式时，如果 JSON 内容有 html 字段，使用它
    if (contentText.value) {
      try {
        const parsed = JSON.parse(contentText.value)
        if (parsed && typeof parsed === 'object') {
          if (parsed.html) {
            richContent.value = parsed.html
          } else if (parsed.text) {
            // 如果有 text 但没有 html，将 text 转换为 HTML
            richContent.value = textToHtml(parsed.text)
            // 更新 JSON 以包含转换后的 HTML
            parsed.html = richContent.value
            contentText.value = JSON.stringify(parsed, null, 2)
          } else {
            // 如果没有 html 和 text，尝试将整个对象转换为字符串再转换
            const textStr = JSON.stringify(parsed, null, 2)
            richContent.value = textToHtml(textStr)
          }
        } else {
          // 如果不是对象，尝试作为文本处理
          richContent.value = textToHtml(String(parsed))
        }
      } catch (e) {
        // 如果 JSON 解析失败，将文本内容转换为 HTML
        richContent.value = textToHtml(contentText.value)
      }
    }
  } else {
    // 切换到 JSON 模式时，如果富文本有内容，更新 JSON
    if (richContent.value) {
      const textContent = richContent.value.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim()
      const contentObj = {
        html: richContent.value,
        text: textContent
      }
      contentText.value = JSON.stringify(contentObj, null, 2)
    }
  }
})

// 提取版本内容的文本
const extractVersionText = (version) => {
  if (!version || !version.content) return ''
  
  const content = version.content
  if (typeof content === 'string') {
    return content
  }
  if (typeof content === 'object') {
    if (content.text) {
      return content.text
    }
    if (content.html) {
      // 从HTML提取纯文本
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = content.html
      return tempDiv.textContent || tempDiv.innerText || ''
    }
    // 如果是其他对象，转换为字符串
    return JSON.stringify(content, null, 2)
  }
  return String(content)
}

// 简单的文本diff算法
const computeDiff = (oldText, newText) => {
  const oldLines = oldText.split('\n')
  const newLines = newText.split('\n')
  
  // 使用简单的LCS算法计算差异
  const result = {
    lines: [],
    stats: {
      added: 0,
      removed: 0,
      modified: 0
    }
  }
  
  // 创建差异矩阵
  const m = oldLines.length
  const n = newLines.length
  const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0))
  
  // 计算LCS
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (oldLines[i - 1] === newLines[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1])
      }
    }
  }
  
  // 回溯找出差异
  let i = m
  let j = n
  const diffLines = []
  
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && oldLines[i - 1] === newLines[j - 1]) {
      // 相同行
      diffLines.unshift({
        type: 'same',
        oldLine: i,
        newLine: j,
        content: escapeHtml(oldLines[i - 1])
      })
      i--
      j--
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      // 新增行
      diffLines.unshift({
        type: 'added',
        oldLine: null,
        newLine: j,
        content: escapeHtml(newLines[j - 1])
      })
      result.stats.added++
      j--
    } else if (i > 0) {
      // 删除行
      diffLines.unshift({
        type: 'removed',
        oldLine: i,
        newLine: null,
        content: escapeHtml(oldLines[i - 1])
      })
      result.stats.removed++
      i--
    }
  }
  
  // 优化：合并相邻的删除和新增，标记为修改
  const finalLines = []
  for (let k = 0; k < diffLines.length; k++) {
    const line = diffLines[k]
    const prevLine = k > 0 ? diffLines[k - 1] : null
    
    if (line.type === 'added' && prevLine && prevLine.type === 'removed') {
      // 相邻的删除和新增，合并为修改
      finalLines[finalLines.length - 1] = {
        type: 'modified',
        oldLine: prevLine.oldLine,
        newLine: line.newLine,
        content: prevLine.content,
        newContent: line.content
      }
      result.stats.modified++
      result.stats.added--
      result.stats.removed--
    } else {
      finalLines.push(line)
    }
  }
  
  result.lines = finalLines
  return result
}

// HTML转义
const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 高亮显示差异内容（简单的字符级diff）
const highlightDiff = (oldText, newText) => {
  // 简单的字符级对比
  const oldWords = oldText.split(/(\s+)/)
  const newWords = newText.split(/(\s+)/)
  
  // 找出不同的部分
  let i = 0
  let j = 0
  const result = []
  
  while (i < oldWords.length || j < newWords.length) {
    if (i < oldWords.length && j < newWords.length && oldWords[i] === newWords[j]) {
      result.push({ type: 'same', text: oldWords[i] })
      i++
      j++
    } else {
      // 找出不同的部分
      if (i < oldWords.length) {
        result.push({ type: 'removed', text: oldWords[i] })
        i++
      }
      if (j < newWords.length) {
        result.push({ type: 'added', text: newWords[j] })
        j++
      }
    }
  }
  
  return result.map(item => {
    if (item.type === 'same') {
      return escapeHtml(item.text)
    } else if (item.type === 'removed') {
      return `<span class="diff-removed-inline">${escapeHtml(item.text)}</span>`
    } else {
      return `<span class="diff-added-inline">${escapeHtml(item.text)}</span>`
    }
  }).join('')
}

// 版本对比
const handleVersionCompare = () => {
  if (!compareVersion1.value || !compareVersion2.value) {
    ElMessage.warning('请选择两个版本进行对比')
    return
  }
  
  if (compareVersion1.value === compareVersion2.value) {
    ElMessage.warning('请选择不同的版本进行对比')
    return
  }
  
  const version1 = versions.value.find(v => v.version === compareVersion1.value)
  const version2 = versions.value.find(v => v.version === compareVersion2.value)
  
  if (!version1 || !version2) {
    ElMessage.error('版本不存在')
    return
  }
  
  // 确保版本1是较新的版本
  let oldVersion = version1
  let newVersion = version2
  if (version1.version > version2.version) {
    oldVersion = version2
    newVersion = version1
  }
  
  const oldText = extractVersionText(oldVersion)
  const newText = extractVersionText(newVersion)
  
  diffResult.value = computeDiff(oldText, newText)
  showDiff.value = true
  
  // 滚动到对比区域
  nextTick(() => {
    const diffCard = document.querySelector('.diff-container')
    if (diffCard) {
      diffCard.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
}

// 快速对比（与上一个版本）
const quickCompare = (version1, version2) => {
  compareVersion1.value = version1
  compareVersion2.value = version2
  handleVersionCompare()
}

// 查看版本内容
const viewVersionContent = (version) => {
  viewingVersion.value = version
  // 可以打开一个对话框显示版本内容
  ElMessageBox.alert(
    formatVersionContent(version),
    `版本 ${version.version} 内容`,
    {
      confirmButtonText: '关闭',
      dangerouslyUseHTMLString: true,
      customClass: 'version-content-dialog'
    }
  )
}

// 格式化版本内容用于显示
const formatVersionContent = (version) => {
  const content = version.content
  if (!content) return '<p>暂无内容</p>'
  
  if (typeof content === 'string') {
    if (content.includes('<') && content.includes('>')) {
      return content
    }
    return `<pre style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(content)}</pre>`
  }
  
  if (typeof content === 'object') {
    if (content.html) {
      return content.html
    }
    if (content.text) {
      return `<pre style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(content.text)}</pre>`
    }
    return `<pre style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(JSON.stringify(content, null, 2))}</pre>`
  }
  
  return `<pre style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(String(content))}</pre>`
}

// 版本回滚
const handleRollback = async (version) => {
  try {
    // 使用prompt让用户输入回滚原因
    const { value: reason } = await ElMessageBox.prompt(
      `确定要回滚到版本 ${version.version} 吗？\n\n回滚后将：\n1. 恢复该版本的内容\n2. 创建新的版本记录\n3. 更新当前版本号\n\n请输入回滚原因（可选）：`,
      '确认回滚',
      {
        confirmButtonText: '确认回滚',
        cancelButtonText: '取消',
        type: 'warning',
        inputType: 'textarea',
        inputPlaceholder: '请输入回滚原因，如：需要恢复之前的合同条款...',
        inputValidator: (value) => {
          // 可选，不验证
          return true
        }
      }
    )
    
    // 执行回滚
    loading.value = true
    try {
      const response = await api.post(`/contracts/contracts/${route.params.id}/rollback/`, {
        version: version.version,
        reason: reason || ''
      })
      
      ElMessage.success({
        message: `已成功回滚到版本 ${version.version}，已创建新版本 ${response.data.new_version}`,
        duration: 5000
      })
      
      // 刷新合同数据
      await fetchContract()
      
      // 切换到版本历史标签
      activeTab.value = 'versions'
      
      // 滚动到顶部，显示最新版本
      nextTick(() => {
        const timeline = document.querySelector('.el-timeline')
        if (timeline) {
          timeline.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      })
    } catch (error) {
      const errorMsg = error.response?.data?.error || error.message || '回滚失败'
      ElMessage.error(`回滚失败: ${errorMsg}`)
    } finally {
      loading.value = false
    }
  } catch (error) {
    // 用户取消
    if (error !== 'cancel') {
      console.error('回滚确认失败:', error)
    }
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

.content-display {
  min-height: 200px;
}

.content-html {
  background-color: #ffffff;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.content-html :deep(p) {
  margin: 10px 0;
}

.content-html :deep(h1),
.content-html :deep(h2),
.content-html :deep(h3),
.content-html :deep(h4),
.content-html :deep(h5),
.content-html :deep(h6) {
  margin: 15px 0 10px 0;
  font-weight: bold;
}

.content-text {
  background-color: #ffffff;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.content-json {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  border: 1px solid #e4e7ed;
}

.quill-editor-wrapper {
  margin-bottom: 50px;
}

:deep(.quill-editor-wrapper .ql-container) {
  min-height: 300px;
  font-size: 14px;
}

:deep(.quill-editor-wrapper .ql-editor) {
  min-height: 300px;
}

:deep(.quill-editor-wrapper .ql-toolbar) {
  border-top: 1px solid #ccc;
  border-left: 1px solid #ccc;
  border-right: 1px solid #ccc;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
}

:deep(.quill-editor-wrapper .ql-container) {
  border-bottom: 1px solid #ccc;
  border-left: 1px solid #ccc;
  border-right: 1px solid #ccc;
  border-top: none;
  border-radius: 0 0 4px 4px;
}

.versions-container {
  padding: 10px 0;
}

.version-controls {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.diff-container {
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #ffffff;
}

.diff-content {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.diff-line {
  display: flex;
  padding: 2px 0;
  min-height: 20px;
}

.diff-line-number {
  display: inline-block;
  width: 50px;
  text-align: right;
  padding: 0 10px;
  color: #909399;
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  user-select: none;
  flex-shrink: 0;
}

.diff-content-text {
  flex: 1;
  padding: 0 10px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.diff-same {
  background-color: #ffffff;
}

.diff-added {
  background-color: #f0f9ff;
}

.diff-removed {
  background-color: #fef0f0;
}

.diff-modified {
  background-color: #fff7e6;
}

.diff-added .diff-content-text {
  color: #67c23a;
}

.diff-removed .diff-content-text {
  color: #f56c6c;
  text-decoration: line-through;
}

.diff-modified .diff-content-text {
  color: #e6a23c;
}

.diff-old-content {
  background-color: #fef0f0;
  color: #f56c6c;
  text-decoration: line-through;
  padding: 2px 4px;
  border-radius: 2px;
  margin-right: 5px;
}

.diff-new-content {
  background-color: #f0f9ff;
  color: #67c23a;
  padding: 2px 4px;
  border-radius: 2px;
  margin-left: 5px;
}

.diff-arrow {
  margin: 0 10px;
  color: #909399;
  font-weight: bold;
}

.diff-added-inline {
  background-color: #d4edda;
  color: #155724;
  padding: 2px 4px;
  border-radius: 2px;
}

.diff-removed-inline {
  background-color: #f8d7da;
  color: #721c24;
  padding: 2px 4px;
  border-radius: 2px;
  text-decoration: line-through;
}

:deep(.version-content-dialog) {
  width: 80%;
  max-width: 900px;
}

:deep(.version-content-dialog .el-message-box__content) {
  max-height: 600px;
  overflow-y: auto;
}
</style>

