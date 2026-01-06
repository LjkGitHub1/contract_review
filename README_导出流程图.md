# 导出流程图为PNG - 快速指南

我已经为您创建了两个单独的HTML文件，方便您导出为PNG：

## 文件说明

1. **合同起草流程图.html** - 包含合同起草流程图
2. **合同审核流程图.html** - 包含合同审核流程图

## 最简单的导出方法（推荐）

### 方法一：使用浏览器截图

1. **打开HTML文件**
   - 双击 `合同起草流程图.html` 在浏览器中打开
   - 双击 `合同审核流程图.html` 在浏览器中打开

2. **截图**
   - **Windows**: 按 `Windows键 + Shift + S` 打开截图工具
   - **Mac**: 按 `Command + Shift + 4` 进行区域截图
   - 选择整个流程图区域
   - 保存为PNG格式

3. **保存文件**
   - 合同起草流程图 → 保存为 `合同流程图_合同起草流程图.png`
   - 合同审核流程图 → 保存为 `合同流程图_合同审核流程图.png`

### 方法二：使用浏览器打印功能

1. 打开HTML文件
2. 按 `Ctrl + P` (Windows) 或 `Command + P` (Mac)
3. 选择"另存为PDF"
4. 使用PDF转PNG工具转换为PNG

### 方法三：使用浏览器开发者工具

1. 打开HTML文件
2. 按 `F12` 打开开发者工具
3. 找到流程图容器（`<div class="diagram-container">`）
4. 右键点击 → "Capture node screenshot"
5. 保存为PNG

## 使用Python脚本（可选）

如果您想自动化导出，可以使用提供的Python脚本：

### 安装依赖
```bash
pip install playwright
playwright install chromium
```

### 运行脚本
```bash
python export_flowcharts_browser.py
```

---

**推荐使用方法一（浏览器截图）**，最简单快捷！

