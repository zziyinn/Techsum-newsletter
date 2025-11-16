# 测试指南

## 本地测试

### 1. 环境准备

```bash
# 安装依赖
npm install

# 复制环境变量配置
cp env.example .env

# 编辑 .env 文件，填入你的 MongoDB 连接字符串等配置
```

### 2. 启动本地服务器

```bash
npm run dev
# 或者
npm start
```

服务器会在 `http://localhost:3000` 启动

### 3. 测试 API 端点

#### 健康检查
```bash
curl http://localhost:3000/api/health
```

#### 订阅
```bash
curl -X POST http://localhost:3000/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "tags": ["tech"]}'
```

#### 取消订阅
```bash
curl -X POST http://localhost:3000/api/unsubscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

#### 获取统计信息
```bash
curl http://localhost:3000/api/stats
```

#### 更新订阅者标签
```bash
curl -X PATCH http://localhost:3000/api/subscribers/test@example.com/tags \
  -H "Content-Type: application/json" \
  -d '{"tag": "ai", "add": true}'
```

#### 删除订阅者
```bash
curl -X DELETE http://localhost:3000/api/subscribers/test@example.com
```

### 4. 测试前端页面

- 订阅页面: http://localhost:3000/
- 取消订阅页面: http://localhost:3000/unsubscribe.html
- 管理页面: http://localhost:3000/admin.html

---

## Railway 部署后测试

### 1. 部署准备

1. 在 Railway 创建新项目
2. 连接 GitHub 仓库
3. 配置环境变量（在 Railway 项目设置中添加）：
   - `MONGODB_URI`
   - `MONGODB_DB`
   - `MONGODB_COLL`
   - `EMAIL_USER` (可选)
   - `EMAIL_PASS` (可选)
   - `CORS_ORIGIN` (可选，默认为 `*`)

### 2. 获取部署 URL

部署完成后，Railway 会提供一个 URL，例如：
- `https://your-app.railway.app`

### 3. 测试 API 端点

将以下命令中的 `YOUR_RAILWAY_URL` 替换为你的实际 URL：

#### 健康检查
```bash
curl https://YOUR_RAILWAY_URL/api/health
```

预期响应：
```json
{"ok":true,"timestamp":"2025-01-XX..."}
```

#### 订阅测试
```bash
curl -X POST https://YOUR_RAILWAY_URL/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "tags": ["tech"]}'
```

预期响应：
```json
{"ok":true,"email":"test@example.com"}
```

#### 取消订阅测试
```bash
curl -X POST https://YOUR_RAILWAY_URL/api/unsubscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

#### 统计信息
```bash
curl https://YOUR_RAILWAY_URL/api/stats
```

### 4. 使用测试脚本

运行提供的测试脚本：

```bash
# 本地测试
./test-api.sh localhost:3000

# Railway 测试
./test-api.sh YOUR_RAILWAY_URL
```

---

## 自动化测试

可以使用 `test-api.js` 脚本进行自动化测试：

```bash
# 本地测试
node test-api.js http://localhost:3000

# Railway 测试
node test-api.js https://YOUR_RAILWAY_URL
```

---

## 常见问题排查

### 连接 MongoDB 失败
- 检查 `MONGODB_URI` 是否正确
- 检查 MongoDB Atlas 网络访问设置（IP 白名单）

### API 返回 500 错误
- 查看 Railway 日志：Railway Dashboard > 项目 > Deployments > 查看日志
- 检查环境变量是否都已配置

### CORS 错误
- 检查 `CORS_ORIGIN` 环境变量设置
- 确保前端域名在允许列表中

### 应用休眠
- Railway 免费版会在无流量时休眠
- 首次访问可能需要等待几秒钟唤醒应用

