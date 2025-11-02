// api/subscribe.js
import { getCollection } from '../lib/mongo.js';

function setCORS(res) {
  const allow = process.env.CORS_ORIGIN || '*';
  res.setHeader('Access-Control-Allow-Origin', allow);
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function isEmail(v) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v).toLowerCase());
}

export default async (req, res) => {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).send('Method Not Allowed');

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    const email = (body.email || '').trim().toLowerCase();
    const tags  = Array.isArray(body.tags) ? body.tags : [];

    // 蜜罐可选：body.website
    if (body.website) {
      console.warn('[subscribe] honeypot triggered');
      return res.status(200).json({ ok: true, bot: true });
    }
    if (!isEmail(email)) {
      return res.status(400).json({ ok: false, error: 'Invalid email' });
    }

    const coll = await getCollection();
    const now = new Date();

    const r = await coll.updateOne(
      { email },
      {
        $set: { email, status: 'active', tags, updatedAt: now },
        $setOnInsert: { createdAt: now }
      },
      { upsert: true }
    );

    console.log('[subscribe] upsert result:', r);

    return res.status(200).json({ ok: true, email });
  } catch (err) {
    console.error('[subscribe] error:', err);
    // 开发阶段给更多信息
    const msg = process.env.VERCEL_ENV === 'production' ? 'Server Error' : String(err?.message || err);
    return res.status(500).send(msg);
  }
};
