// api/subscribe.js
import { getCollection } from "../lib/mongo.js";

function isEmail(v) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v).toLowerCase());
}

function corsHeaders(origin) {
  const allow = process.env.CORS_ORIGIN || ""; // e.g. https://<user>.github.io/<repo>
  const ok = origin && allow && origin.startsWith(allow);
  return {
    "Access-Control-Allow-Origin": ok ? origin : allow || "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400"
  };
}

export default async function handler(req, res) {
  const headers = corsHeaders(req.headers.origin || "");
  if (req.method === "OPTIONS") {
    return res.status(200).set(headers).end();
  }
  if (req.method !== "POST") {
    return res.status(405).set(headers).json({ error: "Method Not Allowed" });
  }

  try {
    const { email, website, tags } = req.body || {};
    // 蜜罐：机器人会填
    if (website) return res.status(200).set(headers).json({ ok: true });

    if (!email || !isEmail(email)) {
      return res.status(400).set(headers).json({ error: "Invalid email" });
    }

    const col = await getCollection();
    const now = new Date().toISOString();
    await col.updateOne(
      { email: email.toLowerCase() },
      {
        $set: {
          email: email.toLowerCase(),
          status: "active",
          updated_at: now
        },
        $setOnInsert: {
          created_at: now,
          tags: Array.isArray(tags) ? tags : []
        }
      },
      { upsert: true }
    );

    return res.status(200).set(headers).json({ ok: true });
  } catch (e) {
    console.error(e);
    return res.status(500).set(headers).json({ error: "Server error" });
  }
}
