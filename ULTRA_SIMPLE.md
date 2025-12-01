# 🚀 超簡単版 - 楽器分離付き

## 基本インストール（1行）

```bash
pip install streamlit numpy scipy matplotlib librosa soundfile
```

## 楽器分離AI（オプション）

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install demucs
```

**GPU版（NVIDIA GPU搭載の場合）**:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install demucs
```

## 起動

```bash
streamlit run pa_analyzer_ultra_simple.py
```

## ログイン

- メール: `admin@pa.local`
- パスワード: `admin123`

## 完了！🎉

---

## できること

### 基本機能（すぐ使える）
✅ 音源解析（RMS, Peak, Crest, Stereo）  
✅ AI学習（3回目から傾向分析）  
✅ 改善提案  
✅ 履歴保存  

### 楽器分離AI（オプション）
🎸 Vocals（ボーカル）  
🥁 Drums（ドラム）  
🎸 Bass（ベース）  
🎹 Other（ギター、キーボードなど）

---

## 使い方

1. **まず基本だけインストール**
   ```bash
   pip install streamlit numpy scipy matplotlib librosa soundfile
   ```

2. **動作確認**
   ```bash
   streamlit run pa_analyzer_ultra_simple.py
   ```

3. **楽器分離が欲しくなったら追加**
   ```bash
   pip install torch torchaudio demucs
   ```

4. **アプリ再起動**
   - 自動的に「楽器分離AI使用」チェックボックスが有効に！

---

## エラーが出たら

### Mac/Linux:
```bash
pip3 install streamlit numpy scipy matplotlib librosa soundfile
python3 -m streamlit run pa_analyzer_ultra_simple.py
```

### Windows:
```bash
py -m pip install streamlit numpy scipy matplotlib librosa soundfile
py -m streamlit run pa_analyzer_ultra_simple.py
```

---

## 💡 ポイント

- **楽器分離なし**: 5秒で解析完了
- **楽器分離あり**: 2-3分かかるけど超詳細！
- チェックボックスで簡単切り替え
- 楽器分離は後からでもインストールOK

---

**シンプルだけど全機能！** 😎
