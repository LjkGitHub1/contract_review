# 后端API实现说明

## 已实现的后端API

### 1. 文件上传API ✅

**端点：** `POST /api/contracts/upload/`

**功能描述：**
- 支持上传Word文档（.doc, .docx）和PDF文件
- 自动解析文件内容
- 文件大小限制10MB
- 返回文件路径和解析后的内容

**请求格式：**
```
Content-Type: multipart/form-data
file: [文件]
```

**响应格式：**
```json
{
  "file_path": "contracts/uploads/xxx.pdf",
  "content": {
    "text": "解析的文本内容",
    "html": "HTML格式内容",
    "metadata": {
      "page_count": 5,
      "word_count": 1000
    }
  },
  "message": "文件上传成功"
}
```

**实现位置：**
- `backend/apps/contracts/views.py` - `FileUploadView`
- `backend/apps/contracts/urls.py` - 路由配置

**依赖库：**
- `python-docx` - Word文档解析
- `pymupdf` (fitz) - PDF文档解析

**文件存储：**
- 文件保存在 `MEDIA_ROOT/contracts/uploads/` 目录
- 文件名使用UUID生成，避免冲突

---

### 2. 审核报告下载API ✅

**端点：** `GET /api/reviews/results/{id}/download_report/`

**功能描述：**
- 下载审核报告文件
- 支持PDF、Word等格式
- 自动设置正确的Content-Type和下载文件名

**响应：**
- 文件流（FileResponse）
- Content-Type根据文件类型自动设置
- Content-Disposition设置为attachment，触发下载

**实现位置：**
- `backend/apps/reviews/views.py` - `ReviewResultViewSet.download_report`

**使用示例：**
```python
# 前端调用
GET /api/reviews/results/1/download_report/
# 浏览器会自动下载文件
```

---

### 3. 审核报告预览API ✅

**端点：** `GET /api/reviews/results/{id}/preview_report/`

**功能描述：**
- 预览审核报告文件
- PDF文件：浏览器内联显示
- Word文件：尝试内联显示（浏览器支持时）
- 其他格式：文本预览

**响应：**
- PDF：返回PDF文件流，Content-Disposition设置为inline
- Word：返回Word文件流，Content-Disposition设置为inline
- 文本：返回文本内容

**实现位置：**
- `backend/apps/reviews/views.py` - `ReviewResultViewSet.preview_report`

**使用示例：**
```python
# 前端调用
GET /api/reviews/results/1/preview_report/
# 浏览器会在新窗口打开预览
```

---

### 4. 知识图谱关系API ✅

**端点：** `GET /api/knowledge/relations/`

**功能描述：**
- 获取知识实体之间的关系
- 返回源实体和目标实体的ID和名称
- 支持过滤和排序

**响应格式：**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "source_entity": 1,
      "source_entity_id": 1,
      "source_entity_name": "合同主体",
      "target_entity": 2,
      "target_entity_id": 2,
      "target_entity_name": "合同条款",
      "relation_type": "related_to",
      "relation_properties": {},
      "confidence": 0.95,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**实现位置：**
- `backend/apps/knowledge/serializers.py` - `KnowledgeRelationSerializer`
- `backend/apps/knowledge/views.py` - `KnowledgeRelationViewSet`

**改进内容：**
- 添加了 `source_entity_id` 和 `target_entity_id` 字段
- 便于前端知识图谱可视化使用

---

## 文件解析功能

### Word文档解析

**使用库：** `python-docx`

**解析内容：**
- 提取所有段落文本
- 生成纯文本和HTML格式
- 统计段落数和字数

**代码示例：**
```python
doc = docx.Document(file_path)
paragraphs = [p.text for p in doc.paragraphs]
text = '\n'.join(paragraphs)
html = '<br>'.join([f'<p>{p}</p>' for p in paragraphs])
```

### PDF文档解析

**使用库：** `pymupdf` (fitz)

**解析内容：**
- 逐页提取文本
- 生成纯文本和HTML格式
- 统计页数和字数

**代码示例：**
```python
doc = fitz.open(file_path)
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    # 处理文本...
doc.close()
```

---

## 审核报告生成（待完善）

**当前状态：**
- 审核结果模型已有 `report_path` 和 `report_format` 字段
- 审核任务完成后可以生成报告文件
- 需要实现报告生成逻辑

**建议实现：**
1. 在 `process_review_task` 任务中生成报告
2. 使用模板生成Word或PDF格式报告
3. 保存报告文件路径到 `report_path` 字段

