# 旅行プランサイト

静的サイト（GitHub Pages 想定）です。

## ローカル起動

```bash
cd /path/to/hukushima_travel
python3 -m http.server 8765
```

ブラウザで http://localhost:8765 を開く。

## 構成

| パス | 内容 |
|------|------|
| `/` | プラン一覧 |
| `/plans/fukushima-aizu-jul2025/` | 福島・会津 |
| `/plans/sendai-aug2026/` | 仙台・松島 |

## Git への更新

```bash
cd /path/to/hukushima_travel
git add .
git status
git commit -m "変更内容の説明"
git push origin main
```

初回のみ remote 未設定なら:

```bash
git remote add origin git@github.com:k-masahiro116/travel_plan.git
git push -u origin main
```

## 公開

`main` への push で GitHub Actions が Pages にデプロイします。  
Settings → Pages → Source は **GitHub Actions** にしてください。
