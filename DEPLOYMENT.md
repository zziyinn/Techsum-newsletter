# Railway 部署方案

本指南详细说明如何将 TechSum Newsletter 后端部署到 Railway。

## 📋 前置准备

### 1. 准备账号和资源

- ✅ [Railway](https://railway.app) 账号（可使用 GitHub 账号登录）
- ✅ [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) 账号（免费层即可）
- ✅ GitHub 仓库（项目代码已推送到 GitHub）

### 2. 配置 MongoDB Atlas

1. 登录 MongoDB Atlas
2. 创建集群（选择免费 M0 集群）
3. 创建数据库用户（Database Access）
4. 配置网络访问（Network Access），添加 `0.0.0.0/0` 允许所有 IP
5. 获取连接字符串（Database > Connect > Connect your application）
   - 格式：`mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`
   - 将 `<password>` 替换为实际密码

---

## 🚀 部署步骤

### 步骤 1：创建 Railway 项目

1. 登录 [Railway Dashboard](https://railway.app/dashboard)
2. 点击 **"New Project"** 或 **"New"** 按钮
3. 选择 **"Deploy from GitHub repo"**
4. 选择你的 GitHub 账号和仓库 `Techsum-newsletter-1`
5. Railway 会自动检测仓库并开始部署

### 步骤 2：配置环境变量

在 Railway 项目页面：

1. 点击项目名称进入项目详情
2. 点击 **"Variables"** 标签页
3. 点击 **"New Variable"** 添加以下环境变量：

#### 必需环境变量

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=techsum
MONGODB_COLL=subscribers
```

#### 可选环境变量

```bash
CORS_ORIGIN=*
PORT=3000  # Railway 会自动设置，一般不需要手动配置
```

> **注意：**
> - `MONGODB_URI` 中的 `<username>` 和 `<password>` 需要替换为实际值
> - `PORT` 变量由 Railway 自动提供，通常不需要手动设置
> - 如果需要限制 CORS 访问，将 `CORS_ORIGIN` 设置为你的前端域名

### 步骤 3：检查部署配置

项目已包含以下部署配置文件，Railway 会自动识别：

#### `railway.json` - Railway 构建配置
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildEnvironment": "V3"
  },
  "deploy": {
    "startCommand": "npm start",
    "sleepApplication": true
  }
}
```

#### `Procfile` - 进程定义
```
web: npm start
```

#### `package.json` - Node.js 配置
- ✅ 已指定 Node.js 版本：`>=18.0.0`
- ✅ 已配置启动命令：`npm start`

### 步骤 4：等待部署完成

1. Railway 会自动检测到新的部署
2. 查看 **"Deployments"** 标签页，观察构建日志
3. 确认构建成功：
   - ✅ 应显示 "Detected Node.js"
   - ✅ 执行 `npm install` 成功
   - ✅ 执行 `npm start` 启动服务

### 步骤 5：获取部署 URL

1. 部署成功后，点击 **"Settings"** 标签页
2. 在 **"Networking"** 部分，点击 **"Generate Domain"**
3. Railway 会生成一个域名，例如：`techsum-newsletter-production.up.railway.app`
4. 记录此 URL，用于访问你的 API

---

## ✅ 验证部署

### 1. 健康检查

```bash
curl https://YOUR_RAILWAY_URL/api/health
```

预期响应：
```json
{"ok":true,"timestamp":"2025-11-16T..."}
```

### 2. 测试订阅接口

```bash
curl -X POST https://YOUR_RAILWAY_URL/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "tags": ["tech"]}'
```

预期响应：
```json
{"ok":true,"email":"test@example.com"}
```

### 3. 访问前端页面

- **订阅页面**: `https://YOUR_RAILWAY_URL/`
- **取消订阅页面**: `https://YOUR_RAILWAY_URL/unsubscribe.html`
- **管理后台**: `https://YOUR_RAILWAY_URL/admin.html`

### 4. 查看日志

在 Railway Dashboard：
1. 点击项目 > **"View Logs"**
2. 检查是否有错误信息
3. 确认服务器正常运行

---

## 🔧 常见问题排查

### 问题 1：构建失败 - 误识别为 Python 项目

**症状：**
```
✖ No start command was found.
To start your Python application...
```

**解决方案：**
- ✅ 确认 `requirements.txt` 已移动到 `scripts/` 目录
- ✅ 确认 `railway.json` 使用 `NIXPACKS` 构建器
- ✅ 确认根目录有 `package.json` 和 `Procfile`

### 问题 2：MongoDB 连接失败

**症状：**
```
Error: Missing ENV: MONGODB_URI
```

**解决方案：**
1. 检查 Railway 环境变量是否已正确设置
2. 验证 MongoDB Atlas 连接字符串格式
3. 确认 MongoDB Atlas 网络访问已允许所有 IP (`0.0.0.0/0`)
4. 检查 MongoDB Atlas 数据库用户密码是否正确

### 问题 3：应用休眠

**症状：**
首次访问需要等待几秒钟

**说明：**
- Railway 免费版会在无流量时休眠应用
- 首次访问需要几秒钟唤醒应用
- 这是正常现象，不影响功能

**解决方案（可选）：**
- 升级到付费计划可避免休眠
- 使用定时任务（如 UptimeRobot）定期访问健康检查端点

### 问题 4：端口错误

**症状：**
```
Error: listen EADDRINUSE: address already in use
```

**解决方案：**
- Railway 会自动设置 `PORT` 环境变量
- 不要手动设置 `PORT` 环境变量
- 代码中已使用 `process.env.PORT || 3000`，会自动适配

### 问题 5：CORS 错误

**症状：**
前端无法访问 API，浏览器控制台显示 CORS 错误

**解决方案：**
1. 在 Railway 环境变量中设置 `CORS_ORIGIN`
2. 设置为你的前端域名，例如：`https://your-frontend.com`
3. 如需允许所有来源（开发环境），设置为 `*`

---

## 📊 监控和维护

### 查看部署状态

1. **Deployments** 标签页 - 查看所有部署历史
2. **Metrics** 标签页 - 查看 CPU、内存使用情况
3. **Logs** 标签页 - 实时查看应用日志

### 重新部署

每次推送到 GitHub 的 `main` 分支，Railway 会自动触发重新部署。

手动触发重新部署：
1. 在 **Deployments** 标签页
2. 点击 **"Redeploy"** 按钮

### 环境变量更新

1. 在 **Variables** 标签页
2. 编辑或添加环境变量
3. Railway 会自动重启应用应用新配置

---

## 🔐 安全建议

1. **MongoDB Atlas 安全：**
   - 使用强密码
   - 定期轮换密码
   - 限制网络访问（生产环境）

2. **环境变量安全：**
   - 不要将敏感信息提交到 Git
   - 使用 Railway 的 Secrets 管理
   - 定期审查环境变量

3. **CORS 配置：**
   - 生产环境不要使用 `*`
   - 明确指定允许的前端域名

---

## 📝 部署检查清单

部署前确认：

- [ ] GitHub 仓库已推送最新代码
- [ ] MongoDB Atlas 集群已创建并配置
- [ ] MongoDB 连接字符串已获取
- [ ] Railway 项目已创建并连接 GitHub
- [ ] 必需环境变量已配置（MONGODB_URI, MONGODB_DB, MONGODB_COLL）
- [ ] 部署日志显示构建成功
- [ ] 健康检查端点返回正常响应
- [ ] API 功能测试通过

---

## 🎯 快速部署命令总结

```bash
# 1. 确保代码已提交并推送
git add .
git commit -m "Ready for Railway deployment"
git push origin main

# 2. 在 Railway Dashboard 中：
#    - 创建新项目并连接 GitHub 仓库
#    - 配置环境变量（MONGODB_URI, MONGODB_DB, MONGODB_COLL）
#    - 等待自动部署完成

# 3. 验证部署
curl https://YOUR_RAILWAY_URL/api/health
```

---

## 📚 相关资源

- [Railway 官方文档](https://docs.railway.app/)
- [MongoDB Atlas 文档](https://www.mongodb.com/docs/atlas/)
- [项目 README](./readme.md)

---

## 🆘 获取帮助

如果遇到问题：

1. 查看 Railway 部署日志
2. 检查环境变量配置
3. 验证 MongoDB Atlas 连接
4. 参考 [Railway Discord](https://discord.gg/railway) 社区

部署愉快！🚀

