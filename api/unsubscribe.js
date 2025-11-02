// api/unsubscribe.js
import { getCollection } from '../lib/mongo.js';

function setCORS(res) {
  const allow = process.env.CORS_ORIGIN || '*';
  res.setHeader('Access-Control-Allow-Origin', allow);
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

export default async (req, res) => {
  setCORS(res);
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).send('Method Not Allowed');

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    const email = (body.email || '').trim().toLowerCase();
    if (!email) return res.status(400).json({ ok: false, error: 'Email required' });

    const coll = await getCollection();
    const email_lc = email.toLowerCase();
    // 使用 email_lc 作为查询条件，保持与索引一致
    const r = await coll.updateOne(
      { email_lc }, 
      { $set: { status: 'inactive', updatedAt: new Date() } }
    );
    console.log('[unsubscribe] update result:', r);

    return res.status(200).json({ ok: true, email });
  } catch (err) {
    console.error('[unsubscribe] error:', err);
    const msg = process.env.VERCEL_ENV === 'production' ? 'Server Error' : String(err?.message || err);
    return res.status(500).send(msg);
  }
};
