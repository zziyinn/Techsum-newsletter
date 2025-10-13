#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, glob, smtplib, pathlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"

def find_latest_html() -> pathlib.Path:
    files = sorted(OUTPUT_DIR.glob("newsletter-*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError("No newsletter-*.html found in output/")
    return files[0]

def to_plain(html: str) -> str:
    import re
    txt = re.sub(r"<(script|style)[\\s\\S]*?</\\1>", "", html, flags=re.I)
    txt = re.sub(r"<[^>]+>", "", txt)
    txt = re.sub(r"\\n\\s*\\n+", "\\n\\n", txt)
    return txt.strip()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="HTML file to send; default: latest in output/")
    args = ap.parse_args()

    html_path = pathlib.Path(args.file).resolve() if args.file else find_latest_html()
    html = html_path.read_text(encoding="utf-8")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("EMAIL_USER")
    pwd  = os.getenv("EMAIL_PASS")
    to_list  = [s.strip() for s in os.getenv("MAIL_TO", "").split(",") if s.strip()]
    bcc_list = [s.strip() for s in os.getenv("MAIL_BCC", "").split(",") if s.strip()]
    subject_prefix = os.getenv("SUBJECT_PREFIX", "[TechSum Weekly]")

    assert user and pwd, "EMAIL_USER/EMAIL_PASS required"
    assert to_list or bcc_list, "MAIL_TO or MAIL_BCC required"

    # 主题采用文件名中的日期
    date_part = html_path.stem.replace("newsletter-","")
    subject = f"{subject_prefix} {date_part}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(to_list) if to_list else user

    msg.attach(MIMEText(to_plain(html), "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()
        s.login(user, pwd)
        recipients = (to_list or []) + (bcc_list or [])
        if not recipients:
            recipients = [user]
        s.sendmail(user, recipients, msg.as_string())

    print(f"📧 Sent preview for {html_path.name} to: {', '.join(to_list + bcc_list)}")

if __name__ == "__main__":
    main()
