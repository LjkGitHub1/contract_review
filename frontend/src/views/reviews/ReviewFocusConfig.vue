<template>
  <div class="review-focus-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审核重点配置</span>
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
        <p>为不同层级的审核员配置审核重点，每个层级可以设置不同的审核着重点和关注事项。</p>
      </el-alert>

      <el-table :data="configs" v-loading="loading" style="width: 100%">
        <el-table-column prop="level" label="审核层级" width="150">
          <template #default="{ row }">
            {{ getLevelText(row.level) }}
          </template>
        </el-table-column>
        <el-table-column prop="level_name" label="层级名称" width="200" />
        <el-table-column prop="focus_description" label="审核重点描述" min-width="300" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="140px"
      >
        <el-form-item label="审核层级" prop="level">
          <el-select v-model="formData.level" placeholder="请选择审核层级" :disabled="isEdit">
            <el-option label="一级审核员" value="level1" />
            <el-option label="二级审核员" value="level2" />
            <el-option label="三级审核员（高级）" value="level3" />
          </el-select>
        </el-form-item>
        <el-form-item label="层级名称" prop="level_name">
          <el-input v-model="formData.level_name" placeholder="请输入层级名称" />
        </el-form-item>
        <el-form-item label="审核重点" prop="focus_points">
          <el-input
            v-model="focusPointsText"
            type="textarea"
            :rows="4"
            placeholder="请输入审核重点，每行一个重点项"
            @input="handleFocusPointsInput"
          />
          <div class="form-tip">每行一个重点项，系统会自动转换为列表</div>
        </el-form-item>
        <el-form-item label="审核重点描述" prop="focus_description">
          <el-input
            v-model="formData.focus_description"
            type="textarea"
            :rows="3"
            placeholder="请输入审核重点的详细描述"
          />
        </el-form-item>
        <el-form-item label="审核标准" prop="review_standards">
          <el-input
            v-model="formData.review_standards"
            type="textarea"
            :rows="3"
            placeholder="请输入审核标准"
          />
        </el-form-item>
        <el-form-item label="关注事项" prop="attention_items">
          <el-input
            v-model="attentionItemsText"
            type="textarea"
            :rows="4"
            placeholder="请输入关注事项，每行一个事项"
            @input="handleAttentionItemsInput"
          />
          <div class="form-tip">每行一个关注事项，系统会自动转换为列表</div>
        </el-form-item>
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
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
const configs = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const focusPointsText = ref('')
const attentionItemsText = ref('')

const dialogTitle = computed(() => (isEdit.value ? '编辑审核重点配置' : '新建审核重点配置'))

const formData = reactive({
  id: null,
  level: '',
  level_name: '',
  focus_points: [],
  focus_description: '',
  review_standards: '',
  attention_items: [],
  is_active: true,
})

const formRules = {
  level: [{ required: true, message: '请选择审核层级', trigger: 'change' }],
  level_name: [{ required: true, message: '请输入层级名称', trigger: 'blur' }],
  focus_points: [{ required: true, message: '请至少输入一个审核重点', trigger: 'change' }],
  focus_description: [{ required: true, message: '请输入审核重点描述', trigger: 'blur' }],
}

// 获取层级文本
const getLevelText = (level) => {
  const levelMap = {
    level1: '一级审核员',
    level2: '二级审核员',
    level3: '三级审核员（高级）',
  }
  return levelMap[level] || level
}

// 处理审核重点输入
const handleFocusPointsInput = (value) => {
  formData.focus_points = value
    .split('\n')
    .map(item => item.trim())
    .filter(item => item.length > 0)
}

// 处理关注事项输入
const handleAttentionItemsInput = (value) => {
  formData.attention_items = value
    .split('\n')
    .map(item => item.trim())
    .filter(item => item.length > 0)
}

// 加载配置列表
const loadConfigs = async () => {
  loading.value = true
  try {
    const response = await api.get('/reviews/focus-configs/')
    configs.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('加载配置列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 创建配置
const handleCreate = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑配置
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, {
    id: row.id,
    level: row.level,
    level_name: row.level_name,
    focus_points: row.focus_points || [],
    focus_description: row.focus_description,
    review_standards: row.review_standards || '',
    attention_items: row.attention_items || [],
    is_active: row.is_active,
  })
  focusPointsText.value = Array.isArray(row.focus_points) ? row.focus_points.join('\n') : ''
  attentionItemsText.value = Array.isArray(row.attention_items) ? row.attention_items.join('\n') : ''
  dialogVisible.value = true
}

// 删除配置
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该配置吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await api.delete(`/reviews/focus-configs/${row.id}/`)
    ElMessage.success('删除成功')
    loadConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    if (formData.focus_points.length === 0) {
      ElMessage.warning('请至少输入一个审核重点')
      return
    }
    
    submitting.value = true
    try {
      const data = {
        ...formData,
        focus_points: formData.focus_points,
        attention_items: formData.attention_items.length > 0 ? formData.attention_items : null,
      }
      
      if (isEdit.value) {
        await api.patch(`/reviews/focus-configs/${formData.id}/`, data)
        ElMessage.success('更新成功')
      } else {
        await api.post('/reviews/focus-configs/', data)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadConfigs()
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    id: null,
    level: '',
    level_name: '',
    focus_points: [],
    focus_description: '',
    review_standards: '',
    attention_items: [],
    is_active: true,
  })
  focusPointsText.value = ''
  attentionItemsText.value = ''
  formRef.value?.clearValidate()
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.review-focus-config {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>

