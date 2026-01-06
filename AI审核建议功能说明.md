# AI审核建议功能说明

## 功能概述

在分层审核流程中，系统会根据审核员的层级和对应的审核重点配置，使用AI生成相应的审核建议，帮助审核员更高效、更准确地完成审核工作。

## 核心功能

1. **基于层级的AI建议生成**：根据审核员层级（一级/二级/三级）和审核重点配置，生成针对性的AI审核建议
2. **审核重点配置关联**：自动关联审核重点配置，确保AI建议符合该层级的审核要求
3. **审核建议保存**：将AI生成的建议保存到审核结果中，方便审核员查看和参考
4. **人工审核辅助**：为人工审核提供AI建议，提高审核效率和准确性

## 数据模型变更

### User模型
- 新增字段：`reviewer_level`（审核员层级）
  - 类型：CharField
  - 可选值：level1（一级审核员）、level2（二级审核员）、level3（三级审核员（高级））
  - 说明：仅当用户角色为审核员时有效

### ReviewTask模型
- 新增字段：`reviewer`（审核员）
  - 类型：ForeignKey(User)
  - 说明：关联到执行审核任务的审核员
- 新增字段：`reviewer_level`（审核员层级）
  - 类型：CharField
  - 说明：审核任务的审核员层级，用于确定使用哪个审核重点配置

## API接口

### 1. 生成AI审核建议

**接口地址：** `POST /api/reviews/ai-suggestions/generate/`

**请求参数：**
```json
{
    "contract_id": 1,
    "review_task_id": 1  // 可选
}
```

**响应示例：**
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
        "issues": [
            {
                "clause_id": "条款1",
                "clause_content": "合同主体信息",
                "issue_description": "合同主体信息不够详细",
                "risk_level": "low",
                "legal_basis": "《合同法》要求合同主体信息明确",
                "suggestion": "建议补充完整的合同主体信息"
            }
        ],
        "focus_points": [
            {
                "point": "格式规范",
                "status": "正常",
                "description": "合同格式符合要求"
            }
        ],
        "conclusion": "需要修改",
        "summary": "合同基础信息完整，但需要补充部分细节"
    }
}
```

### 2. 获取审核任务的AI建议

**接口地址：** `GET /api/reviews/ai-suggestions/get_by_task/?review_task_id=1`

**响应示例：**
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

## 使用流程

### 场景1：人工审核时获取AI建议

1. **审核员登录系统**
   - 确保用户角色为"审核员"且已设置审核员层级

2. **选择合同进行审核**
   - 审核员在审核任务列表中选择需要审核的合同

3. **生成AI建议**
   - 调用 `POST /api/reviews/ai-suggestions/generate/` 接口
   - 传入合同ID和审核任务ID（如果有）

4. **查看AI建议**
   - 系统返回基于该审核员层级的AI审核建议
   - 建议包含：总体评价、发现的问题、重点关注事项、审核结论

5. **参考AI建议进行审核**
   - 审核员参考AI建议，结合自己的专业判断进行审核
   - 可以采纳、修改或忽略AI建议

6. **提交审核意见**
   - 审核员提交自己的审核意见
   - AI建议已自动保存到审核结果中

### 场景2：自动审核任务

1. **创建审核任务**
   - 系统创建审核任务时，可以指定审核员和审核员层级

2. **自动生成AI建议**
   - 在审核任务处理过程中，自动调用AI服务生成建议
   - 根据审核员层级和审核重点配置生成针对性建议

3. **保存审核结果**
   - AI建议自动保存到审核结果中
   - 审核员可以查看AI建议作为参考

## AI服务配置

### 环境变量配置

在 `backend/config/settings.py` 中可以配置AI服务：

```python
# AI服务配置
AI_ENABLED = True  # 是否启用AI功能
AI_API_KEY = 'your-api-key'  # AI API密钥
AI_API_URL = 'https://api.openai.com/v1/chat/completions'  # AI API地址
AI_MODEL = 'gpt-3.5-turbo'  # AI模型名称
```

### AI服务实现

当前实现使用模拟数据，实际使用时需要：

1. **集成真实的AI API**
   - 支持OpenAI、文心一言、通义千问等
   - 在 `backend/apps/reviews/services.py` 的 `AIService._call_ai_api` 方法中实现

2. **优化提示词**
   - 根据审核重点配置构建更精准的提示词
   - 在 `AIService._build_prompt` 方法中优化

3. **处理AI响应**
   - 解析AI返回的JSON格式数据
   - 处理异常情况（API调用失败、响应格式错误等）

## 审核建议数据结构

### 总体结构
```json
{
    "overall_evaluation": "总体评价文本",
    "issues": [
        {
            "clause_id": "条款ID或位置",
            "clause_content": "条款内容",
            "issue_description": "问题描述",
            "risk_level": "high/medium/low",
            "legal_basis": "法律依据",
            "suggestion": "修改建议"
        }
    ],
    "focus_points": [
        {
            "point": "关注点名称",
            "status": "正常/异常/需关注",
            "description": "说明"
        }
    ],
    "conclusion": "通过/不通过/需要修改",
    "summary": "审核摘要"
}
```

### 问题（Issue）字段说明
- `clause_id`: 条款ID或位置标识
- `clause_content`: 相关条款的内容
- `issue_description`: 发现的问题描述
- `risk_level`: 风险等级（high/medium/low）
- `legal_basis`: 法律依据或规则依据
- `suggestion`: 具体的修改建议

### 关注点（Focus Point）字段说明
- `point`: 关注点名称（对应审核重点配置中的focus_points）
- `status`: 状态（正常/异常/需关注）
- `description`: 对该关注点的说明

## 前端集成建议

### 1. 审核页面显示AI建议

在审核页面中，可以：
- 显示AI生成的总体评价
- 列出发现的问题和建议
- 显示重点关注事项的状态
- 展示审核结论

### 2. AI建议与人工审核意见对比

可以设计对比视图：
- 左侧显示AI建议
- 右侧显示审核员的审核意见
- 支持审核员参考AI建议，但不强制采纳

### 3. AI建议采纳功能

可以添加功能：
- 一键采纳AI建议作为审核意见
- 修改AI建议后采纳
- 忽略AI建议

## 注意事项

1. **审核员层级设置**
   - 确保审核员用户已正确设置 `reviewer_level` 字段
   - 只有设置了层级的审核员才能使用AI建议功能

2. **审核重点配置**
   - 确保每个层级都有对应的审核重点配置
   - 配置必须处于启用状态（is_active=True）

3. **AI服务可用性**
   - 如果AI服务不可用，系统会返回模拟数据
   - 建议在生产环境中配置真实的AI服务

4. **数据隐私和安全**
   - 合同内容会发送到AI服务，注意数据隐私保护
   - 建议使用企业级AI服务，确保数据安全

5. **审核建议的准确性**
   - AI建议仅供参考，不能完全替代人工审核
   - 审核员需要结合专业判断，对AI建议进行验证

## 后续优化方向

1. **AI模型优化**
   - 使用专门针对合同审核训练的模型
   - 提高建议的准确性和专业性

2. **建议个性化**
   - 根据审核员的历史审核记录，优化建议内容
   - 学习审核员的审核偏好和习惯

3. **多轮对话**
   - 支持审核员与AI进行多轮对话
   - 针对特定问题进行深入分析

4. **建议评分**
   - 对AI建议进行评分
   - 根据采纳率优化AI建议质量

---

**创建时间**：2024年12月22日  
**功能状态**：已实现（使用模拟数据，待集成真实AI服务）

