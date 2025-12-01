# ⚡ 3分でデプロイ - クイックスタート

## 📦 準備完了！

すべてのファイルが揃っています：
- ✅ pa_analyzer_ultra_simple.py
- ✅ requirements.txt
- ✅ packages.txt
- ✅ .streamlit/config.toml

---

## 🚀 3ステップでデプロイ

### ステップ1: GitHubにアップロード（2分）

```bash
# ultra_simpleフォルダで実行
git init
git add .
git commit -m "初回コミット"
git remote add origin https://github.com/あなたのユーザー名/pa-audio-analyzer.git
git branch -M main
git push -u origin main
```

### ステップ2: Streamlit Cloudでデプロイ（1分）

1. https://share.streamlit.io にアクセス
2. GitHubでログイン
3. 「New app」クリック
4. リポジトリ選択 → 「Deploy!」
5. 完了！

### ステップ3: アクセス

```
https://あなたのアプリ名.streamlit.app
```

**ログイン情報**:
- メール: admin@pa.local
- パスワード: admin123

---

## 📱 完成イメージ

```
あなたのアプリ.streamlit.app
    ↓
🎛️ PA Audio Analyzer
    ↓
ログイン → 音源アップロード → 解析 → 結果表示
```

---

## 🔧 初めてGitを使う場合

```bash
# 最初に1回だけ設定
git config --global user.name "あなたの名前"
git config --global user.email "your-email@example.com"
```

---

## ⚠️ よくあるエラー

### 「Permission denied」
→ GitHubの認証が必要
```bash
# Personal Access Tokenを使う
# Settings → Developer settings → Personal access tokens
```

### 「Repository not found」
→ URLが間違ってる
```bash
# 正しいURLを確認
git remote -v
```

---

## 💡 詳しい説明

詳細は `DEPLOY_GUIDE.md` を参照

---

**たった3分で世界公開！** 🌍
