# --- 4. AI生成ロジック（構造変更版） ---
def generate_creative_plan(user_req, genre, layout, key):
    if not key:
        st.error("Gemini API Key が必要です。")
        return None
    
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    genre_hint = GENRES.get(genre, "")
    prompt = f"""
    You are a world-class Ad Director. Create a banner design JSON.
    IMPORTANT: The text layers are the most critical part. Ensure they are catchy and brief.
    
    【Context】
    User Request: {user_req}
    Target Genre: {genre} ({genre_hint})
    Layout Pattern: {layout}

    【Instructions】
    - Descriptions for 'bg' and 'subject' MUST be in detailed English.
    - Headlines MUST be in Japanese and extremely concise (t1 < 10 chars).
    - Choose 3 Hex colors and optimal font sizes.

    Return ONLY JSON:
    {{
        "t1": "JP headline", "t2": "JP subline", "t3": "JP cta",
        "theme_val": "Concept name", "colors": ["#111", "#222", "#333"], 
        "typo": "Font style desc", "bg": "Detailed EN", "subj": "Detailed EN", 
        "t1_s": "85px", "t2_s": "40px", "t3_s": "30px",
        "t1_p": "top_left", "fx": "Text effect"
    }}
    """
    # ...（中略：実行部分は同じ）...

# --- 5. UI構成（YAML構築部分のみ抜粋） ---
if "res" in st.session_state:
    r = st.session_state.res
    st.subheader("📋 テキスト優先型プロンプト")
    
    # 【変更点】YAMLの順番を入れ替え
    final_yaml = {
        "text_layers": [
            {"text": r['t1'], "position": r['t1_p'], "size": r['t1_s'], "style": r['fx']},
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
        "target_model": "Nano_Banana_Pro", # モデル名は最後に
        "dimensions": dims
    }
    
    yaml_output = yaml.dump(final_yaml, allow_unicode=True, sort_keys=False) # sort_keys=Falseが重要
    st.code(yaml_output, language="yaml")