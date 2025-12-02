# Archive - 历史周刊存档

此文件夹用于保存所有已生成的历史周刊，这些文件会被提交到 Git 仓库。

## 文件命名格式

- `newsletter-YYYY-MM-DD.html`

例如：
- `newsletter-2025-01-15.html`
- `newsletter-2025-01-22.html`

## 说明

- 每次运行 `python scripts/api.py` 生成周刊时，会自动保存一份到此文件夹
- 此文件夹中的文件会被提交到 Git，方便查看历史周刊
- 工作目录 `output/` 文件夹中的文件不会被提交到 Git（在 .gitignore 中）

## 查看历史周刊

你可以通过 Git 历史查看所有已生成的周刊：

```bash
git log --oneline archive/
```