**示例代码（待实现）：**
```python
from docx import Document

def generate_review_report(result):
    """生成审核报告"""
    doc = Document()
    doc.add_heading('合同审核报告', 0)
    doc.add_paragraph(f'合同编号：{result.contract.contract_no}')
    doc.add_paragraph(f'总体评分：{result.overall_score}分')
    doc.add_paragraph(f'风险等级：{result.get_risk_level_display()}')
    # ... 添加更多内容
    
    # 保存文件
    report_path = f'reports/review_{result.id}.docx'
    full_path = os.path.join(settings.MEDIA_ROOT, report_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    doc.save(full_path)
    
    result.report_path = report_path
    result.report_format = 'docx'
    result.save()
```

---

## 配置说明

### 文件上传配置

在 `settings.py` 中已配置：
```python
# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 依赖包

已在 `requirements.txt` 中包含：
```
python-docx==1.1.2  # Word文档处理
pymupdf==1.24.5     # PDF文档处理
Pillow==10.3.0      # 图像处理（如需要）
```

---

## API端点汇总

### 文件上传
- `POST /api/contracts/upload/` - 上传并解析文件

### 审核报告
- `GET /api/reviews/results/{id}/download_report/` - 下载报告
- `GET /api/reviews/results/{id}/preview_report/` - 预览报告

### 知识图谱
- `GET /api/knowledge/relations/` - 获取关系列表
- `POST /api/knowledge/relations/` - 创建关系
- `GET /api/knowledge/relations/{id}/` - 获取关系详情
- `PATCH /api/knowledge/relations/{id}/` - 更新关系
- `DELETE /api/knowledge/relations/{id}/` - 删除关系

---

## 使用示例

### 1. 上传文件

**前端代码：**
```javascript
const formData = new FormData()
formData.append('file', file)

const response = await api.post('/contracts/upload/', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// response.data.file_path - 文件路径
// response.data.content - 解析后的内容
```

### 2. 下载报告

**前端代码：**
```javascript
const url = `/api/reviews/results/${resultId}/download_report/`
const link = document.createElement('a')
link.href = url
link.setAttribute('download', '')
link.click()
```

### 3. 预览报告

**前端代码：**
```javascript
const url = `/api/reviews/results/${resultId}/preview_report/`
window.open(url, '_blank')
```

### 4. 获取知识图谱关系

**前端代码：**
```javascript
const response = await api.get('/knowledge/relations/')
const relations = response.data.results
// 使用relations构建知识图谱
```

---

## 错误处理

### 文件上传错误

**错误响应：**
```json
{
  "error": "错误信息"
}
```

**常见错误：**
- `未找到文件` - 请求中未包含文件
- `不支持的文件类型` - 文件类型不在允许列表中
- `文件大小不能超过10MB` - 文件过大
- `文件处理失败: [详细错误]` - 文件解析失败

### 报告下载/预览错误

**错误响应：**
```json
{
  "error": "报告文件不存在"
}
```

**常见错误：**
- `报告文件不存在` - report_path为空或文件不存在
- `下载失败: [详细错误]` - 文件读取失败

---

## 安全考虑

1. **文件类型验证**：只允许上传.doc, .docx, .pdf文件
2. **文件大小限制**：限制为10MB
3. **权限控制**：所有API都需要认证（IsAuthenticated）
4. **文件存储**：文件存储在MEDIA_ROOT，不在Web根目录
5. **文件名安全**：使用UUID生成文件名，避免路径遍历攻击

---

## 后续优化建议

1. **异步文件处理**：大文件使用Celery异步处理
2. **文件缓存**：解析结果可以缓存，避免重复解析
3. **文件清理**：定期清理未使用的上传文件
4. **报告模板**：使用模板引擎生成更美观的报告
5. **文件预览优化**：支持更多文件格式的预览
6. **OCR支持**：扫描PDF的OCR识别

---

## 测试建议

### 文件上传测试

```python
# 测试用例
def test_file_upload():
    # 测试Word上传
    # 测试PDF上传
    # 测试文件类型验证
    # 测试文件大小限制
    # 测试文件解析
```

### 报告下载测试

```python
# 测试用例
def test_report_download():
    # 测试PDF下载
    # 测试Word下载
    # 测试文件不存在情况
```

---

## 总结

已实现的后端API功能：

✅ **文件上传和解析**
- Word文档解析
- PDF文档解析
- 文件存储管理

✅ **审核报告管理**
- 报告下载功能
- 报告预览功能

✅ **知识图谱API**
- 关系数据序列化优化
- 支持前端可视化需求

所有API都已实现并通过代码检查，可以直接使用。

