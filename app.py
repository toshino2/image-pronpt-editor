import streamlit as st
import yaml
import google.generativeai as genai
import json
import os

# --- ページ設定 ---
st.set_page_config(page_title="AI Banner Director Pro", layout="wide", page_icon="🎨")

# --- 1. 定義：業界・ジャンル別の隠しプロンプト ---
GENRES = {
    "ビジネス・セミナー": "Professional, Trustworthy, Corporate. Clean lines, reliable blue/gray tones.",
    "美容・コスメ": "Elegant, Clean, Aesthetic. Soft lighting, pastels, minimalist layouts.",
    "求人・採用": "Energetic, Friendly, Future-oriented. Emphasize people and growth.",
    "ゲーム・エンタメ": "Vibrant, High-impact, Exciting. Neon effects, dynamic angles, bold typography.",
    "高級・ラグジュアリー": "Prestigious, Sophisticated, Gold/Black theme. Serif fonts, spacious design.",
    "セール・キャンペーン": "Urgent, Catchy, High-contrast. Bright red/yellow, large font sizes."
}

# --- 2. 定義：レイアウトパターンの図解 ---
LAYOUT_PATTERNS = {
    "左右分割 (右被写体)": {"desc": "Split: Subject Right, Text Left", "img": "image/layout_split_right.png"},
    "左右分割 (左被写体)": {"desc": "Split: Subject Left, Text Right", "img": "image/layout_split_left.png"},
    "中央配置": {"desc": "Center: Focused Subject, Wrapped Text", "img": "image/layout_center.png"},
    "ダイナミック（重ね）": {"desc": "Dynamic: Text overlapping subject", "img": "image/layout_overlap.png"}
}

# --- 3. APIキー管理 ---
if "api_key" not in st.session_state:
    st.session_state.api_key = st.query_params.get("key", "")

# --- 4. AI生成ロジック ---
def generate_creative_plan(user_req, genre, layout, key):
    if not key:
        st.error("Gemini API Key が必要です。")
        return None
    
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    genre_hint = GENRES.get(genre, "")
    prompt = f"""
    You are a world-class Ad Director. Create a banner design JSON for Nano_Banana_Pro.
    IMPORTANT: The text layers are the most critical part. Ensure they are catchy and brief.
    
    【Context】
    User Request: {user_req}
    Target Genre: {genre} ({genre_hint})
    Layout Pattern: {layout}

    【Instructions】
    - Descriptions for 'bg' and 'subj' MUST be in detailed English.
    - Headlines (t1, t2, t3) MUST be in Japanese and extremely concise (t1 < 10 chars).
    - Choose 3 matching Hex colors and font styles.

    Return ONLY JSON:
    {{
        "t1": "JP headline", "t2": "JP subline", "t3": "JP cta",
        "theme_val": "Concept", "colors": ["#111", "#222", "#333"], 
        "typo": "Font desc", "bg": "Detailed EN", "subj": "Detailed EN", 
        "t1_s": "85px", "t2_s": "40px", "t3_s": "30px",
        "t1_p": "top_left", "fx": "Text effect"
    }}
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.replace("```json", "").replace("```", "").strip())
    except Exception as e:
        st.error(f"生成エラー: {e}")
        return None

# --- 5. UI構成 ---
st.sidebar.header("🔑 API Setup")
api_input = st.sidebar.text_input("Gemini API Key", value=st.session_state.api_key, type="password")
if api_input: st.session_state.api_key = api_input

st.sidebar.divider()
st.sidebar.subheader("📐 Layout & Genre")
genre_choice = st.sidebar.selectbox("ジャンルを選択", list(GENRES.keys()))
layout_choice = st.sidebar.radio("レイアウトを選択", list(LAYOUT_PATTERNS.keys()))

img_path = LAYOUT_PATTERNS[layout_choice]["img"]
if os.path.exists(img_path): st.sidebar.image(img_path, width='stretch')

# メインエリア
st.title("🎨 AI Creative Director Pro")
user_msg = st.text_area("要望を入力（例：30代女性、美容液、高級感）", height=100)
dims = st.selectbox("バナーサイズ", ["1200x628", "1080x1080", "1920x1080"])

if st.button("🚀 デザイン案を生成", use_container_width=True):
    res = generate_creative_plan(user_msg, genre_choice, LAYOUT_PATTERNS[layout_choice]["desc"], st.session_state.api_key)
    if res: st.session_state.res = res

if "res" in st.session_state:
    r = st.session_state.res
    st.divider()
    
    # YAMLの構造：テキストを最上段に配置
    final_yaml = {
        "text_layers": [
            {"text": r['t1'], "position": r.get('t1_p', 'top_left'), "size": r['t1_s'], "style": r['fx']},
            {"text": r['t2'], "position": "below_main_text", "size": r['t2_s']},
            {"text": r['t3'], "position": "bottom_left", "size": r['t3_s'], "background_box": r['colors'][2]}
        ],
        "style_guidelines": {
            "theme": r['theme_val'],
            "color_palette": r['colors'],
            "typography": r['typo']
        },
        "composition": {
            "background": {"description": r['bg']},
            "main_visual": {"subject": r['subj']}
        },
        "target_model": "Nano_Banana_Pro", # モデル名は最後
        "dimensions": dims
    }
    
    st.subheader("📋 テキスト優先型プロンプト")
    st.code(yaml.dump(final_yaml, allow_unicode=True, sort_keys=False), language="yaml")
    
    with st.expander("🛠️ 内容を編集する"):
        st.json(r)