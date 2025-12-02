# TURING PLANET ✖️ TECHSUM Newsletter

⚡ **Your weekly TechSum**: the most noteworthy tech stories — quick and clear.

一个现代化的技术新闻通讯订阅系统，支持订阅管理、邮件发送和后台管理。

**🌐 在线地址**: [https://web-production-914f7.up.railway.app/](https://web-production-914f7.up.railway.app/)

---

## 📋 目录

- [功能特性](#功能特性)
- [页面说明](#页面说明)
- [快速开始](#快速开始)
- [部署指南](#部署指南)
- [API 文档](#api-文档)
- [项目结构](#项目结构)
- [技术栈](#技术栈)

---

## ✨ 功能特性

- 📧 **新闻通讯生成**: 从多个来源获取技术亮点，生成精美的 HTML 新闻通讯
- 📬 **邮件发送**: 通过 Gmail 批量发送邮件，支持 MongoDB 订阅者管理
- 🌐 **Web 界面**: 
  - 订阅页面 - 用户注册订阅
  - 取消订阅页面 - 用户取消订阅
  - 后台管理面板 - 订阅者管理
- 💾 **MongoDB 集成**: 在 MongoDB Atlas 中存储和管理订阅者
- 🏷️ **标签系统**: 使用标签组织订阅者（preview、user 等）
- 🛡️ **反垃圾邮件**: 内置蜜罐（honeypot）机制防止机器人注册
- 📊 **实时统计**: 后台管理面板显示订阅者统计数据
- 🔐 **管理员认证**: 登录系统保护后台管理面板
- ✉️ **确认邮件**: 新订阅者自动收到欢迎确认邮件
- 📁 **周刊存档**: 每期周刊自动保存到 `output/` 文件夹，文件名格式为 `newsletter-YYYY-MM-DD.html`

---

## 📄 页面说明

### 1. 订阅页面 (Subscribe)

**访问地址**: 
- 生产环境: [https://web-production-914f7.up.railway.app/](https://web-production-914f7.up.railway.app/)
- 本地开发: `http://localhost:3000/`

**功能**:
- 用户输入邮箱地址订阅新闻通讯
- 实时表单验证
- 防机器人注册（蜜罐机制）
- 响应式设计，支持移动端
- **自动发送确认邮件**: 订阅成功后，系统会立即发送欢迎邮件给新订阅者

**特性**:
- 🚀 AI 筛选，来自 30+ 顶级发布商
- 🧭 可操作的摘要，几分钟内完成阅读
- 🛡️ 隐私保护，不共享数据
- ✉️ 订阅后立即收到欢迎确认邮件

---

### 2. 取消订阅页面 (Unsubscribe)

**访问地址**: 
- 生产环境: [https://web-production-914f7.up.railway.app/unsubscribe.html](https://web-production-914f7.up.railway.app/unsubscribe.html)
- 本地开发: `http://localhost:3000/unsubscribe.html`

**功能**:
- 用户输入邮箱取消订阅
- 可选原因选择（太频繁、不相关、太长、其他）
- 可选反馈意见
- 支持 URL 参数预填充邮箱（`?email=xxx`）

**取消订阅流程**:
1. 用户输入邮箱地址
2. 选择取消原因（可选）
3. 填写额外反馈（可选）
4. 确认取消订阅
5. 系统将订阅者状态设置为 `inactive`

---

### 3. 登录页面 (Login)

**访问地址**: 
- 生产环境: [https://web-production-914f7.up.railway.app/login.html](https://web-production-914f7.up.railway.app/login.html)
- 本地开发: `http://localhost:3000/login.html`

**功能**:
- 管理员登录认证
- 使用环境变量配置的用户名和密码
- Session 管理，登录状态保持 24 小时
- 未登录用户访问 admin 页面会自动重定向到登录页

**配置**:
在 `.env` 文件中设置：
```bash
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
SESSION_SECRET=your_session_secret_key
```

如果不设置，默认用户名为 `admin`，密码为 `admin123`（**仅用于开发环境，生产环境请务必修改**）

---

### 4. 后台管理面板 (Admin Dashboard)

**访问地址**: 
- 生产环境: [https://web-production-914f7.up.railway.app/admin.html](https://web-production-914f7.up.railway.app/admin.html)
- 本地开发: `http://localhost:3000/admin.html`

**安全**: 
- 需要登录才能访问
- 未登录用户会自动重定向到登录页面
- 支持登出功能

**功能**:

#### 📊 统计面板
- **总订阅者数**: 显示所有订阅者总数
- **活跃订阅者**: 状态为 `active` 的订阅者数量
- **非活跃订阅者**: 状态为 `inactive` 的订阅者数量

#### 🔍 搜索和筛选
- **邮箱搜索**: 实时搜索订阅者邮箱
- **状态筛选**: 按 `active` / `inactive` 筛选
- **标签筛选**: 按 `preview` / `user` 标签筛选

#### ✏️ 订阅者管理
- **编辑标签**: 
  - 勾选/取消 `preview` 标签
  - 勾选/取消 `user` 标签
- **更新状态**: 
  - 将订阅者设置为 `active` 或 `inactive`
- **删除订阅者**: 永久删除订阅者记录

#### 🔄 自动刷新
- 每 30 秒自动刷新数据
- 手动刷新按钮

**使用场景**:
- 管理订阅者列表
- 批量标记预览用户
- 处理取消订阅请求
- 查看订阅者统计信息

---

## 🚀 快速开始

### 环境要求

- Node.js 18.x 或更高版本
- npm >= 9.0.0
- Python 3.x（用于新闻通讯生成和邮件发送）
- MongoDB Atlas 账户

### 1. 克隆项目

```bash
git clone <repository-url>
cd Techsum-newsletter
```

### 2. 安装依赖

```bash
# Node.js 依赖（API 服务器）
npm install

# Python 依赖（新闻通讯生成和发送）
pip install -r scripts/requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件（参考 `.env.example`）：

```bash
# MongoDB 配置
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=techsum
MONGODB_COLL=subscribers

# Gmail 配置（用于发送邮件）
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# TechSum API（可选，用于获取新闻亮点）
TECHSUM_API_KEY=your-api-key

# 管理员认证配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SESSION_SECRET=your_random_session_secret_key

# 服务器配置
PORT=3000
CORS_ORIGIN=*
```

**Gmail App Password 获取方法**:
1. 登录 Google 账户
2. 启用两步验证
3. 访问 [App Passwords](https://myaccount.google.com/apppasswords)
4. 生成应用专用密码

### 4. 启动本地服务器

```bash
npm run dev
# 或
npm start
```

服务器将在 `http://localhost:3000` 启动：

- **订阅页面**: http://localhost:3000/
- **取消订阅页面**: http://localhost:3000/unsubscribe.html
- **登录页面**: http://localhost:3000/login.html
- **后台管理面板**: http://localhost:3000/admin.html（需要登录）
- **健康检查**: http://localhost:3000/api/health

### 5. 生成新闻通讯

```bash
python scripts/api.py
```

这将生成 `newsletter-YYYY-MM-DD.html` 文件到 `output/` 目录。

**周刊保存机制**:
- 每期周刊自动保存到 `output/` 文件夹（用于日常使用，不提交到 Git）
- 同时自动复制到 `archive/` 文件夹（用于 Git 提交，保存历史记录）
- 文件名格式: `newsletter-YYYY-MM-DD.html`（例如：`newsletter-2025-01-15.html`）
- `archive/` 文件夹中的文件会被提交到 Git，方便查看历史周刊
- `output/` 文件夹在 `.gitignore` 中，不会被提交到 Git

### 6. 发送新闻通讯

```bash
# 发送给 MongoDB 中的订阅者
LATEST=$(ls -t output/newsletter-*.html | head -n 1)
python scripts/send_email.py \
  --file "$LATEST" \
  --subject "TechSum Weekly · $(date +%Y-%m-%d)" \
  --from-mongo --tags "preview" --status active --limit 50 \
  --batch-size 10 --sleep 2
```

---

## 🚢 部署指南

### Railway 部署

项目已配置 Railway 部署，详细步骤请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

**快速部署步骤**:

1. **在 Railway 创建项目**
   - 访问 [Railway](https://railway.app)
   - 创建新项目并连接 GitHub 仓库

2. **配置环境变量**
   - 在 Railway 项目设置中添加以下环境变量：
     - `MONGODB_URI`
     - `MONGODB_DB`
     - `MONGODB_COLL`
     - `EMAIL_USER`
     - `EMAIL_PASS`
     - `TECHSUM_API_KEY`（可选）
     - `ADMIN_USERNAME`（管理员用户名，建议设置）
     - `ADMIN_PASSWORD`（管理员密码，**必须设置强密码**）
     - `SESSION_SECRET`（Session 密钥，建议设置随机字符串）

3. **自动部署**
   - Railway 会自动检测 `railway.json` 和 `Procfile`
   - 部署完成后获取部署 URL

4. **测试部署**
   - 访问部署 URL 测试各个页面
   - 检查 API 端点是否正常工作

**部署文件说明**:
- `Procfile`: 定义 Railway 启动命令
- `railway.json`: Railway 构建配置

---

## 📡 API 文档

### 订阅 API

**端点**: `POST /api/subscribe`

**请求体**:
```json
{
  "email": "user@example.com",
  "tags": ["preview"]  // 可选
}
```

**响应**:
```json
{
  "ok": true,
  "email": "user@example.com"
}
```

**注意**: 订阅成功后，系统会自动发送欢迎确认邮件给新订阅者。

---

### 取消订阅 API

**端点**: `POST /api/unsubscribe`

**请求体**:
```json
{
  "email": "user@example.com"
}
```

**响应**:
```json
{
  "ok": true,
  "email": "user@example.com"
}
```

---

### 统计 API

**端点**: `GET /api/stats`

**响应**:
```json
{
  "ok": true,
  "total": 100,
  "active": 85,
  "inactive": 15,
  "recent": [
    {
      "email": "user@example.com",
      "status": "active",
      "tags": ["preview"],
      "updatedAt": "2025-01-15T10:00:00.000Z",
      "createdAt": "2025-01-10T10:00:00.000Z"
    }
  ]
}
```

---

### 更新标签 API

**端点**: `PATCH /api/subscribers/:email/tags`

**请求体**:
```json
{
  "tag": "preview",
  "add": true  // true 添加，false 删除
}
```

**响应**:
```json
{
  "ok": true,
  "tags": ["preview", "user"]
}
```

---

### 删除订阅者 API

**端点**: `DELETE /api/subscribers/:email`

**响应**:
```json
{
  "ok": true,
  "message": "Deleted user@example.com"
}
```

---

### 登录 API

**端点**: `POST /api/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**响应**:
```json
{
  "ok": true,
  "message": "Login successful"
}
```

---

### 登出 API

**端点**: `POST /api/logout`

**响应**:
```json
{
  "ok": true,
  "message": "Logged out successfully"
}
```

---

### 认证检查 API

**端点**: `GET /api/auth/check`

**响应**:
```json
{
  "ok": true,
  "authenticated": true,
  "username": "admin"
}
```

---

### 健康检查 API

**端点**: `GET /api/health`

**响应**:
```json
{
  "ok": true,
  "timestamp": "2025-01-15T10:00:00.000Z"
}
```

---

## 📁 项目结构

```
Techsum-newsletter/
├── api/                    # API 端点
│   ├── subscribe.js        # 订阅 API
│   └── unsubscribe.js      # 取消订阅 API
├── config/                 # 配置文件
│   └── categories.json     # 新闻分类配置
├── docs/                   # 前端页面
│   ├── index.html          # 订阅页面
│   ├── unsubscribe.html    # 取消订阅页面
│   └── admin.html          # 后台管理面板
├── lib/                    # 工具库
│   ├── mongo.js            # MongoDB 连接工具
│   └── email.js            # 邮件发送工具
├── archive/                # 历史周刊存档（提交到 Git）
│   ├── README.md           # 存档说明
│   └── newsletter-*.html   # 历史周刊文件
├── output/                 # 生成的新闻通讯 HTML（不提交到 Git）
│   └── newsletter-*.html
├── scripts/                # Python 脚本
│   ├── api.py              # 新闻通讯 HTML 生成
│   ├── send_email.py       # 批量邮件发送
│   ├── subscribers.py      # 订阅者管理 CLI
│   └── requirements.txt    # Python 依赖
├── src/                    # 资源文件
│   ├── newsletter_template.html  # 新闻通讯模板
│   ├── confirmation_email_template.html  # 订阅确认邮件模板
│   ├── turing_black_logo.png      # Logo
│   └── utils.py            # Python 工具函数
├── server.js               # Express 服务器（本地开发）
├── package.json            # Node.js 依赖
├── Procfile                # Railway 部署配置
├── railway.json            # Railway 构建配置
├── DEPLOYMENT.md           # 详细部署指南
└── readme.md               # 本文件
```

---

## 🛠️ MongoDB 管理

### 使用 Python CLI 管理订阅者

```bash
# 添加订阅者
python scripts/subscribers.py add \
  --email someone@example.com \
  --tags preview \
  --status active

# 更新状态
python scripts/subscribers.py set-status \
  --email someone@example.com \
  --status inactive

# 添加标签
python scripts/subscribers.py add-tags \
  --email someone@example.com \
  --tags user

# 删除标签
python scripts/subscribers.py remove-tags \
  --email someone@example.com \
  --tags preview

# 删除订阅者
python scripts/subscribers.py remove \
  --email someone@example.com

# 列出订阅者
python scripts/subscribers.py list \
  --status active \
  --tags preview
```

---

## 🎨 技术栈

- **后端**: 
  - Node.js (Express) - API 服务器
  - MongoDB - 数据库
- **前端**: 
  - Vanilla HTML/CSS/JavaScript - 无框架，轻量级
  - 响应式设计，支持移动端
- **邮件**: 
  - Gmail SMTP - 邮件发送
- **新闻通讯生成**: 
  - Python (requests, jinja2) - 内容抓取和模板渲染
- **部署**: 
  - Railway - 云平台部署

---

## 📝 许可证

私有项目 - 保留所有权利

---

## 🔗 相关链接

- **网站**: [https://www.techsum.ai](https://www.techsum.ai)
- **联系邮箱**: info@turingplanet.org
- **部署地址**: [https://web-production-914f7.up.railway.app/](https://web-production-914f7.up.railway.app/)

---

## 💡 使用提示

1. **订阅者标签说明**:
   - `preview`: 预览用户，用于测试邮件发送
   - `user`: 正式用户

2. **邮件发送建议**:
   - 使用 `--batch-size` 控制批量大小，避免触发 Gmail 限制
   - 使用 `--sleep` 设置发送间隔，避免频率限制
   - 先发送给 `preview` 标签用户测试

3. **安全建议**:
   - 不要将 `.env` 文件提交到 Git
   - 使用 Gmail App Password 而非账户密码
   - 定期更新依赖包

---

**Made with ❤️ by TURING PLANET**
