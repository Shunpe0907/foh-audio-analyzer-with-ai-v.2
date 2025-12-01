"""
PA Audio Analyzer V4.0 - 超シンプル版（長時間音源対応）
最大2時間の音源を解析可能

使い方:
    pip install streamlit numpy scipy matplotlib librosa soundfile
    streamlit run pa_analyzer_ultra_simple.py
"""

import streamlit as st
import numpy as np
try:
    import librosa
    LIBROSA_OK = True
except:
    LIBROSA_OK = False

# 楽器分離AI（オプション）
try:
    import torch
    import torchaudio
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    DEMUCS_OK = True
except:
    DEMUCS_OK = False

import matplotlib.pyplot as plt
from scipy import signal
import io
from pathlib import Path
import tempfile
import json
from datetime import datetime
import os
import hashlib
import secrets
import warnings
warnings.filterwarnings('ignore')

# 大容量ファイル対応の設定
st.set_page_config(
    page_title="PA Analyzer", 
    page_icon="🎛️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
.big {font-size:2rem; font-weight:bold; text-align:center;}
.good {background:#e6ffe6; padding:1rem; border-left:4px solid #44ff44; margin:0.5rem 0;}
.bad {background:#ffe6e6; padding:1rem; border-left:4px solid #ff4444; margin:0.5rem 0;}
.ai {background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:1rem; margin:0.5rem 0;}
</style>
""", unsafe_allow_html=True)


# 認証
class Auth:
    def __init__(self):
        self.file = Path('users.json')
        self.users = self.load()
        
    def load(self):
        if self.file.exists():
            with open(self.file) as f: return json.load(f)
        u = {'admin@pa.local': {'pw': self.hash('admin123'), 'name': '管理者'}}
        with open(self.file, 'w') as f: json.dump(u, f)
        return u
    
    def hash(self, pw):
        s = secrets.token_hex(8)
        return f"{s}:{hashlib.sha256((pw+s).encode()).hexdigest()}"
    
    def check(self, pw, stored):
        s, h = stored.split(':')
        return hashlib.sha256((pw+s).encode()).hexdigest() == h
    
    def login(self, email, pw):
        if email in self.users and self.check(pw, self.users[email]['pw']):
            return True, self.users[email]
        return False, None
    
    def register(self, email, pw, name):
        if email in self.users: return False
        self.users[email] = {'pw': self.hash(pw), 'name': name}
        with open(self.file, 'w') as f: json.dump(self.users, f)
        return True


# AI学習
class AI:
    def __init__(self):
        self.file = Path('ai.json')
        self.data = json.load(open(self.file)) if self.file.exists() else {'users': {}}
    
    def learn(self, email, rms):
        if email not in self.data['users']:
            self.data['users'][email] = {'rms': []}
        self.data['users'][email]['rms'].append(rms)
        with open(self.file, 'w') as f: json.dump(self.data, f)
    
    def insight(self, email, rms):
        if email not in self.data['users']: return "🎉 初回解析！"
        history = self.data['users'][email]['rms']
        if len(history) < 3: return f"📊 解析{len(history)}回目"
        avg = np.mean(history[-5:])
        if rms > avg + 2: return f"📈 音圧向上！+{rms-avg:.1f}dB"
        if rms < avg - 2: return f"📉 音圧低下。-{avg-rms:.1f}dB"
        return f"✅ 安定（平均{avg:.1f}dB）"


# 解析
class Analyzer:
    def __init__(self, path):
        if not LIBROSA_OK:
            raise Exception("librosaが必要です")
        
        # ファイルサイズ確認
        file_size = os.path.getsize(path) / (1024 * 1024)  # MB
        
        # 大きいファイルはチャンク読み込み
        if file_size > 100:  # 100MB以上
            st.info(f"📦 大容量ファイル検出（{file_size:.0f}MB）- チャンク処理で読み込みます")
            self.large_file = True
            self.path = path
            # サンプルだけ先読み（全体の情報取得用）
            self.y, self.sr = librosa.load(path, sr=44100, mono=False, duration=30)
        else:
            self.large_file = False
            self.y, self.sr = librosa.load(path, sr=44100, mono=False)
        
        if len(self.y.shape) == 1:
            self.y = np.stack([self.y, self.y])
    
    def analyze(self):
        """チャンク処理で長時間音源にも対応"""
        
        if self.large_file:
            # 大容量ファイルはチャンク処理
            return self._analyze_large_file()
        else:
            # 通常処理
            return self._analyze_normal()
    
    def _analyze_normal(self):
        """通常サイズのファイル解析"""
        mono = np.mean(self.y, axis=0)
        
        # RMS
        rms = 20 * np.log10(np.sqrt(np.mean(mono**2)) + 1e-10)
        
        # Peak
        peak = 20 * np.log10(np.max(np.abs(mono)) + 1e-10)
        
        # Stereo
        L, R = self.y[0], self.y[1]
        mid = (L+R)/2
        side = (L-R)/2
        stereo = (np.sum(side**2) / (np.sum(mid**2)+np.sum(side**2)+1e-10)) * 100
        
        return {
            'rms': float(rms),
            'peak': float(peak),
            'crest': float(peak - rms),
            'stereo': float(stereo),
            'duration': len(mono) / self.sr
        }
    
    def _analyze_large_file(self):
        """大容量ファイルをチャンク処理で解析"""
        import soundfile as sf
        
        chunk_size = 44100 * 30  # 30秒ずつ
        rms_values = []
        peak_values = []
        stereo_values = []
        
        with sf.SoundFile(self.path) as f:
            total_frames = len(f)
            duration = total_frames / f.samplerate
            num_chunks = int(np.ceil(total_frames / chunk_size))
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(num_chunks):
                # チャンク読み込み
                f.seek(i * chunk_size)
                chunk = f.read(chunk_size)
                
                if len(chunk) == 0:
                    break
                
                # ステレオ化
                if len(chunk.shape) == 1:
                    chunk = np.stack([chunk, chunk], axis=-1)
                
                # 転置してlibrosa形式に
                chunk = chunk.T
                
                # 各指標を計算
                mono = np.mean(chunk, axis=0)
                
                # RMS
                rms = np.sqrt(np.mean(mono**2))
                rms_values.append(rms)
                
                # Peak
                peak = np.max(np.abs(mono))
                peak_values.append(peak)
                
                # Stereo
                L, R = chunk[0], chunk[1]
                mid = (L+R)/2
                side = (L-R)/2
                stereo = (np.sum(side**2) / (np.sum(mid**2)+np.sum(side**2)+1e-10)) * 100
                stereo_values.append(stereo)
                
                # 進捗更新
                progress = (i + 1) / num_chunks
                progress_bar.progress(progress)
                status_text.text(f"解析中... {int(progress*100)}% ({i+1}/{num_chunks}チャンク)")
            
            progress_bar.empty()
            status_text.empty()
            
            # 平均値を計算
            avg_rms = np.mean(rms_values)
            avg_peak = np.max(peak_values)  # Peakは最大値
            avg_stereo = np.mean(stereo_values)
            
            rms_db = 20 * np.log10(avg_rms + 1e-10)
            peak_db = 20 * np.log10(avg_peak + 1e-10)
            
            return {
                'rms': float(rms_db),
                'peak': float(peak_db),
                'crest': float(peak_db - rms_db),
                'stereo': float(avg_stereo),
                'duration': duration
            }


# 楽器分離
class Separator:
    def __init__(self):
        self.available = DEMUCS_OK
        self.model = None
        
        if self.available:
            try:
                self.model = get_model('htdemucs')
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
                self.model.to(self.device)
            except:
                self.available = False
    
    def separate(self, path):
        if not self.available:
            return None, "Demucs未インストール"
        
        # ファイルサイズチェック
        file_size = os.path.getsize(path) / (1024 * 1024)
        
        if file_size > 500:
            return None, f"ファイルが大きすぎます（{file_size:.0f}MB）。楽器分離は500MB以下を推奨"
        
        try:
            st.info("🎸 楽器分離処理中...（大容量ファイルは数分かかります）")
            
            audio, sr = torchaudio.load(path)
            
            # 長時間音源の場合は警告
            duration = audio.shape[1] / sr
            if duration > 600:  # 10分以上
                st.warning(f"⚠️ {duration/60:.1f}分の音源です。処理に時間がかかります")
            
            if audio.shape[0] == 1:
                audio = audio.repeat(2, 1)
            
            audio = audio.to(self.device).unsqueeze(0)
            
            with torch.no_grad():
                sources = apply_model(self.model, audio, device=self.device)
            
            sources = sources.squeeze(0).cpu().numpy()
            
            return {
                'drums': sources[0],
                'bass': sources[1],
                'other': sources[2],
                'vocals': sources[3]
            }, None
            
        except Exception as e:
            return None, f"エラー: {str(e)}"


# データ保存
class Storage:
    def __init__(self):
        self.dir = Path('data')
        self.dir.mkdir(exist_ok=True)
    
    def save(self, email, result, name, venue):
        file = self.dir / f"{email.replace('@','_').replace('.','_')}.json"
        data = json.load(open(file)) if file.exists() else []
        data.append({
            'time': datetime.now().isoformat(),
            'name': name,
            'venue': venue,
            'result': result
        })
        with open(file, 'w') as f: json.dump(data, f)
    
    def load(self, email):
        file = self.dir / f"{email.replace('@','_').replace('.','_')}.json"
        return json.load(open(file)) if file.exists() else []


# メイン
def main():
    if 'auth' not in st.session_state:
        st.session_state.auth = False
    
    if not st.session_state.auth:
        st.markdown('<p class="big">🎛️ PA Audio Analyzer</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["ログイン", "新規登録"])
        
        with tab1:
            email = st.text_input("メール", key="l_mail")
            pw = st.text_input("パスワード", type="password", key="l_pw")
            if st.button("ログイン", use_container_width=True, type="primary"):
                auth = Auth()
                ok, user = auth.login(email, pw)
                if ok:
                    st.session_state.auth = True
                    st.session_state.user = {'email': email, 'name': user['name']}
                    st.rerun()
                else:
                    st.error("ログイン失敗")
        
        with tab2:
            email = st.text_input("メール", key="r_mail")
            name = st.text_input("ユーザー名")
            pw = st.text_input("パスワード", type="password", key="r_pw")
            if st.button("登録", use_container_width=True, type="primary"):
                if email and name and pw:
                    auth = Auth()
                    if auth.register(email, pw, name):
                        st.success("✅ 登録完了！ログインしてください")
                    else:
                        st.error("既に登録済み")
        return
    
    # ログイン済み
    user = st.session_state.user
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.caption(user['email'])
        menu = st.radio("", ["🎵 解析", "📊 履歴", "🚪 ログアウト"], label_visibility="collapsed")
        if menu == "🚪 ログアウト":
            st.session_state.auth = False
            st.rerun()
    
    if menu == "🎵 解析":
        st.markdown('<p class="big">🎛️ 音源解析</p>', unsafe_allow_html=True)
        
        if not LIBROSA_OK:
            st.error("❌ librosaがインストールされていません")
            st.code("pip install librosa soundfile")
            return
        
        # 楽器分離の状態表示
        col1, col2 = st.columns(2)
        with col1:
            if DEMUCS_OK:
                st.success("✅ 楽器分離AI: 利用可能")
            else:
                st.info("ℹ️ 楽器分離AI: 未インストール")
        with col2:
            st.info("📦 最大2GB・2時間の音源に対応")
        
        with st.expander("📥 インストール方法"):
            st.code("""# 楽器分離AI
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install demucs""")
        
        st.markdown("---")
        
        # 大容量ファイル対応（2GB = 2048MB）
        file = st.file_uploader(
            "音源（WAV/MP3/FLAC）", 
            type=['wav', 'mp3', 'flac'],
            help="最大2GBまで対応。長時間音源も解析可能"
        )
        
        if file:
            # ファイル情報表示
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            st.caption(f"📦 ファイルサイズ: {file_size_mb:.1f}MB")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("解析名", "ライブ本番")
                venue = st.text_input("会場", "")
            with col2:
                st.write("")
                st.write("")
                use_separation = st.checkbox(
                    "🎸 楽器分離AI使用", 
                    value=False, 
                    disabled=not DEMUCS_OK or file_size_mb > 500,
                    help="500MB以下のファイルで利用可能。それ以上は基本解析のみ"
                )
            
            if file_size_mb > 500 and use_separation:
                st.warning("⚠️ 500MB以上のファイルは楽器分離を使用できません")
            
            if st.button("🚀 解析", type="primary", use_container_width=True):
                with st.spinner("解析中..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                        tmp.write(file.getvalue())
                        tmp_path = tmp.name
                    
                    try:
                        analyzer = Analyzer(tmp_path)
                        result = analyzer.analyze()
                        
                        # 時間情報
                        duration = result.get('duration', 0)
                        duration_str = f"{int(duration//60)}分{int(duration%60)}秒"
                        
                        # AI
                        ai = AI()
                        ai.learn(user['email'], result['rms'])
                        insight = ai.insight(user['email'], result['rms'])
                        
                        # 保存
                        storage = Storage()
                        storage.save(user['email'], result, name, venue)
                        
                        # 結果
                        st.success(f"✅ 完了！ 音源長さ: {duration_str}")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("RMS", f"{result['rms']:.1f}dB")
                        col2.metric("Peak", f"{result['peak']:.1f}dB")
                        col3.metric("Crest", f"{result['crest']:.1f}dB")
                        col4.metric("Stereo", f"{result['stereo']:.1f}%")
                        
                        # AI提案
                        st.markdown(f'<div class="ai">🧠 {insight}</div>', unsafe_allow_html=True)
                        
                        # 改善提案
                        rms = result['rms']
                        if -20 <= rms <= -16:
                            st.markdown('<div class="good">✅ RMS音圧が適切です</div>', unsafe_allow_html=True)
                        elif rms < -23:
                            st.markdown('<div class="bad">⚠️ 音圧が低い。マスターを上げて</div>', unsafe_allow_html=True)
                        
                        if result['peak'] > -1:
                            st.markdown('<div class="bad">⚠️ ピークが高すぎ。クリッピング注意</div>', unsafe_allow_html=True)
                        
                        # 楽器分離
                        if use_separation:
                            st.markdown("---")
                            st.markdown("### 🎸 楽器分離解析")
                            
                            with st.spinner("楽器を分離中...（数分かかります）"):
                                separator = Separator()
                                separated, error = separator.separate(tmp_path)
                                
                                if separated:
                                    st.success("✅ 分離完了！")
                                    
                                    # 各楽器の解析
                                    inst_names = {
                                        'vocals': '🎤 Vocals',
                                        'drums': '🥁 Drums',
                                        'bass': '🎸 Bass',
                                        'other': '🎹 Other'
                                    }
                                    
                                    for key, audio in separated.items():
                                        with st.expander(inst_names[key]):
                                            mono = np.mean(audio, axis=0)
                                            rms = 20 * np.log10(np.sqrt(np.mean(mono**2)) + 1e-10)
                                            peak = 20 * np.log10(np.max(np.abs(mono)) + 1e-10)
                                            
                                            col1, col2, col3 = st.columns(3)
                                            col1.metric("RMS", f"{rms:.1f}dB")
                                            col2.metric("Peak", f"{peak:.1f}dB")
                                            col3.metric("Crest", f"{peak-rms:.1f}dB")
                                            
                                            # 簡易アドバイス
                                            if key == 'vocals' and rms < -25:
                                                st.write("💡 ボーカルが小さめです")
                                            elif key == 'bass' and rms < -20:
                                                st.write("💡 ベースをもう少し上げてもいいかも")
                                else:
                                    st.error(error)
                        
                    finally:
                        os.unlink(tmp_path)
    
    elif menu == "📊 履歴":
        st.markdown("## 📊 解析履歴")
        
        storage = Storage()
        data = storage.load(user['email'])
        
        if not data:
            st.info("まだデータがありません")
            return
        
        st.write(f"**{len(data)}件**")
        
        for d in reversed(data[-10:]):  # 最新10件
            t = datetime.fromisoformat(d['time'])
            with st.expander(f"🎵 {d['name']} ({t.strftime('%m/%d %H:%M')})"):
                r = d['result']
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("RMS", f"{r['rms']:.1f}dB")
                col2.metric("Peak", f"{r['peak']:.1f}dB")
                col3.metric("Crest", f"{r['crest']:.1f}dB")
                col4.metric("Stereo", f"{r['stereo']:.1f}%")


if __name__ == "__main__":
    main()
