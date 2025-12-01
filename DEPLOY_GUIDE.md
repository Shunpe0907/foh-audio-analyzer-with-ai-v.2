# 🚀 GitHub + Streamlit Cloud デプロイガイド

## 📋 必要なファイル（すべて揃ってます！）

```
ultra_simple/
├── pa_analyzer_ultra_simple.py  ← メインアプリ
├── requirements.txt              ← Pythonパッケージ
├── packages.txt                  ← システムパッケージ
├── .streamlit/
│   └── config.toml              ← Streamlit設定
├── START.txt
├── README.txt
├── ULTRA_SIMPLE.md
└── LARGE_FILE_SUPPORT.md
```

---

## 🎯 ステップ1: GitHubにアップロード

### 1-1. GitHubでリポジトリを作成

1. https://github.com にログイン
2. 右上の「+」→「New repository」
3. リポジトリ名: `pa-audio-analyzer`（任意）
4. **Public**を選択（Streamlit Cloudの無料プランはPublicのみ）
5. 「Create repository」クリック

### 1-2. ローカルでGitセットアップ

```bash
# ultra_simpleフォルダに移動
cd ultra_simple

# Gitを初期化
git init

# すべてのファイルを追加
git add .

# 初回コミット
git commit -m "初回コミット: PA Audio Analyzer V4.0"

# GitHubと接続（URLは自分のに変更）
git remote add origin https://github.com/あなたのユーザー名/pa-audio-analyzer.git

# メインブランチに変更
git branch -M main

# アップロード
git push -u origin main
```

**👤 初めてGitを使う場合**:
```bash
# ユーザー名とメールを設定
git config --global user.name "あなたの名前"
git config --global user.email "your-email@example.com"
```

---

## 🎯 ステップ2: Streamlit Cloudでデプロイ

### 2-1. Streamlit Cloudアカウント作成

1. https://share.streamlit.io にアクセス
2. 「Sign up」→「Continue with GitHub」
3. GitHubアカウントで連携

### 2-2. アプリをデプロイ

1. Streamlit Cloudにログイン後、「New app」をクリック
2. 設定を入力：
   ```
   Repository: あなたのユーザー名/pa-audio-analyzer
   Branch: main
   Main file path: pa_analyzer_ultra_simple.py
   ```
3. 「Deploy!」をクリック
4. 数分待つ...
5. 完了！🎉

---

## ✅ デプロイ成功の確認

### アプリのURL
```
https://あなたのユーザー名-pa-audio-analyzer-pa-analyzer-ultra-simple-xxxxx.streamlit.app
```

### ログイン情報
```
メール: admin@pa.local
パスワード: admin123
```

---

## 🔧 トラブルシューティング

### エラー1: `ModuleNotFoundError`
**原因**: requirements.txtが読み込まれてない

**対処法**:
1. requirements.txtがリポジトリのルートにあるか確認
2. Streamlit Cloudでアプリを「Reboot」

### エラー2: `File too large`
**原因**: アップロード上限の設定が反映されてない

**対処法**:
1. `.streamlit/config.toml`がリポジトリにあるか確認
2. Streamlit Cloudでアプリを「Reboot」

### エラー3: ビルドが失敗
**原因**: パッケージのバージョン不整合

**対処法**:
```bash
# requirements.txtを編集して再プッシュ
git add requirements.txt
git commit -m "requirements.txtを修正"
git push
```

---

## 📝 コード更新の手順

### ローカルで修正した場合

```bash
# 変更をコミット
git add .
git commit -m "○○を修正"

# GitHubにプッシュ
git push

# Streamlit Cloudが自動的に再デプロイ！
```

---

## ⚙️ Streamlit Cloud設定

### アプリの設定変更

1. Streamlit Cloudのダッシュボード
2. アプリの「⋮」メニュー→「Settings」
3. 設定変更可能：
   - Python version
   - Secrets（環境変数）
   - Resources

### シークレット設定（パスワード等）

1. Settings → Secrets
2. TOML形式で入力:
```toml
[passwords]
admin = "your-secure-password"
```

3. アプリ内で使用:
```python
import streamlit as st
password = st.secrets["passwords"]["admin"]
```

---

## 🎨 カスタムドメイン（有料プラン）

Streamlit Cloudの有料プランで独自ドメイン設定可能:
```
https://pa-analyzer.yourdomein.com
```

---

## 📊 制限事項

### Streamlit Cloud 無料プラン
- ✅ Public リポジトリのみ
- ✅ 1 GB RAM
- ✅ 1 CPU
- ✅ アプリは最大3つまで
- ⚠️ アイドル時は自動スリープ（初回アクセス時に起動）

### 大容量ファイル
- ✅ 2GBまでアップロード可能
- ⚠️ メモリ制限（1GB）に注意
- ⚠️ 500MB以上のファイルは処理が重い

---

## 🚀 有料プランの検討

### こんな場合は有料プラン推奨:
- 🔒 Privateリポジトリを使いたい
- 💪 より高速な処理が必要（2GB RAM, 2 CPU）
- 🌐 独自ドメインを使いたい
- 📈 複数のアプリを公開したい

料金: $20/月〜

---

## 📚 参考リンク

- Streamlit Cloud: https://share.streamlit.io
- ドキュメント: https://docs.streamlit.io/streamlit-community-cloud
- コミュニティ: https://discuss.streamlit.io

---

## 🎉 完了！

これであなたのPA Analyzerが世界中からアクセス可能に！

URLを共有すれば、誰でも使えます：
```
https://あなたのアプリURL.streamlit.app
```

---

## 💡 次のステップ

1. ✅ GitHubにアップロード
2. ✅ Streamlit Cloudでデプロイ
3. 🎯 URLを仲間に共有
4. 📊 フィードバックを収集
5. 🔧 改善を続ける

頑張ってください！🚀
