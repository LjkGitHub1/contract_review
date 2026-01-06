# AI模型配置功能说明

## 功能概述

AI模型配置功能允许系统管理员配置AI大模型接口，支持硅基流动、OpenAI等模型服务提供商。可以创建多个配置，并设置其中一个为系统默认配置。

## 核心功能

1. **多提供商支持**：支持硅基流动、OpenAI、Anthropic等
2. **模型管理**：可以配置多个可用模型，并选择默认模型
3. **参数配置**：支持配置温度、最大Token数、超时时间等参数
4. **默认配置**：可以设置一个配置为系统默认，AI服务会自动使用默认配置
5. **连接测试**：可以测试API连接是否正常

## 数据模型

### AIModelConfig（AI模型配置表）

**字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| name | CharField | 配置名称（唯一） |
| provider | CharField | 服务提供商（siliconflow/openai/anthropic/custom） |
| api_key | CharField | API密钥 |
| api_base_url | CharField | API基础地址（默认：https://api.siliconflow.cn/v1） |
| available_models | JSONField | 可用模型列表（JSON数组） |
| default_model | CharField | 默认模型（从可用模型列表中选择） |
| is_active | BooleanField | 是否启用 |
| is_default | BooleanField | 是否系统默认（只能有一个） |
| description | TextField | 配置描述 |
| temperature | FloatField | 温度参数（0-2，默认0.7） |
| max_tokens | IntegerField | 最大Token数（默认2000） |
| timeout | IntegerField | 超时时间（秒，默认30） |
| created_by | ForeignKey | 创建人 |
| updated_by | ForeignKey | 更新人 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

## API接口

### 1. 获取配置列表
```
GET /api/reviews/ai-model-configs/
```

### 2. 创建配置
```
POST /api/reviews/ai-model-configs/
Content-Type: application/json

{
  "name": "硅基流动配置",
  "provider": "siliconflow",
  "api_key": "your-api-key",
  "api_base_url": "https://api.siliconflow.cn/v1",
  "available_models": ["deepseek-chat", "qwen-plus"],
  "default_model": "deepseek-chat",
  "temperature": 0.7,
  "max_tokens": 2000,
  "timeout": 30,
  "is_active": true,
  "is_default": true
}
```

### 3. 更新配置
```
PATCH /api/reviews/ai-model-configs/{id}/
```

### 4. 删除配置
```
DELETE /api/reviews/ai-model-configs/{id}/
```

### 5. 获取系统默认配置
```
GET /api/reviews/ai-model-configs/get_default/
```

### 6. 设置为系统默认
```
POST /api/reviews/ai-model-configs/{id}/set_default/
```

### 7. 测试连接
```
POST /api/reviews/ai-model-configs/{id}/test_connection/
```

### 8. 获取可用模型列表
```
GET /api/reviews/ai-model-configs/get_available_models/?provider=siliconflow
```

## 硅基流动配置示例

### 1. 获取API密钥

