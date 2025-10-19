#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Send newsletter HTML via Gmail.
- Supports recipients from CLI/ENV/file and/or MongoDB Atlas.
- Batching with sleep to avoid provider limits.

Usage examples:
  # 从 Mongo 取 active+preview ，分批发送
  EMAIL_USER=... EMAIL_PASS=... MONGODB_URI=... \
  python scripts/send_email.py \
    --file output/newsletter-2025-10-13.html \
    --subject "TechSum Weekly · 2025-10-13" \
    --from-mongo --tags "preview" --status active \
    --batch-size 80 --sleep 4

  # 传统：直接传收件人
  EMAIL_USER=... EMAIL_PASS=... \
  python scripts/send_email.py \
    --file output/newsletter-2025-10-13.html \
    --to "a@x.com,b@y.com" --subject "Subject"
"""

import os, time, argparse, smtplib
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid

# --- load .env for local dev (safe if missing on CI) ---
try:
    from dotenv import load_dotenv
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except Exception:
    pass

# ---------------- small utils ----------------
def parse_list(s: str | None) -> list[str]:
    if not s:
        return []
    import re
    parts = re.split(r"[,\s;]+", s.strip())
    return [p for p in parts if p]

def uniq(seq):
    seen = set(); out = []
    for x in seq:
        if x not in seen:
            seen.add(x); out.append(x)
    return out

# ---------------- mongo helpers ----------------
def get_mongo_collection():
    """Return pymongo collection or None if MONGODB_URI not set."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    from pymongo import MongoClient
    from pymongo.server_api import ServerApi
    dbname = os.getenv("MONGODB_DB", "techsum")
    collname = os.getenv("MONGODB_COLL", "subscribers")
    client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=8000)
    db = client[dbname]
    return db[collname]

def fetch_recipients_from_mongo(tags=None, status="active", limit=None) -> list[str]:
    """Fetch emails from MongoDB, filter by status and optional tags."""
    coll = get_mongo_collection()
    # 修复：Collection 不支持布尔判断，必须和 None 比较
    if coll is None:
        return []
    q = {"status": status}
    if tags:
        q["tags"] = {"$in": tags}
    projection = {"_id": 0, "email": 1}
    cur = coll.find(q, projection)
    if limit:
        cur = cur.limit(int(limit))
    emails = []
    for doc in cur:
        e = (doc.get("email") or "").strip().lower()
        if e:
            emails.append(e)
    return uniq(emails)

# ---------------- main send ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="HTML file to send")
    ap.add_argument("--subject", default=os.getenv("EMAIL_SUBJECT", "TechSum Weekly Preview"))

    # classic recipients
    ap.add_argument("--to", help="comma/semicolon/space separated emails")
    ap.add_argument("--cc", help="comma/semicolon/space separated emails")
    ap.add_argument("--bcc", help="comma/semicolon/space separated emails")
    ap.add_argument("--to-file", help="path to a file of emails (one per line)")

    # mongo recipients
    ap.add_argument("--from-mongo", action="store_true", help="Pull recipients from MongoDB Atlas")
    ap.add_argument("--tags", help="filter by tags (comma/semicolon/space separated)")
    ap.add_argument("--status", default="active", help="status filter (default=active)")
    ap.add_argument("--limit", type=int, help="max recipients fetched from Mongo")

    # batching
    ap.add_argument("--batch-size", type=int, default=80, help="max recipients per batch (default 80)")
    ap.add_argument("--sleep", type=float, default=4.0, help="seconds between batches (default 4s)")

    args = ap.parse_args()

    user = os.getenv("EMAIL_USER")
    pwd  = os.getenv("EMAIL_PASS")
    assert user and pwd, "EMAIL_USER/EMAIL_PASS required"

    # parse CLI/ENV
    to_list  = parse_list(args.to)  or parse_list(os.getenv("MAIL_TO"))
    cc_list  = parse_list(args.cc)  or parse_list(os.getenv("MAIL_CC"))
    bcc_list = parse_list(args.bcc) or parse_list(os.getenv("MAIL_BCC"))

    # file list (optional)
    file_list = []
    if args.to_file:
        with open(args.to_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    file_list.append(line)

    # mongo list (optional)
    mongo_list = []
    if args.from_mongo:
        tag_list = parse_list(args.tags)
        mongo_list = fetch_recipients_from_mongo(tags=tag_list, status=args.status, limit=args.limit)

    # priority: CLI/ENV > file > Mongo
    base_rcpts = to_list or file_list or []
    all_rcpts = uniq(base_rcpts + cc_list + bcc_list + mongo_list)
    assert all_rcpts, "No recipients: use --from-mongo or provide --to/MAIL_TO"

    with open(args.file, "r", encoding="utf-8") as f:
        html = f.read()

    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = args.subject
    msg["From"] = formataddr(("TechSum", user))
    if base_rcpts: msg["To"] = ", ".join(base_rcpts)
    if cc_list:    msg["Cc"] = ", ".join(cc_list)
    msg["Message-ID"] = make_msgid(domain=user.split("@")[-1])

    batch = max(1, int(args.batch_size))
    delay = max(0.0, float(args.sleep))
    total = len(all_rcpts); sent = 0

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as s:
        s.starttls(); s.login(user, pwd)
        for i in range(0, total, batch):
            chunk = all_rcpts[i:i+batch]
            s.sendmail(user, chunk, msg.as_string())
            sent += len(chunk)
            print(f"✅ Batch {i//batch+1}: sent {len(chunk)} (total {sent}/{total})")
            if i + batch < total and delay > 0:
                time.sleep(delay)

    print(f"🎉 Done. Sent to {sent} recipients.")

if __name__ == "__main__":
    main()
