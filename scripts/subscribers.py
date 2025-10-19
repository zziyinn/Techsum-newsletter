#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manage subscribers in MongoDB Atlas.

Usage examples:
  # 1) 添加/更新（去重键=email_lc）
  python scripts/subscribers.py add --email alice@example.com --tags preview,cn --status active

  # 2) 删除
  python scripts/subscribers.py remove --email alice@example.com

  # 3) 设置状态
  python scripts/subscribers.py set-status --email bob@example.com --status inactive

  # 4) 增/删标签
  python scripts/subscribers.py add-tags --email bob@example.com --tags cn
  python scripts/subscribers.py remove-tags --email bob@example.com --tags preview

  # 5) 列表（可过滤）
  python scripts/subscribers.py list --status active --tags preview --limit 100

  # 6) 导入CSV（列：email,status,tags；tags用逗号）
  python scripts/subscribers.py import-csv --file subs.csv --default-status active --default-tags preview

  # 7) 导出CSV（可过滤）
  python scripts/subscribers.py export-csv --file out.csv --status active --tags preview

  # 8) 建索引（唯一约束 email_lc）
  python scripts/subscribers.py ensure-index
"""

import os, csv, argparse, sys
from typing import List
from pymongo import MongoClient, ASCENDING
from pymongo.server_api import ServerApi

try:
    from dotenv import load_dotenv
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except Exception:
    pass

DBNAME  = os.getenv("MONGODB_DB", "techsum")
COLL    = os.getenv("MONGODB_COLL", "subscribers")
URI     = os.getenv("MONGODB_URI")

def col():
    assert URI, "MONGODB_URI not set"
    client = MongoClient(URI, server_api=ServerApi('1'), serverSelectionTimeoutMS=8000)
    return client[DBNAME][COLL]

def parse_tags(s: str | None) -> List[str]:
    if not s: return []
    parts = [x.strip() for x in s.replace(";",",").split(",")]
    return [p for p in parts if p]

def cmd_add(args):
    c = col()
    email = args.email.strip()
    doc = {
        "email": email,
        "email_lc": email.lower(),
        "status": args.status,
        "tags": parse_tags(args.tags) or [],
    }
    res = c.update_one({"email_lc": doc["email_lc"]}, {"$set": doc}, upsert=True)
    if res.matched_count: print(f"✅ updated: {email}")
    else:                 print(f"✅ inserted: {email}")

def cmd_remove(args):
    c = col()
    email_lc = args.email.strip().lower()
    res = c.delete_one({"email_lc": email_lc})
    print(f"🗑 deleted: {res.deleted_count}")

def cmd_set_status(args):
    c = col()
    email_lc = args.email.strip().lower()
    res = c.update_one({"email_lc": email_lc}, {"$set": {"status": args.status}})
    print(f"✅ set-status affected: {res.modified_count}")

def cmd_add_tags(args):
    c = col()
    email_lc = args.email.strip().lower()
    tags = parse_tags(args.tags)
    res = c.update_one({"email_lc": email_lc}, {"$addToSet": {"tags": {"$each": tags}}})
    print(f"✅ add-tags affected: {res.modified_count}")

def cmd_remove_tags(args):
    c = col()
    email_lc = args.email.strip().lower()
    tags = parse_tags(args.tags)
    res = c.update_one({"email_lc": email_lc}, {"$pull": {"tags": {"$in": tags}}})
    print(f"✅ remove-tags affected: {res.modified_count}")

def cmd_list(args):
    c = col()
    q = {}
    if args.status: q["status"] = args.status
    if args.tags:   q["tags"]   = {"$in": parse_tags(args.tags)}
    cur = c.find(q, {"_id":0,"email":1,"status":1,"tags":1}).sort("email_lc", ASCENDING)
    if args.limit: cur = cur.limit(int(args.limit))
    cnt = 0
    for d in cur:
        print(f"{d.get('email'):40s}  status={d.get('status','')}  tags={','.join(d.get('tags',[]))}")
        cnt += 1
    print(f"Total: {cnt}")

def cmd_import_csv(args):
    c = col()
    default_status = args.default_status
    default_tags   = parse_tags(args.default_tags)
    n=0
    with open(args.file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = (row.get("email") or "").strip()
            if not email: continue
            status = (row.get("status") or default_status).strip()
            tags   = parse_tags(row.get("tags")) or default_tags
            doc = {"email": email, "email_lc": email.lower(), "status": status, "tags": tags}
            c.update_one({"email_lc": doc["email_lc"]}, {"$set": doc}, upsert=True)
            n += 1
    print(f"✅ imported/upserted: {n}")

def cmd_export_csv(args):
    c = col()
    q = {}
    if args.status: q["status"] = args.status
    if args.tags:   q["tags"]   = {"$in": parse_tags(args.tags)}
    cur = c.find(q, {"_id":0,"email":1,"status":1,"tags":1}).sort("email_lc", ASCENDING)
    with open(args.file, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["email","status","tags"])
        n=0
        for d in cur:
            w.writerow([d.get("email",""), d.get("status",""), ",".join(d.get("tags",[]))])
            n+=1
    print(f"✅ exported: {n} -> {args.file}")

def cmd_ensure_index(_):
    c = col()
    # email_lc 唯一索引；另外建 status / tags 的普通索引
    c.create_index([("email_lc", ASCENDING)], unique=True, name="uniq_email_lc")
    c.create_index([("status", ASCENDING)], name="idx_status")
    c.create_index([("tags", ASCENDING)],   name="idx_tags")
    print("✅ indexes ensured")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add");           s.add_argument("--email", required=True); s.add_argument("--status", default="active"); s.add_argument("--tags"); s.set_defaults(func=cmd_add)
    s = sub.add_parser("remove");        s.add_argument("--email", required=True); s.set_defaults(func=cmd_remove)
    s = sub.add_parser("set-status");    s.add_argument("--email", required=True); s.add_argument("--status", required=True); s.set_defaults(func=cmd_set_status)
    s = sub.add_parser("add-tags");      s.add_argument("--email", required=True); s.add_argument("--tags", required=True); s.set_defaults(func=cmd_add_tags)
    s = sub.add_parser("remove-tags");   s.add_argument("--email", required=True); s.add_argument("--tags", required=True); s.set_defaults(func=cmd_remove_tags)
    s = sub.add_parser("list");          s.add_argument("--status"); s.add_argument("--tags"); s.add_argument("--limit", type=int); s.set_defaults(func=cmd_list)
    s = sub.add_parser("import-csv");    s.add_argument("--file", required=True); s.add_argument("--default-status", default="active"); s.add_argument("--default-tags"); s.set_defaults(func=cmd_import_csv)
    s = sub.add_parser("export-csv");    s.add_argument("--file", required=True); s.add_argument("--status"); s.add_argument("--tags"); s.set_defaults(func=cmd_export_csv)
    s = sub.add_parser("ensure-index");  s.set_defaults(func=cmd_ensure_index)

    args = p.parse_args()
    try:
        args.func(args)
    except AssertionError as e:
        print(f"[ERR] {e}", file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    main()