1. 访问 [硅基流动官网](https://siliconflow.cn)
2. 注册/登录账号
3. 在控制台获取API密钥

### 2. 配置参数

```json
{
  "name": "硅基流动配置",
  "provider": "siliconflow",
  "api_key": "sk-xxxxxxxxxxxxx",
  "api_base_url": "https://api.siliconflow.cn/v1",
  "available_models": [
    "deepseek-chat",
    "deepseek-coder",
    "qwen-plus",
    "qwen-turbo",
    "qwen-max",
    "glm-4",
    "chatgpt-3.5-turbo",
    "gpt-4"
  ],
  "default_model": "deepseek-chat",
  "temperature": 0.7,
  "max_tokens": 2000,
  "timeout": 30,
  "is_active": true,
  "is_default": true
}
```

### 3. 常用模型说明

- **deepseek-chat**: DeepSeek对话模型，适合通用对话和审核任务
- **deepseek-coder**: DeepSeek代码模型，适合代码相关任务
- **qwen-plus**: 通义千问Plus，性能较强
- **qwen-turbo**: 通义千问Turbo，速度较快
- **qwen-max**: 通义千问Max，性能最强
- **glm-4**: GLM-4模型
- **chatgpt-3.5-turbo**: ChatGPT 3.5 Turbo兼容模型
- **gpt-4**: GPT-4兼容模型

## 前端页面

### 页面路径
`/ai-model-config`

### 功能特性

1. **配置列表展示**
   - 显示所有AI模型配置
   - 显示配置名称、服务提供商、默认模型、状态等信息
   - 支持编辑、删除、设为默认、测试连接等操作

2. **创建/编辑配置**
   - 选择服务提供商（硅基流动/OpenAI/Anthropic/自定义）
   - 输入API密钥和API基础地址
   - 选择可用模型（支持多选）
   - 选择默认模型
   - 配置温度、最大Token数、超时时间等参数
   - 设置是否启用和是否系统默认

3. **模型选择**
   - 点击"选择模型"按钮打开模型选择对话框
   - 支持多选模型
   - 已选择的模型会显示为标签，可以删除

4. **连接测试**
   - 点击"测试连接"按钮测试API连接
   - 显示测试结果（成功/失败）

## AI服务集成

### 自动使用默认配置

AI服务类（`AIService`）会自动从数据库获取默认配置：

```python
from apps.reviews.services import AIService

# 自动使用默认配置
ai_service = AIService()

# 或指定配置
from apps.reviews.models import AIModelConfig
config = AIModelConfig.objects.get(name='硅基流动配置')
ai_service = AIService(config=config)
```

### 配置更新

当更新AI模型配置后，新的配置会立即生效，无需重启服务。

## 使用流程

### 1. 创建配置

1. 访问 `/ai-model-config` 页面
2. 点击"新建配置"按钮
3. 填写配置信息：
   - 配置名称：如"硅基流动配置"
   - 服务提供商：选择"硅基流动"
   - API密钥：输入从硅基流动获取的API密钥
   - API基础地址：默认 `https://api.siliconflow.cn/v1`
   - 选择模型：点击"选择模型"，选择需要的模型
   - 默认模型：从已选择的模型中选择一个作为默认
   - 其他参数：根据需要调整温度、最大Token数等
4. 点击"确定"保存

### 2. 设置为系统默认

1. 在配置列表中，点击"设为默认"按钮
2. 系统会自动将其他配置的"系统默认"状态取消
3. 该配置将成为系统默认配置，AI服务会自动使用

### 3. 测试连接

1. 在配置列表中，点击"测试连接"按钮
2. 系统会发送测试请求到API
3. 显示测试结果（成功/失败）

### 4. 使用配置

配置完成后，AI服务会自动使用系统默认配置。在生成AI审核建议时，会使用配置的模型和参数。

## 注意事项

1. **API密钥安全**：API密钥会加密存储，但建议定期更换
2. **默认配置唯一性**：只能有一个配置为系统默认
3. **模型可用性**：确保选择的模型在服务提供商中可用
4. **参数设置**：
   - 温度参数：0-2，值越大输出越随机，建议0.7
   - 最大Token数：根据需求设置，建议2000-4000
   - 超时时间：根据网络情况设置，建议30-60秒
5. **连接测试**：配置完成后建议先测试连接，确保配置正确

## 数据库迁移

运行以下命令创建数据库迁移：

```bash
cd backend
python manage.py makemigrations reviews
python manage.py migrate
```

## 后续优化方向

1. **模型列表自动获取**：从API自动获取可用模型列表
2. **配置导入导出**：支持批量导入导出配置
3. **使用统计**：统计各配置的使用情况
4. **成本监控**：监控API调用成本和Token使用量
5. **多配置切换**：支持在不同场景使用不同配置

---

**创建时间**：2024年12月22日  
**功能状态**：已实现

