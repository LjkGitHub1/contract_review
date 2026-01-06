<template>
  <div class="chat-window">
    <el-card class="chat-card" :body-style="{ padding: 0, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }">
      <template #header>
        <div class="chat-header">
          <div class="header-left">
            <el-icon style="font-size: 20px; color: #409EFF; margin-right: 8px"><ChatDotRound /></el-icon>
            <span style="font-size: 18px; font-weight: 500">AI智能助手</span>
            <el-tag v-if="currentModel" size="small" style="margin-left: 10px" type="info">
              {{ currentModel }}
            </el-tag>
          </div>
          <div class="header-right">
            <el-button
              size="small"
              :icon="Delete"
              @click="clearChat"
              :disabled="messages.length === 0"
            >
              清空对话
            </el-button>
          </div>
        </div>
      </template>

      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <el-icon style="font-size: 64px; color: #C0C4CC; margin-bottom: 16px"><ChatDotRound /></el-icon>
          <p style="color: #909399; font-size: 14px">开始与AI助手对话吧！</p>
          <p style="color: #C0C4CC; font-size: 12px; margin-top: 8px">我可以帮您解答合同审核相关问题</p>
        </div>
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message-item', message.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <div class="message-avatar">
            <el-icon v-if="message.role === 'user'" style="font-size: 20px; color: #409EFF"><User /></el-icon>
            <el-icon v-else style="font-size: 20px; color: #67C23A"><Cpu /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        <div v-if="loading" class="message-item ai-message">
          <div class="message-avatar">
            <el-icon class="is-loading" style="font-size: 20px; color: #67C23A"><Loading /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text">
              <span class="typing-indicator">
                <span></span><span></span><span></span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入您的问题..."
          @keydown.ctrl.enter="sendMessage"
          @keydown.meta.enter="sendMessage"
          :disabled="loading"
          resize="none"
        />
        <div class="input-actions">
          <div class="input-tips">
            <span style="color: #909399; font-size: 12px">按 Ctrl+Enter 或 Cmd+Enter 发送</span>
          </div>
          <el-button
            type="primary"
            :icon="Promotion"
            @click="sendMessage"
            :loading="loading"
            :disabled="!inputMessage.trim() || loading"
          >
            发送
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound, User, Cpu, Loading, Delete, Promotion } from '@element-plus/icons-vue'
import api from '@/utils/api'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const currentModel = ref('')

// 获取当前使用的AI模型
const fetchCurrentModel = async () => {
  try {
    const response = await api.get('/reviews/ai-model-configs/')
    const configs = response.data.results || []
    const defaultConfig = configs.find(c => c.is_default && c.is_active)
    if (defaultConfig) {
      currentModel.value = defaultConfig.default_model || '未配置'
    }
  } catch (error) {
    console.error('获取AI模型配置失败:', error)
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) {
    return
  }

  const userMessage = {
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const question = inputMessage.value.trim()
  inputMessage.value = ''
  loading.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    const response = await api.post('/reviews/ai-model-configs/chat/', {
      message: question,
      history: messages.value.slice(0, -1).map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    })

    const aiMessage = {
      role: 'assistant',
      content: response.data.response || response.data.message || '抱歉，我无法回答这个问题。',
      timestamp: new Date()
    }

    messages.value.push(aiMessage)
  } catch (error) {
    console.error('发送消息失败:', error)
    const errorMessage = error.response?.data?.error || error.response?.data?.detail || '发送消息失败，请稍后重试'
    ElMessage.error(errorMessage)
    
    const errorMsg = {
      role: 'assistant',
      content: `抱歉，发生了错误：${errorMessage}`,
      timestamp: new Date()
    }
    messages.value.push(errorMsg)
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 清空对话
const clearChat = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有对话记录吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    messages.value = []
    ElMessage.success('对话已清空')
  } catch (error) {
    // 用户取消
  }
}

// 格式化消息内容（支持Markdown和换行）
const formatMessage = (content) => {
  if (!content) return ''
  
  // 转义HTML
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 处理换行
  formatted = formatted.replace(/\n/g, '<br>')
  
  // 处理代码块（简单处理）
  formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  return formatted
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 监听消息变化，自动滚动
watch(() => messages.value.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

onMounted(() => {
  fetchCurrentModel()
})
</script>

<style scoped>
.chat-window {
  padding: 20px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

/* 确保 el-card 的 body 部分也能正确设置高度 */
.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
  padding: 0;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 0;
  max-height: 100%;
  position: relative;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background-color: #409EFF;
  color: white;
  margin-right: 12px;
  margin-left: 60px;
}

.ai-message .message-content {
  background-color: white;
  color: #303133;
  margin-left: 12px;
  margin-right: 60px;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background-color: #f0f2f5;
}

.user-message .message-avatar {
  background-color: #e6f4ff;
}

.ai-message .message-avatar {
  background-color: #f0f9ff;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  word-wrap: break-word;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-text {
  line-height: 1.6;
  font-size: 14px;
}

.message-text :deep(code) {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.user-message .message-text :deep(code) {
  background-color: rgba(255, 255, 255, 0.2);
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 6px;
}

.ai-message .message-time {
  color: #909399;
}

.typing-indicator {
  display: inline-flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #409EFF;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.input-container {
  padding: 16px;
  background-color: white;
  border-top: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-tips {
  flex: 1;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

