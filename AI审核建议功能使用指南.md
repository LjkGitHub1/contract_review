# AI审核建议功能使用指南

## 快速开始

### 1. 数据库迁移

运行以下命令创建数据库迁移：

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 2. 设置审核员层级

为审核员用户设置层级：

```python
# 在Django shell中执行
from apps.users.models import User

# 设置一级审核员
user1 = User.objects.get(username='reviewer1')
user1.role = 'reviewer'
user1.reviewer_level = 'level1'
user1.save()

# 设置二级审核员
user2 = User.objects.get(username='reviewer2')
user2.role = 'reviewer'
user2.reviewer_level = 'level2'
user2.save()

# 设置三级审核员
user3 = User.objects.get(username='reviewer3')
user3.role = 'reviewer'
user3.reviewer_level = 'level3'
user3.save()
```

### 3. 填充审核重点配置

运行测试数据填充命令：

```bash
python manage.py fill_review_focus_config
```

## API使用示例

### 示例1：生成AI审核建议

**请求：**
```bash
curl -X POST http://localhost:8897/api/reviews/ai-suggestions/generate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "contract_id": 1,
    "review_task_id": 1
  }'
```

**响应：**
```json
{
    "reviewer_level": "level1",
    "reviewer_level_name": "一级审核员",
    "focus_config": {
        "level": "level1",
        "level_name": "一级审核员",
        "focus_points": ["格式规范", "基础条款完整性", "基本信息准确性"],
        "review_standards": "符合合同格式要求，基础信息准确完整"
    },
    "suggestions": {
        "overall_evaluation": "合同格式基本规范，基础信息完整...",
        "issues": [...],
        "focus_points": [...],
        "conclusion": "需要修改",
        "summary": "..."
    }
}
```

### 示例2：获取审核任务的AI建议

**请求：**
```bash
curl -X GET "http://localhost:8897/api/reviews/ai-suggestions/get_by_task/?review_task_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
    "review_task_id": 1,
    "reviewer_level": "level1",
    "generated_at": "2024-12-22T10:00:00Z",
    "suggestions": {
        "overall_evaluation": "...",
        "issues": [...],
        "focus_points": [...],
        "conclusion": "需要修改",
        "summary": "..."
    }
}
```

## 前端集成示例

### Vue组件示例

```vue
<template>
  <div class="ai-suggestions">
    <el-button @click="generateSuggestions" :loading="loading">
      生成AI审核建议
    </el-button>
    
    <div v-if="suggestions" class="suggestions-content">
      <h3>AI审核建议</h3>
      
      <el-card>
        <h4>总体评价</h4>
        <p>{{ suggestions.overall_evaluation }}</p>
      </el-card>
      
      <el-card>
        <h4>发现的问题</h4>
        <el-table :data="suggestions.issues">
          <el-table-column prop="clause_id" label="条款ID" />
          <el-table-column prop="issue_description" label="问题描述" />
          <el-table-column prop="risk_level" label="风险等级" />
          <el-table-column prop="suggestion" label="修改建议" />
        </el-table>
      </el-card>
      
      <el-card>
        <h4>审核结论</h4>
        <p>{{ suggestions.conclusion }}</p>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  name: 'AISuggestions',
  props: {
    contractId: {
      type: Number,
      required: true
    },
    reviewTaskId: {
      type: Number,
      default: null
    }
  },
  setup(props) {
    const loading = ref(false)
    const suggestions = ref(null)
    
    const generateSuggestions = async () => {
      loading.value = true
      try {
        const response = await axios.post('/api/reviews/ai-suggestions/generate/', {
          contract_id: props.contractId,
          review_task_id: props.reviewTaskId
        })
        suggestions.value = response.data.suggestions
      } catch (error) {
        console.error('生成AI建议失败:', error)
        this.$message.error('生成AI建议失败')
      } finally {
        loading.value = false
      }
    }
    
    return {
      loading,
      suggestions,
      generateSuggestions
    }
  }
}
</script>
```

## 工作流程

### 人工审核流程

1. **审核员登录系统**
   - 确保用户角色为"审核员"且已设置审核员层级

2. **选择审核任务**
   - 在审核任务列表中选择需要审核的合同

3. **查看合同内容**
   - 打开合同详情页面，查看合同内容

4. **生成AI建议**
   - 点击"生成AI审核建议"按钮
   - 系统根据审核员层级和审核重点配置生成建议

5. **参考AI建议进行审核**
   - 查看AI生成的总体评价、问题列表、重点关注事项
   - 结合AI建议和自己的专业判断进行审核

6. **提交审核意见**
   - 填写审核意见
   - 可以选择采纳、修改或忽略AI建议
   - 提交审核结果

### 自动审核流程

1. **创建审核任务**
   - 系统自动创建审核任务
   - 指定审核员和审核员层级

2. **自动生成AI建议**
   - 在审核任务处理过程中，自动调用AI服务
   - 根据审核员层级生成针对性建议

3. **保存审核结果**
   - AI建议自动保存到审核结果中
   - 审核员可以查看AI建议作为参考

## 配置说明

### AI服务配置（可选）

在 `backend/config/settings.py` 中配置：

```python
# AI服务配置
AI_ENABLED = True  # 是否启用AI功能（默认False，使用模拟数据）
AI_API_KEY = 'your-api-key'  # AI API密钥
AI_API_URL = 'https://api.openai.com/v1/chat/completions'  # AI API地址
AI_MODEL = 'gpt-3.5-turbo'  # AI模型名称
```

### 集成真实AI服务

修改 `backend/apps/reviews/services.py` 中的 `_call_ai_api` 方法：

```python
def _call_ai_api(self, prompt: str) -> Dict:
    """调用真实的AI API"""
    import openai
    
    openai.api_key = self.api_key
    response = openai.ChatCompletion.create(
        model=self.model,
        messages=[
            {"role": "system", "content": "你是一位专业的合同审核专家。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    # 解析响应
    content = response.choices[0].message.content
    return json.loads(content)
```

## 注意事项

1. **审核员层级必须设置**：只有设置了层级的审核员才能使用AI建议功能
2. **审核重点配置必须存在**：确保每个层级都有对应的审核重点配置
3. **AI服务可用性**：如果AI服务不可用，系统会返回模拟数据
4. **数据隐私**：合同内容会发送到AI服务，注意数据隐私保护
5. **建议仅供参考**：AI建议不能完全替代人工审核，需要审核员结合专业判断

---

**创建时间**：2024年12月22日

