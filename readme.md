# 增
python scripts/subscribers.py add --email someone@example.com --tags preview --status active
# 改
python scripts/subscribers.py set-status --email someone@example.com --status inactive
python scripts/subscribers.py add-tags --email someone@example.com --tags cn
# 删
python scripts/subscribers.py remove --email someone@example.com
# 查
python scripts/subscribers.py list --status active --tags preview

本地生成 + 发送

python scripts/api.py
LATEST=$(ls -t output/newsletter-*.html | head -n 1)
python scripts/send_email.py \
  --file "$LATEST" \
  --subject "TechSum Weekly · $(date +%Y-%m-%d)" \
  --from-mongo --tags "preview" --status active --limit 50 \
  --batch-size 10 --sleep 2
