# GitHub上传指南

## 当前状态

项目已经配置了Git仓库，远程仓库地址为：
```
https://github.com/LjkGitHub1/contract_review.git
```

当前分支：`main`
远程分支：`origin/main`

## 上传步骤

### 方法一：使用命令行（推荐）

#### 1. 确保所有更改已提交

```bash
# 检查状态
git status

# 添加所有更改
git add .

# 提交更改
git commit -m "添加部署文档并更新后端端口为8897"
```

#### 2. 推送到GitHub

```bash
# 推送到main分支
git push origin main

# 如果需要推送到其他分支（如当前的功能分支）
git push origin 2025-12-23-xxnq-c8881
```

#### 3. 如果遇到网络问题

如果连接GitHub失败，可以尝试：

```bash
# 使用SSH方式（需要配置SSH密钥）
git remote set-url origin git@github.com:LjkGitHub1/contract_review.git
git push origin main

# 或者配置代理（如果有）
git config --global http.proxy http://proxy-server:port
git config --global https.proxy https://proxy-server:port
```

### 方法二：使用GitHub Desktop

1. 下载并安装 [GitHub Desktop](https://desktop.github.com/)
2. 打开GitHub Desktop
3. 选择 "File" -> "Add Local Repository"
4. 选择项目目录：`D:\AI合同`
5. 在GitHub Desktop中：
   - 查看所有更改
   - 填写提交信息
   - 点击 "Commit to main"
   - 点击 "Push origin" 推送到GitHub

### 方法三：使用VS Code

1. 在VS Code中打开项目
2. 点击左侧的源代码管理图标（或按 `Ctrl+Shift+G`）
3. 在"源代码管理"面板中：
   - 查看所有更改
   - 在消息框中输入提交信息
   - 点击"提交"按钮（✓）
   - 点击"同步更改"或"推送"按钮

## 需要上传的文件

确保以下重要文件已包含：

### 后端文件
- ✅ `backend/` - 所有Django应用代码
- ✅ `backend/requirements.txt` - Python依赖
- ✅ `backend/config/settings.py` - Django配置
- ✅ `backend/.env.example` - 环境变量示例（不要上传.env）

### 前端文件
- ✅ `frontend/src/` - Vue源代码
- ✅ `frontend/package.json` - Node依赖
- ✅ `frontend/vite.config.js` - Vite配置

### 文档文件
- ✅ `README.md` - 项目说明
- ✅ `部署文档.md` - 部署指南
- ✅ `项目说明.md` - 项目详细说明
- ✅ `环境要求.md` - 环境配置要求
- ✅ `数据库设计文档.md` - 数据库设计

### 配置文件
- ✅ `.gitignore` - Git忽略规则
- ✅ `start_backend.bat` - 后端启动脚本
- ✅ `start_frontend.bat` - 前端启动脚本
- ✅ `start_celery.bat` - Celery启动脚本

## 不应上传的文件

确保 `.gitignore` 已正确配置，以下文件不应上传：

- ❌ `backend/.env` - 环境变量（包含敏感信息）
- ❌ `backend/venv/` - Python虚拟环境
- ❌ `backend/__pycache__/` - Python缓存
- ❌ `backend/media/` - 上传的文件
- ❌ `backend/staticfiles/` - 静态文件
- ❌ `backend/logs/` - 日志文件
- ❌ `frontend/node_modules/` - Node依赖
- ❌ `frontend/dist/` - 构建产物
- ❌ `.vscode/` - VS Code配置
- ❌ `.idea/` - IDE配置

## 验证上传

上传完成后，访问GitHub仓库检查：
```
https://github.com/LjkGitHub1/contract_review
```

确认以下内容：
- [ ] 所有源代码文件已上传
- [ ] 所有文档文件已上传
- [ ] `.gitignore` 正确配置
- [ ] 敏感文件（.env）未上传
- [ ] README.md 显示正确

## 常见问题

### 1. 网络连接失败

**问题**：`Failed to connect to github.com port 443`

**解决方案**：
- 检查网络连接
- 使用VPN或代理
- 尝试使用SSH方式连接
- 检查防火墙设置

### 2. 认证失败

**问题**：`Authentication failed`

**解决方案**：
- 使用Personal Access Token（推荐）
  - GitHub Settings -> Developer settings -> Personal access tokens
  - 生成新token，权限选择 `repo`
  - 使用token作为密码
- 或配置SSH密钥

### 3. 大文件上传失败

**问题**：某些文件太大无法上传

**解决方案**：
- 检查是否有大文件（如.docx, .pdf等）
- 考虑使用Git LFS（Large File Storage）
- 或将大文件移到其他地方

### 4. 分支冲突

**问题**：`Updates were rejected`

**解决方案**：
```bash
# 先拉取远程更改
git pull origin main

# 解决冲突后
git push origin main
```

## 后续操作

上传成功后，建议：

1. **创建Release**
   - 在GitHub仓库页面点击 "Releases"
   - 创建新版本标签（如 v1.0.0）
   - 添加发布说明

2. **设置仓库描述**
   - 在仓库设置中添加项目描述
   - 添加主题标签
   - 设置可见性（公开/私有）

3. **添加README徽章**
   - 在README.md中添加构建状态、版本等徽章

4. **配置GitHub Actions**（可选）
   - 设置CI/CD流程
   - 自动化测试和部署

## 联系信息

如有问题，请查看：
- GitHub文档：https://docs.github.com
- Git文档：https://git-scm.com/doc

---

**最后更新**：2024年12月

