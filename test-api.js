#!/usr/bin/env node
/**
 * API 测试脚本
 * 用法: node test-api.js [BASE_URL]
 * 例如: node test-api.js http://localhost:3000
 *       node test-api.js https://your-app.railway.app
 */

const BASE_URL = process.argv[2] || 'http://localhost:3000';

// 移除尾部斜杠
const baseUrl = BASE_URL.replace(/\/$/, '');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function test(name, fn) {
  try {
    log(`\n🧪 Testing: ${name}`, 'cyan');
    await fn();
    log(`✅ ${name}: PASSED`, 'green');
  } catch (error) {
    log(`❌ ${name}: FAILED`, 'red');
    log(`   Error: ${error.message}`, 'red');
    throw error;
  }
}

async function request(method, path, body = null) {
  const url = `${baseUrl}${path}`;
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);
  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = text;
  }

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${JSON.stringify(data)}`);
  }

  return { status: response.status, data };
}

async function runTests() {
  log(`\n${'='.repeat(50)}`, 'blue');
  log(`Testing API: ${baseUrl}`, 'blue');
  log(`${'='.repeat(50)}`, 'blue');

  const testEmail = `test-${Date.now()}@example.com`;

  // 1. 健康检查
  await test('Health Check', async () => {
    const { data } = await request('GET', '/api/health');
    if (!data.ok) throw new Error('Health check failed');
    log(`   Response: ${JSON.stringify(data)}`, 'yellow');
  });

  // 2. 订阅
  await test('Subscribe', async () => {
    const { data } = await request('POST', '/api/subscribe', {
      email: testEmail,
      tags: ['tech', 'newsletter'],
    });
    if (!data.ok || data.email !== testEmail) {
      throw new Error('Subscribe failed');
    }
    log(`   Subscribed: ${data.email}`, 'yellow');
  });

  // 3. 统计信息
  await test('Get Stats', async () => {
    const { data } = await request('GET', '/api/stats');
    if (!data.ok) throw new Error('Get stats failed');
    log(`   Total: ${data.total}, Active: ${data.active}`, 'yellow');
  });

  // 4. 更新标签
  await test('Update Tags', async () => {
    const { data } = await request('PATCH', `/api/subscribers/${encodeURIComponent(testEmail)}/tags`, {
      tag: 'ai',
      add: true,
    });
    if (!data.ok) throw new Error('Update tags failed');
    log(`   Tags: ${JSON.stringify(data.tags)}`, 'yellow');
  });

  // 5. 取消订阅
  await test('Unsubscribe', async () => {
    const { data } = await request('POST', '/api/unsubscribe', {
      email: testEmail,
    });
    if (!data.ok) throw new Error('Unsubscribe failed');
    log(`   Unsubscribed: ${data.email}`, 'yellow');
  });

  // 6. 验证取消订阅后的状态
  await test('Verify Unsubscribed Status', async () => {
    const { data } = await request('GET', '/api/stats');
    if (!data.ok) throw new Error('Get stats failed');
    log(`   Active: ${data.active} (should be decreased)`, 'yellow');
  });

  // 7. 删除订阅者
  await test('Delete Subscriber', async () => {
    const { data } = await request('DELETE', `/api/subscribers/${encodeURIComponent(testEmail)}`);
    if (!data.ok) throw new Error('Delete subscriber failed');
    log(`   Deleted: ${testEmail}`, 'yellow');
  });

  // 8. 测试无效邮箱
  await test('Invalid Email Validation', async () => {
    try {
      await request('POST', '/api/subscribe', {
        email: 'invalid-email',
      });
      throw new Error('Should have failed with invalid email');
    } catch (error) {
      if (error.message.includes('400')) {
        log(`   Correctly rejected invalid email`, 'yellow');
      } else {
        throw error;
      }
    }
  });

  // 9. 测试蜜罐（bot 检测）
  await test('Honeypot Detection', async () => {
    const { data } = await request('POST', '/api/subscribe', {
      email: 'bot@example.com',
      website: 'spam', // 蜜罐字段
    });
    if (!data.bot) {
      throw new Error('Honeypot detection failed');
    }
    log(`   Bot detected correctly`, 'yellow');
  });

  log(`\n${'='.repeat(50)}`, 'green');
  log('🎉 All tests passed!', 'green');
  log(`${'='.repeat(50)}\n`, 'green');
}

// 运行测试
runTests().catch((error) => {
  log(`\n❌ Test suite failed: ${error.message}`, 'red');
  process.exit(1);
});

