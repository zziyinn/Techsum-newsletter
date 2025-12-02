#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch TechSum highlights from products/affairs/innovation,
merge, de-duplicate, rank, then render an HTML newsletter.

Usage:
  python scripts/generate_newsletter.py \
    [--token YOUR_TOKEN] \
    [--template src/newsletter_template.html] \
    [--outfile output/newsletter-YYYY-MM-DD.html]
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple, Optional
from urllib.parse import urlparse, urlunparse

import requests
from dateutil import parser as dateparser
from jinja2 import Environment, FileSystemLoader, Template

# ============ 常量 ============
API_ENDPOINTS = {
    "Products":   "https://dataserver.datasum.ai/techsum/api/v3/highlights/products",
    "Affairs":    "https://dataserver.datasum.ai/techsum/api/v3/highlights/affairs",
    "Innovation": "https://dataserver.datasum.ai/techsum/api/v3/highlights/innovation",
}

# 项目根目录（scripts 的上一级）
ROOT_DIR = Path(__file__).resolve().parents[1]

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

# ============== utils ==============
def safe_parse_dt(s: str):
    if not s:
        return datetime(1970,1,1,tzinfo=timezone.utc)
    try:
        dt = dateparser.parse(s)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return datetime(1970,1,1,tzinfo=timezone.utc)

