#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch TechSum highlights from products/affairs/innovation,
merge and pick global top-10 by heat (feed_num),
then render an HTML newsletter.

Usage:
  python scripts/generate_newsletter.py \
    [--token YOUR_TOKEN] \
    [--template src/newsletter_template.html] \
    [--outfile output/newsletter-YYYY-MM-DD.html]
"""

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

import requests
from dateutil import parser as dateparser
from jinja2 import Environment, FileSystemLoader, Template

API_ENDPOINTS = {
    "Products":   "https://dataserver.datasum.ai/techsum/api/v3/highlights/products",
    "Affairs":    "https://dataserver.datasum.ai/techsum/api/v3/highlights/affairs",
    "Innovation": "https://dataserver.datasum.ai/techsum/api/v3/highlights/innovation",
}

DEFAULT_INLINE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ heading or "Tech Highlights" }}</title>
<style>
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif; background:#f6f7f9; color:#222; line-height:1.6; margin:0;}
.container{max-width:760px;margin:32px auto;padding:0 16px;}
.header{text-align:center;padding:16px;}
.header h1{font-size:24px;margin:0 0 6px;}
.header p{font-size:14px;color:#666;margin:0;}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px;}
@media (max-width:640px){.grid{grid-template-columns:1fr;}}
.card{background:#fff;border:1px solid #e6e8eb;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.04);display:flex;flex-direction:column;}
.thumb{position:relative;width:100%;padding-top:56.25%;background:#f0f2f5;overflow:hidden;}
.thumb img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;}
.content{padding:14px;display:flex;flex-direction:column;gap:8px;}
.title{font-size:16px;font-weight:700;color:#111;text-decoration:none;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.meta{font-size:12px;color:#6b7280;display:flex;gap:10px;flex-wrap:wrap;}
.badge{background:#111;color:#fff;font-size:11px;padding:2px 6px;border-radius:6px;}
.summary{font-size:14px;color:#333;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;}
.footer{text-align:center;color:#8a8f98;font-size:12px;padding:24px 0;}
a{color:inherit;}
.cat{font-weight:600;opacity:.8}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>{{ heading or "Tech Highlights" }}</h1>
    <p>{{ date or "" }}</p>
  </div>
  <div class="grid">
    {% for it in items %}
    <article class="card">
      <div class="thumb">
        {% if it.image %}<a href="{{ it.link or '#' }}" target="_blank" rel="noopener"><img src="{{ it.image }}" alt="{{ it.title|e }}"></a>{% endif %}
      </div>
      <div class="content">
        <a class="title" href="{{ it.link or '#' }}" target="_blank" rel="noopener">{{ it.title }}</a>
        <div class="meta">
          <span class="cat">{{ it.category }}</span>
          {% if it.date %}<span>{{ it.date.split(' ')[0] }}</span>{% endif %}
          <span class="badge">热度 {{ it.feed_num }}</span>
        </div>
        {% if it.summary %}<div class="summary">{{ it.summary }}</div>{% endif %}
      </div>
    </article>
    {% endfor %}
  </div>
  <div class="footer">© {{ year or "" }} Tech Newsletter</div>
</div>
</body></html>"""

def safe_parse_dt(s: str):
    from datetime import datetime, timezone
    if not s:
        return datetime(1970,1,1,tzinfo=timezone.utc)
    try:
        return dateparser.parse(s).astimezone(timezone.utc)
    except Exception:
        return datetime(1970,1,1,tzinfo=timezone.utc)

def fetch_json(url: str, token: str | None) -> Any:
    headers = {"accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def normalize_items(data: Any, category: str) -> List[Dict]:
    items: List[Dict] = []

    def mk(v: Dict, title_key: str = "") -> Dict:
        title = v.get("suggested_headline") or v.get("title") or title_key or "Untitled"
        summary_full = (v.get("group_summary") or "").strip()
        summary = summary_full.split("|")[0].strip() if "|" in summary_full else summary_full
        date = v.get("earliest_published") or ""
        feed = v.get("feed_num", 0)
        artnum = v.get("article_num", 0)
        # image
        img = ""
        imgs = v.get("images") or []
        if isinstance(imgs, list) and imgs:
            img = imgs[0].get("image_link") or imgs[0].get("url") or ""
        # link
        link = "#"
        arts = v.get("articles") or []
        if isinstance(arts, list) and arts:
            link = arts[0].get("link") or arts[0].get("url") or "#"

        return {
            "category": category,
            "title": title,
            "summary": summary,
            "date": date,
            "date_dt": safe_parse_dt(date),
            "feed_num": feed,
            "article_num": artnum,
            "image": img,
            "link": link,
        }

    if isinstance(data, list):
        for v in data:
            if isinstance(v, dict):
                items.append(mk(v))
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                items.append(mk(v, k))
    return items

def pick_top10(all_items: List[Dict]) -> List[Dict]:
    # 排序：feed_num(desc) -> article_num(desc) -> date(desc)
    return sorted(
        all_items,
        key=lambda x: (x.get("feed_num", 0), x.get("article_num", 0), x.get("date_dt")),
        reverse=True
    )[:10]

def render_html(items: List[Dict], template_path: str) -> str:
    now = datetime.now()
    if os.path.isfile(template_path):
        env = Environment(loader=FileSystemLoader(os.path.dirname(template_path) or "."))
        tpl = env.get_template(os.path.basename(template_path))
    else:
        tpl = Template(DEFAULT_INLINE_TEMPLATE)
    return tpl.render(
        heading="Tech Highlights (Top 10)",
        date=now.strftime("%Y-%m-%d"),
        items=items,
        year=now.year,
    )

def ensure_dir(p: str):
    d = os.path.dirname(p)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def main():
    import argparse
    now = datetime.now().strftime("%Y-%m-%d")
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=os.getenv("TECHSUM_API_KEY"))
    ap.add_argument("--template", default="src/newsletter_template.html")
    ap.add_argument("--outfile", default=f"output/newsletter-{now}.html")
    args = ap.parse_args()

    all_items: List[Dict] = []
    for cat, url in API_ENDPOINTS.items():
        try:
            raw = fetch_json(url, args.token)
            all_items.extend(normalize_items(raw, category=cat))
        except requests.HTTPError as e:
            sys.stderr.write(f"[HTTP {e.response.status_code}] {cat}: {url}\n")
        except Exception as e:
            sys.stderr.write(f"[Error] {cat}: {e}\n")

    if not all_items:
        sys.stderr.write("No items fetched from any endpoint.\n")
        sys.exit(1)

    top10 = pick_top10(all_items)

    # 控制台预览
    for i, it in enumerate(top10, 1):
        print(f"{i}. [{it['category']}] 热度 {it['feed_num']} | {it['date']}")
        print(f"   {it['title']}")
        if it.get("summary"):
            print(f"   {it['summary']}")
        print(f"   {it['link']}\n")

    # 渲染 HTML
    html = render_html(top10, args.template)
    ensure_dir(args.outfile)
    with open(args.outfile, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 已生成: {args.outfile}")

if __name__ == "__main__":
    main()
