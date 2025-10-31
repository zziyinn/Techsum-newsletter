// lib/mongo.js
import { MongoClient } from "mongodb";

let client;
let clientPromise;

const uri = process.env.MONGODB_URI;           // e.g. mongodb+srv://user:pass@cluster0...
const options = {};

if (!uri) {
  throw new Error("MONGODB_URI is not set");
}

// Vercel: 复用全局连接，避免冷启动重复建连
if (!global._mongoClientPromise) {
  client = new MongoClient(uri, options);
  global._mongoClientPromise = client.connect();
}
clientPromise = global._mongoClientPromise;

export async function getCollection() {
  const db = process.env.MONGODB_DB || "techsum";
  const coll = process.env.MONGODB_COLL || "subscribers";
  const c = (await clientPromise).db(db).collection(coll);
  await c.createIndex({ email: 1 }, { unique: true });
  await c.createIndex({ status: 1 });
  return c;
}