def fetch_json(url: str, token: Optional[str]) -> Any:
    headers = {"accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def normalize_items(data: Any, category: str) -> List[Dict]:
    """把接口返回标准化为统一字段。"""
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

        # link（优先取第一篇文章）
        link = "#"
        arts = v.get("articles") or []
        if isinstance(arts, list) and arts:
            link = arts[0].get("link") or arts[0].get("url") or "#"

        return {
            "category": category,
            "title": str(title).strip(),
            "summary": str(summary).strip(),
            "date": str(date).strip(),
            "date_dt": safe_parse_dt(date),
            "feed_num": int(feed) if str(feed).isdigit() else (feed or 0),
            "article_num": int(artnum) if str(artnum).isdigit() else (artnum or 0),
            "image": str(img).strip(),
            "link": str(link).strip(),
        }

    if isinstance(data, list):
        for v in data:
            if isinstance(v, dict):
                items.append(mk(v))
    elif isinstance(data, dict):
        # 可能是 dict keyed by topic；或某些 key 是 list
        for k, v in data.items():
            if isinstance(v, dict):
                items.append(mk(v, k))
            elif isinstance(v, list):
                for e in v:
                    if isinstance(e, dict):
                        items.append(mk(e, k))
    return items

# ---- 去重：规范化 URL + 标题相似 ----
_PUNCT = re.compile(r"[^\w\s]+", flags=re.U)
_WS = re.compile(r"\s+", flags=re.U)

def normalize_title(title: str) -> str:
    t = (title or "").strip().lower()
    t = _PUNCT.sub(" ", t)
    t = _WS.sub(" ", t).strip()
    return t

def canonical_url(url: str) -> str:
    try:
        u = urlparse(url)
        # 去掉查询串, 标准化结尾斜杠
        path = re.sub(r"/+$", "", u.path or "")
        scheme = "https" if u.scheme in ("http", "https", "") else u.scheme
        return urlunparse((scheme, u.netloc.lower(), path, "", "", ""))
    except Exception:
        return url

def title_similarity(a: str, b: str) -> float:
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio()

def pick_better(a: Dict, b: Dict) -> Dict:
    # feed_num 高者优先；再比发布时间新；再比 article_num；最后保留 a
    fa, fb = a.get("feed_num", 0) or 0, b.get("feed_num", 0) or 0
    if fa != fb:
        return a if fa > fb else b
    da, db = a.get("date_dt"), b.get("date_dt")
    if da != db:
        return a if da > db else b
    aa, ab = a.get("article_num", 0) or 0, b.get("article_num", 0) or 0
    if aa != ab:
        return a if aa > ab else b
    return a

def dedupe_items(items: List[Dict]) -> List[Dict]:
    chosen: List[Dict] = []
    seen: List[Tuple[str, str]] = []  # (canon_url, norm_title)

    for cur in items:
        cu = canonical_url(cur.get("link", ""))
        ct = normalize_title(cur.get("title", ""))

        dup_idx = -1
        for idx, (u_seen, t_seen) in enumerate(seen):
            if cu and u_seen and cu == u_seen:
                dup_idx = idx
                break
            if ct and t_seen and title_similarity(ct, t_seen) >= 0.90:
                dup_idx = idx
                break

        if dup_idx == -1:
            chosen.append(cur)
            seen.append((cu, ct))
        else:
            better = pick_better(cur, chosen[dup_idx])
            if better is cur:
                chosen[dup_idx] = cur
                seen[dup_idx] = (cu, ct)
            # 否则丢弃当前，达到“重复不出现，顺延到下一个”
    return chosen

# ---- 排序与选 TopN（优先有图） ----
def rank_items(items: List[Dict], topk: int = 10) -> List[Dict]:
    # 先按热度 -> 文章数 -> 时间
    items_sorted = sorted(
        items,
        key=lambda x: (x.get("feed_num", 0) or 0, x.get("article_num", 0) or 0, x.get("date_dt")),
        reverse=True
    )
    # 优先保留有图的；不够再用无图补齐
    with_img = [i for i in items_sorted if i.get("image")]
    no_img  = [i for i in items_sorted if not i.get("image")]
    merged = with_img + no_img
    return merged[:topk]

# ---- 模板加载：优先根目录，再脚本相对，最后内置 ----
def resolve_template(template_path: str) -> Tuple[Template, bool]:
    """
    返回 (template_obj, using_inline)
    优先：绝对路径 → 根目录相对路径（ROOT_DIR/…）→ 脚本相对路径（scripts/..）→ 内置模板
    """
    cand = Path(template_path)
    if not cand.is_file():
        cand_root = (ROOT_DIR / template_path).resolve()
        if cand_root.is_file():
            cand = cand_root
    if not cand.is_file():
        cand_script = (Path(__file__).resolve().parent / ".." / template_path).resolve()
        if cand_script.is_file():
            cand = cand_script

    if cand.is_file():
        env = Environment(loader=FileSystemLoader(str(cand.parent)))
        return env.get_template(cand.name), False
    else:
        return Template(DEFAULT_INLINE_TEMPLATE), True

def render_html(items: List[Dict], template_path: str) -> str:
    now = datetime.now()
    tpl, _ = resolve_template(template_path)
    return tpl.render(
        heading="Tech Highlights (Top 10)",
        date=now.strftime("%Y-%m-%d"),
        items=items,
        year=now.year,
        preheader=os.getenv("PREHEADER", "⚡ Weekly TechSum Highlights: The Top 10 Noteworthy Tech Trends and Developments."),
        unsub_url=os.getenv("UNSUB_URL", "https://web-production-914f7.up.railway.app/unsubscribe.html")
    )

# ---- 确保输出目录存在；相对路径一律相对 ROOT_DIR ----
def normalize_outfile(p: str) -> Path:
    out_path = Path(p)
    if not out_path.is_absolute():
        out_path = (ROOT_DIR / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return out_path

# ============== main ==============
def main():
    import argparse
    today = datetime.now().strftime("%Y-%m-%d")

    # 默认输出：固定落到 根目录/output/
    default_outfile = ROOT_DIR / "output" / f"newsletter-{today}.html"

    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=os.getenv("TECHSUM_API_KEY"))
    ap.add_argument("--template", default="src/newsletter_template.html")
    ap.add_argument("--outfile", default=str(default_outfile))
    args = ap.parse_args()

    # 抓取
    all_items: List[Dict] = []
    for cat, url in API_ENDPOINTS.items():
        try:
            raw = fetch_json(url, args.token)
            std = normalize_items(raw, category=cat)
            all_items.extend(std)
        except requests.HTTPError as e:
            sys.stderr.write(f"[HTTP {e.response.status_code}] {cat}: {url}\n")
        except Exception as e:
            sys.stderr.write(f"[Error] {cat}: {e}\n")

    if not all_items:
        sys.stderr.write("No items fetched from any endpoint.\n")
        sys.exit(1)

    # 去重 → 排序选 Top10
    uniq = dedupe_items(all_items)
    top10 = rank_items(uniq, topk=10)

    # 控制台预览
    for i, it in enumerate(top10, 1):
        print(f"{i}. [{it['category']}] 热度 {it['feed_num']} | {it['date']}")
        print(f"   {it['title']}")
        if it.get("summary"):
            print(f"   {it['summary']}")
        print(f"   {it['link']}\n")

    # 渲染
    html = render_html(top10, args.template)

    # 固定写入 根目录/output/...
    out_path = normalize_outfile(args.outfile)
    out_path.write_text(html, encoding="utf-8")
    print(f"✅ 已生成: {out_path}")
    
    # 同时复制到 archive/ 文件夹（用于 Git 提交）
    archive_dir = ROOT_DIR / "archive"
    archive_dir.mkdir(exist_ok=True)
    archive_path = archive_dir / out_path.name
    archive_path.write_text(html, encoding="utf-8")
    print(f"📦 已归档: {archive_path}")

if __name__ == "__main__":
    main()
