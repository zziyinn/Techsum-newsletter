// lib/mongo.js
import { MongoClient, ServerApiVersion } from 'mongodb';

let _client = null;
let _db = null;

function env(name, required = false) {
  const v = process.env[name];
  if (required && !v) {
    throw new Error(`Missing ENV: ${name}`);
  }
  return v;
}

async function getClient() {
  if (_client) return _client;
  const uri = env('MONGODB_URI', true); // 必须
  _client = new MongoClient(uri, { serverApi: ServerApiVersion.v1 });
  await _client.connect();
  return _client;
}

async function getCollection() {
  const client = await getClient();
  const dbName = env('MONGODB_DB', true);
  const collName = env('MONGODB_COLL', true);
  if (!_db) _db = client.db(dbName);
  return _db.collection(collName);
}

export { getCollection };
