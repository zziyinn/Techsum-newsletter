#!/usr/bin/env node
/**
 * 本地开发服务器
 * 提供静态文件服务和API端点
 * 
 * 注意：使用 `node -r dotenv/config server.js` 启动时，
 * dotenv 会在导入任何模块之前加载环境变量
 */

import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import subscribeHandler from './api/subscribe.js';
import unsubscribeHandler from './api/unsubscribe.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 静态文件服务（docs目录）
app.use(express.static(join(__dirname, 'docs')));

// API路由（支持所有HTTP方法，handler内部会处理）
app.all('/api/subscribe', async (req, res) => {
  try {
    await subscribeHandler(req, res);
  } catch (err) {
    console.error('[server] subscribe error:', err);
    if (!res.headersSent) {
      res.status(500).json({ ok: false, error: String(err.message || err) });
    }
  }
});

app.all('/api/unsubscribe', async (req, res) => {
  try {
    await unsubscribeHandler(req, res);
  } catch (err) {
    console.error('[server] unsubscribe error:', err);
    if (!res.headersSent) {
      res.status(500).json({ ok: false, error: String(err.message || err) });
    }
  }
});

// CORS 中间件
app.use('/api', (req, res, next) => {
  const allow = process.env.CORS_ORIGIN || '*';
  res.setHeader('Access-Control-Allow-Origin', allow);
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  next();
});

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ ok: true, timestamp: new Date().toISOString() });
});

// 订阅者统计（用于调试）
app.get('/api/stats', async (req, res) => {
  try {
    const { getCollection } = await import('./lib/mongo.js');
    const coll = await getCollection();
    
    // 排除 email_lc 为 null 的旧数据
    const total = await coll.countDocuments({ email_lc: { $ne: null } });
    const active = await coll.countDocuments({ status: 'active', email_lc: { $ne: null } });
    const inactive = await coll.countDocuments({ status: 'inactive', email_lc: { $ne: null } });
    
    // 获取所有订阅者（按更新时间排序）
    // 过滤掉 email_lc 为 null 的旧数据
    const all = await coll.find({ email_lc: { $ne: null } })
      .sort({ updatedAt: -1, createdAt: -1 })
      .project({ _id: 0, email: 1, status: 1, tags: 1, updatedAt: 1, createdAt: 1 })
      .toArray();
    
    res.json({
      ok: true,
      total,
      active,
      inactive,
      recent: all.map(d => ({
        email: d.email,
        status: d.status,
        tags: d.tags || [],
        updatedAt: d.updatedAt,
        createdAt: d.createdAt
      }))
    });
  } catch (err) {
    console.error('[stats] error:', err);
    res.status(500).json({ ok: false, error: String(err.message || err) });
  }
});

// 更新订阅者标签
app.patch('/api/subscribers/:email/tags', async (req, res) => {
  try {
    const { getCollection } = await import('./lib/mongo.js');
    const coll = await getCollection();
    const email = decodeURIComponent(req.params.email).toLowerCase().trim();
    const { tag, add } = req.body;
    
    if (!tag || typeof add !== 'boolean') {
      return res.status(400).json({ ok: false, error: 'Missing tag or add parameter' });
    }
    
    // 获取当前文档（使用 email_lc 查询，保持与索引一致）
    const doc = await coll.findOne({ email_lc: email });
    if (!doc) {
      return res.status(404).json({ ok: false, error: 'Subscriber not found' });
    }
    
    const currentTags = doc.tags || [];
    let newTags;
    
    if (add) {
      // 添加标签（如果不存在）
      newTags = currentTags.includes(tag) ? currentTags : [...currentTags, tag];
    } else {
      // 删除标签
      newTags = currentTags.filter(t => t !== tag);
    }
    
    const result = await coll.updateOne(
      { email_lc: email },
      { $set: { tags: newTags, updatedAt: new Date() } }
    );
    
    if (result.modifiedCount > 0 || result.matchedCount > 0) {
      res.json({ ok: true, tags: newTags });
    } else {
      res.status(404).json({ ok: false, error: 'Subscriber not found' });
    }
  } catch (err) {
    console.error('[update tags] error:', err);
    res.status(500).json({ ok: false, error: String(err.message || err) });
  }
});

// 删除订阅者
app.delete('/api/subscribers/:email', async (req, res) => {
  try {
    const { getCollection } = await import('./lib/mongo.js');
    const coll = await getCollection();
    const email = decodeURIComponent(req.params.email).toLowerCase().trim();
    
    // 尝试用 email 或 email_lc 字段删除（兼容不同数据格式）
    const result = await coll.deleteOne({ 
      $or: [
        { email: email },
        { email_lc: email }
      ]
    });
    
    if (result.deletedCount > 0) {
      res.json({ ok: true, message: `Deleted ${email}` });
    } else {
      res.status(404).json({ ok: false, error: 'Subscriber not found' });
    }
  } catch (err) {
    console.error('[delete subscriber] error:', err);
    res.status(500).json({ ok: false, error: String(err.message || err) });
  }
});

// 根路径重定向到订阅页
app.get('/', (req, res) => {
  res.sendFile(join(__dirname, 'docs', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
  console.log(`📄 Subscribe page: http://localhost:${PORT}/`);
  console.log(`📋 Unsubscribe page: http://localhost:${PORT}/unsubscribe.html`);
  console.log(`⚙️  Admin page: http://localhost:${PORT}/admin.html`);
  console.log(`🔍 Health check: http://localhost:${PORT}/api/health`);
});

