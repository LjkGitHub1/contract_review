# 快速导出流程图PNG方法

## 方法一：使用浏览器截图（最简单，推荐）

### 步骤：

1. **打开HTML文件**
   - 双击打开 `合同流程图.html` 文件（会在默认浏览器中打开）

2. **截图合同起草流程图**
   - 滚动到页面顶部，找到"一、合同起草流程图"部分
   - 按 `Windows键 + Shift + S`（Windows截图工具）
   - 或使用浏览器扩展（如FireShot、Awesome Screenshot）
   - 选择整个流程图区域
   - 保存为 `合同流程图_合同起草流程图.png`

3. **截图合同审核流程图**
   - 向下滚动，找到"二、合同审核流程图"部分
   - 使用相同方法截图
   - 保存为 `合同流程图_合同审核流程图.png`

## 方法二：使用浏览器打印功能

1. 打开 `合同流程图.html`
2. 按 `Ctrl + P` 打开打印对话框
3. 选择"另存为PDF"
4. 使用PDF转PNG工具（如在线工具或Adobe）将PDF转换为PNG

## 方法三：使用浏览器开发者工具

1. 打开 `合同流程图.html`
2. 按 `F12` 打开开发者工具
3. 找到流程图对应的 `<div class="diagram-container">` 元素
4. 右键点击该元素 → "Capture node screenshot"
5. 保存为PNG

## 方法四：使用Python脚本（需要安装库）

### 安装依赖：
```bash
pip install playwright
playwright install chromium
```

### 运行脚本：
```bash
python export_flowcharts_browser.py
```

## 方法五：使用在线工具

1. 打开 `合同流程图.html`
2. 复制SVG代码（在浏览器中右键 → 检查元素 → 找到 `<svg>` 标签）
3. 使用在线SVG转PNG工具：
   - https://svgtopng.com/
   - https://convertio.co/zh/svg-png/
4. 上传SVG代码或文件，转换为PNG

---

**推荐使用方法一（浏览器截图）**，最简单快捷！

