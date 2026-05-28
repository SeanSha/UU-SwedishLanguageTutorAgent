import os
import json
import random
import re
from html import escape
import gradio as gr
from agent import SwedishSpeakingAgent, OFFLINE_DICT
import config
from tools.vocab_resolver import clean_offline_meaning as resolver_clean_offline_meaning
from tools.vocab_resolver import resolve_vocab

# Global Agent Instance
agent = SwedishSpeakingAgent()
gr.set_static_paths(paths=[config.ASSETS_DIR])

# Modern UI Mappings to resolve friendly names to technical tags
SCENARIO_MAP = {
    "🛒 Food Shop (食品店)": "food_shop",
    "🏫 Family & School (家庭与学校)": "family_school",
    "🏥 Health & Places (健康与场所)": "health_places",
    "🚌 Transport & Travel (交通与出行)": "transport",
    "🏡 Home & Places (住所与生活)": "home_places",
    "👋 Social Introductions (社交与自我介绍)": "social_intro"
}

QUIZ_TYPE_MAP = {
    "🎯 Multiple Choice Quiz (单选题)": "multiple_choice",
    "✍️ Fill-in-the-Blank Exercise (填空题)": "fill_in_the_blank"
}

LANG_MAP = {
    "🇬🇧 English (英文)": "English",
    "🇨🇳 Chinese (中文)": "Chinese"
}


# Custom Premium Glassmorphic Light CSS theme
CUSTOM_CSS = """
body {
    background-color: #f4f6f9;
    color: #1f2937;
    font-family: 'Outfit', 'Inter', sans-serif;
}
.gradio-container {
    background: radial-gradient(circle at top left, #f7f9fc, #ffffff) !important;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
}
/* Force highly readable dark slate text colors for all markdown prose elements */
.prose, .prose p, .prose li, .prose ol {
    color: #374151 !important;
}
.prose h1, .prose h2, .prose h3 {
    color: #1f2937 !important;
}
.prose h4, .prose h5, .prose h6 {
    color: #4f46e5 !important;
}

/* Specific contrast overrides to prevent unreadable text in badges and headers */
.card-header-tag, .card-header-tag span {
    font-weight: 700 !important;
}
.tag-sven, .tag-sven span {
    color: #4338ca !important;
}
.tag-quiz, .tag-quiz span {
    color: #0369a1 !important;
}
.tag-feedback, .tag-feedback span {
    color: #b45309 !important;
}
.stage-lbl-banner, .stage-lbl-banner span {
    color: #ffffff !important;
}
.stage-lbl-banner .stage-badge {
    color: #4f46e5 !important;
    background: #ffffff !important;
}
/* Make blocks title labels readable and deep royal indigo */
.block label span {
    color: #4f46e5 !important;
    font-weight: 600 !important;
}
/* Form inputs and dropdown styling (excluding checkbox and radio to preserve checked indicators) */
.gradio-container input:not([type="radio"]):not([type="checkbox"]), .gradio-container textarea, .gradio-container select {
    background-color: #ffffff !important;
    color: #1f2937 !important;
    border: 1px solid #d1d5db !important;
}
/* Light Glass panel card borders and soft shadow */
.glass-panel {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-radius: 12px !important;
    padding: 16px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
}
.accent-title {
    background: linear-gradient(90deg, #4f46e5, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    text-align: center;
}
.terminal-debug {
    background-color: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    color: #0f172a !important;
    font-family: 'Courier New', Courier, monospace !important;
    border-radius: 8px;
    padding: 12px;
}
.vocab-table {
    border-collapse: collapse;
    width: 100%;
}
.vocab-table th, .vocab-table td {
    border: 1px solid #e5e7eb;
    padding: 8px;
    text-align: left;
}
.vocab-table th {
    background-color: #f3f4f6 !important;
    color: #4f46e5 !important;
}
.vocab-table td {
    color: #4b5563 !important;
}
/* Elegant light-themed hover buttons */
button.secondary {
    background-color: #ffffff !important;
    color: #4f46e5 !important;
    border: 1px solid #4f46e5 !important;
    transition: all 0.2s ease !important;
}
button.secondary:hover {
    background-color: #4f46e5 !important;
    color: #ffffff !important;
    box-shadow: 0 0 8px rgba(79, 70, 229, 0.2) !important;
}
/* Beautiful Clickable Scenario Cards styling */
.scenario-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 12px;
    margin-bottom: 16px;
}
.scenario-card {
    background: #ffffff;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.scenario-card:hover {
    border-color: #4f46e5;
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.08);
}
.scenario-card.active {
    border-color: #4f46e5 !important;
    background-color: rgba(79, 70, 229, 0.03) !important;
    box-shadow: 0 10px 20px -3px rgba(79, 70, 229, 0.12) !important;
    transform: scale(1.03);
}
.scenario-card img {
    width: 100%;
    max-width: 150px;
    aspect-ratio: 1;
    border-radius: 8px;
    object-fit: cover;
    margin-bottom: 10px;
    border: 1px solid rgba(0, 0, 0, 0.05);
}
.scenario-card .card-title {
    font-weight: 700;
    color: #1f2937;
    font-size: 14px;
    margin-bottom: 6px;
}
.scenario-card .card-desc {
    font-size: 11px;
    color: #4b5563;
    line-height: 1.4;
}
#hidden-scenario-input {
    display: none !important;
}
/* Premium Segmented Control for Radio Buttons */
.gradio-container div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 12px !important;
    background: rgba(255, 255, 255, 0.55) !important;
    padding: 6px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.01) !important;
}

.gradio-container div[role="radiogroup"] label {
    flex: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #4b5563 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.01) !important;
}

/* Hover state */
.gradio-container div[role="radiogroup"] label:hover {
    border-color: #4f46e5 !important;
    color: #4f46e5 !important;
    background: rgba(79, 70, 229, 0.02) !important;
    transform: translateY(-1px) !important;
}

/* Selected state (Segmented active control) */
.gradio-container div[role="radiogroup"] label.selected {
    background: linear-gradient(135deg, #4f46e5, #3b82f6) !important;
    border-color: #4f46e5 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
}

/* Hide the default ugly radio circle icon */
.gradio-container div[role="radiogroup"] label input[type="radio"] {
    display: none !important;
}

/* Also color the span inside selected label to white */
.gradio-container div[role="radiogroup"] label.selected span {
    color: #ffffff !important;
}

/* Card containers inside Column B */
.sven-card {
    background: #ffffff !important;
    border: 1.5px solid #e0e7ff !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.03) !important;
    margin-bottom: 16px !important;
}
.quiz-card {
    background: #ffffff !important;
    border: 1.5px solid #e0f2fe !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 4px 6px -1px rgba(6, 182, 212, 0.03) !important;
    margin-bottom: 16px !important;
}
.feedback-card {
    background: #ffffff !important;
    border: 1.5px solid #fef3c7 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.03) !important;
    margin-bottom: 16px !important;
}

/* Beautiful label tags at the top of cards */
.card-header-tag {
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    padding: 4px 10px !important;
    border-radius: 20px !important;
    margin-bottom: 12px !important;
}
.tag-sven {
    background: #e0e7ff !important;
    color: #4338ca !important;
}
.tag-quiz {
    background: #e0f2fe !important;
    color: #0369a1 !important;
}
.tag-feedback {
    background: #fef3c7 !important;
    color: #b45309 !important;
}
"""

def build_stage_lbl_html(stage_num, stage_desc, max_stages=5):
    """Compiles a premium linear-gradient banner indicating the active roleplay turn and progress."""
    return (
        f"<div class='stage-lbl-banner' style='display:flex; justify-content:space-between; align-items:center; "
        f"background:linear-gradient(90deg, #4f46e5, #3b82f6); color:#ffffff !important; "
        f"padding:10px 16px; border-radius:10px; margin-bottom:16px; "
        f"box-shadow:0 4px 12px rgba(79,70,229,0.12);'>"
        f"<span style='font-weight:700; font-size:14px; display:flex; align-items:center; gap:6px; color:#ffffff !important;'>🎮 Roleplay Turn: {stage_desc}</span>"
        f"<span class='stage-badge' style='background:#ffffff !important; color:#4f46e5 !important; font-size:12px; font-weight:800; "
        f"padding:2px 10px; border-radius:20px;'>Turn {stage_num}/{max_stages}</span>"
        f"</div>"
    )
def build_chat_transcript_html(chat_history, lang="English"):
    """
    Renders a compact, scrollable dialogue history transcript inside Column B.
    Sven's prompt is on the left in indigo, user's correct reply is on the right in cyan.
    """
    if not chat_history:
        return (
            "<div style='background:#f9fafb; border:1px dashed #d1d5db; border-radius:8px; "
            "padding:10px; text-align:center; font-size:12.5px; color:#9ca3af;'>"
            "💬 Dialogue Transcript: Starting conversation... (对白实录：开始对话)"
            "</div>"
        )
        
    html = (
        "<div style='background: rgba(249, 250, 251, 0.95); border: 1px solid #e5e7eb; "
        "border-radius: 12px; padding: 10px; max-height: 150px; overflow-y: auto; "
        "box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); display:flex; flex-direction:column; gap:8px; margin-bottom:12px;'>"
    )
    for h in chat_history:
        is_sven = (h["role"] == "assistant")
        bg = "rgba(79, 70, 229, 0.05)" if is_sven else "rgba(6, 182, 212, 0.05)"
        border = "rgba(79, 70, 229, 0.12)" if is_sven else "rgba(6, 182, 212, 0.12)"
        align = "flex-start" if is_sven else "flex-end"
        label_color = "#4338ca" if is_sven else "#0369a1"
        name = "👨‍🏫 Sven" if is_sven else "👤 Du (You)"
        
        translation = h.get("chinese" if lang == "Chinese" else "english", "")
        if not translation and is_sven:
            from agent import SVEN_TRANSLATIONS
            phrase = h["content"]
            if phrase in SVEN_TRANSLATIONS:
                translation = SVEN_TRANSLATIONS[phrase].get(lang, SVEN_TRANSLATIONS[phrase].get("English", ""))
        trans_text = (
            f"<div style='font-size:11px; color:#6b7280; font-weight:normal; margin-top:3px;'>"
            f"{translation}</div>"
            if translation else ""
        )
        mp3_path = agent.tts_avatar_tool.get_cached_tts(h["content"])
        audio_tag = (
            f"<audio id='audio-transcript-{id(h)}' src='/gradio_api/file={mp3_path}' style='display:none;'></audio>"
            if mp3_path else ""
        )
        click_handler = f"onclick=\"document.getElementById('audio-transcript-{id(h)}').play();\"" if mp3_path else ""
        
        html += (
            f"<div {click_handler} style='align-self:{align}; max-width:85%; background:{bg}; "
            f"border:1px solid {border}; border-radius:10px; padding:6px 10px; "
            f"box-shadow: 0 1px 2px rgba(0,0,0,0.01); cursor:pointer;'>"
            f"{audio_tag}"
            f"<div style='font-size:8.5px; font-weight:700; color:{label_color}; text-transform:uppercase; "
            f"letter-spacing:0.05em; margin-bottom:2px;'>{name}</div>"
            f"<div style='font-size:13px; font-weight:600; color:#1f2937;'>{h['content']}{trans_text}</div>"
            f"</div>"
        )
    html += "</div>"
    return html
def update_mode_visibility(mode):
    """Dynamically displays local or online inputs based on selection."""
    if mode == "Local Mode":
        return [
            gr.update(visible=True),  # Local elements
            gr.update(visible=False)  # Online elements
        ]
    else:
        return [
            gr.update(visible=False), # Local elements
            gr.update(visible=True)   # Online elements
        ]

def handle_check_connection(mode, endpoint, local_model, online_key, online_base, online_model):
    """Invokes LLM connection diagnostic ping checks."""
    ok, msg = agent.initialize_provider(
        mode=mode,
        ollama_endpoint=endpoint,
        local_model=local_model,
        online_key=online_key,
        online_base=online_base,
        online_model=online_model
    )
    if ok:
        return f"🟢 Health Check Passed!\n{msg}"
    else:
        return f"🔴 Health Check Failed!\n\n{msg}"

def build_audio_click_markup(text, audio_id, mp3_url=""):
    """
    Returns hidden audio markup plus a click handler.
    Falls back to browser speech synthesis when cached mp3 is unavailable.
    """
    safe_audio_id = escape(str(audio_id), quote=True)
    speech_text = json.dumps(str(text or ""))
    audio_html = f"<audio id='{safe_audio_id}' src='{escape(mp3_url, quote=True)}' style='display:none;'></audio>"
    click_attr = (
        "onclick='var speak=function(){if(\"speechSynthesis\" in window){"
        "var u=new SpeechSynthesisUtterance(" + speech_text + ");"
        "u.lang=\"sv-SE\";window.speechSynthesis.cancel();window.speechSynthesis.speak(u);}};"
        "var a=document.getElementById(\"" + safe_audio_id + "\");"
        "if(a&&a.getAttribute(\"src\")){a.currentTime=0;var p=a.play();"
        "if(p&&p.catch){p.catch(speak);}}else{speak();}'"
    )
    return audio_html, click_attr

def build_study_guide_html(retrieved_log, topic_context=None):
    """
    Builds a lesson-first study guide:
    clickable vocabulary, clickable retrieved examples, then a generated example dialogue.
    """
    if not retrieved_log and not topic_context:
        return "<p>No study guide expressions retrieved yet.</p>"

    def h(text):
        return escape(str(text or ""))

    def collect_examples():
        seen = set()
        items = []

        def add_item(text, english="", chinese="", function="", source="Retrieved"):
            key = (text or "").strip()
            if not key or key in seen:
                return
            seen.add(key)
            items.append({
                "text": key,
                "english": english or "",
                "chinese": chinese or "",
                "function": function or "",
                "source": source or "Retrieved",
            })

        if topic_context:
            for step in topic_context.get("retrieved_sequence") or []:
                for ex in step.get("retrieved_examples") or []:
                    add_item(
                        ex.get("sentence", ""),
                        ex.get("english", ""),
                        ex.get("chinese", ""),
                        step.get("function", ex.get("function", "")),
                        f"Turn {step.get('turn')}",
                    )
            for ex in topic_context.get("ranked_sentences") or []:
                add_item(
                    ex.get("sentence", ""),
                    ex.get("english", ""),
                    ex.get("chinese", ""),
                    ex.get("function", ""),
                    "Sentence bank",
                )

        for item in retrieved_log or []:
            add_item(
                item.get("text", ""),
                item.get("english", ""),
                item.get("chinese", ""),
                item.get("source", ""),
                item.get("source", "Retrieved"),
            )

        return items[:14]

    vocab_items = (topic_context or {}).get("vocabulary") or []
    vocab_html = (
        "<div style='background:#ffffff; border:1px solid #dbeafe; border-radius:8px; padding:12px; margin-bottom:12px;'>"
        "<div style='font-size:13px; color:#1d4ed8; font-weight:800; margin-bottom:8px;'>1. Vocabulary Warm-up / 先学单词</div>"
    )
    if vocab_items:
        vocab_html += "<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;'>"
        for idx, v in enumerate(vocab_items[:18]):
            word = (v.get("word") or "").strip()
            mp3_path = agent.tts_avatar_tool.get_cached_tts(word)
            mp3_url = f"/gradio_api/file={mp3_path}" if mp3_path else ""
            audio_id = f"audio-vocab-{idx}"
            audio_html, click_attr = build_audio_click_markup(word, audio_id, mp3_url)
            vocab_html += (
                f"<div {click_attr} style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:8px; "
                "cursor:pointer;'>"
                f"{audio_html}"
                "<div style='display:flex; justify-content:space-between; align-items:center; gap:6px;'>"
                f"<div style='font-size:15px; color:#0f172a; font-weight:800;'>{h(v.get('word'))}</div>"
                f"<span style='font-size:10px; color:#0f766e; font-weight:800;'>🔊</span>"
                "</div>"
                f"<div style='font-size:12px; color:#475569;'>{h(v.get('english'))}</div>"
                f"<div style='font-size:12px; color:#64748b;'>{h(v.get('chinese'))}</div>"
                "</div>"
            )
        vocab_html += "</div>"
    else:
        vocab_html += "<div style='font-size:12px; color:#64748b;'>No vocabulary retrieved for this topic.</div>"
    vocab_html += "</div>"

    stages = getattr(agent.dialogue_tool, "custom_stages", None) or []
    dialogue_html = (
        "<div style='background:#f0fdfa; border:1px solid #99f6e4; border-radius:8px; padding:12px;'>"
        "<div style='font-size:13px; color:#0f766e; font-weight:800; margin-bottom:6px;'>3. Example Dialogue / 按检索内容生成的对话例子</div>"
    )
    if stages:
        for st in stages[:6]:
            dialogue_html += (
                "<div style='border-bottom:1px solid #e0f2fe; padding:6px 0;'>"
                f"<div style='font-size:11px; color:#0369a1; font-weight:800;'>Stage {h(st.get('stage'))}: {h(st.get('desc'))}</div>"
                f"<div style='font-size:13px; color:#1f2937; margin-top:3px;'><b>Sven:</b> {h(st.get('sven_phrase'))}</div>"
                f"<div style='font-size:12px; color:#64748b;'>{h(st.get('sven_english'))}</div>"
                f"<div style='font-size:13px; color:#1f2937; margin-top:3px;'><b>You:</b> {h(st.get('target_phrase'))}</div>"
                f"<div style='font-size:12px; color:#64748b;'>{h(st.get('target_english'))}</div>"
                "</div>"
            )
    else:
        dialogue_html += "<div style='font-size:12px; color:#64748b;'>Dialogue example appears after the lesson starts.</div>"
    dialogue_html += "</div>"

    phrase_cards = ""
    for idx, item in enumerate(collect_examples()):
        mp3_path = agent.tts_avatar_tool.get_cached_tts(item["text"])
        mp3_url = f"/gradio_api/file={mp3_path}" if mp3_path else ""
        audio_id = f"audio-guide-{idx}"
        audio_html, click_attr = build_audio_click_markup(item["text"], audio_id, mp3_url)
        listen_badge = "Listen" if mp3_url else "Browser voice"
        phrase_cards += (
            f"<div {click_attr} style='background:#ffffff; border:1px solid #e5e7eb; border-radius:8px; padding:12px; "
            "cursor:pointer; transition:all 0.2s ease; box-shadow:0 1px 3px rgba(0,0,0,0.02);' "
            f"onmouseover=\"this.style.borderColor='#4f46e5'; this.style.boxShadow='0 4px 12px rgba(79,70,229,0.08)';\" "
            f"onmouseout=\"this.style.borderColor='#e5e7eb'; this.style.boxShadow='0 1px 3px rgba(0,0,0,0.02)';\">"
            f"{audio_html}"
            "<div style='display:flex; justify-content:space-between; align-items:center; gap:8px;'>"
            f"<span style='background:#4f46e5; color:#ffffff; font-size:10px; font-weight:bold; padding:2px 6px; border-radius:4px;'>{h(item.get('source'))}</span>"
            f"<span style='background:#10b981; color:#ffffff; font-size:10px; font-weight:bold; padding:2px 6px; border-radius:4px;'>🔊 {listen_badge}</span>"
            "</div>"
            f"<div style='font-size:11px; color:#64748b; margin-top:7px;'><code>{h(item.get('function'))}</code></div>"
            f"<div style='font-size:15px; font-weight:800; color:#1f2937; margin:5px 0 4px 0;'>{h(item['text'])}</div>"
            f"<div style='font-size:12px; color:#4b5563;'>EN: {h(item['english'])}</div>"
            f"<div style='font-size:12px; color:#6b7280;'>中文: {h(item['chinese'])}</div>"
            "</div>"
        )

    html = (
        "<div style='background:rgba(79,70,229,0.035); border:1px solid rgba(79,70,229,0.12); "
        "border-radius:10px; padding:16px; margin-bottom:8px;'>"
        "<h3 style='margin:0 0 8px 0; color:#4f46e5; display:flex; align-items:center; gap:6px;'>📖 Lesson Study Guide</h3>"
        "<p style='margin:0 0 12px 0; font-size:13px; color:#64748b;'>"
        "Start with clickable vocabulary, listen to retrieved examples, then study the example dialogue.</p>"
        f"{vocab_html}"
        "<div style='background:#ffffff; border:1px solid #e5e7eb; border-radius:8px; padding:12px;'>"
        "<div style='font-size:13px; color:#334155; font-weight:800; margin-bottom:8px;'>"
        "2. Retrieved Sentence Examples / 可点击听音频的检索例句</div>"
    )
    if phrase_cards:
        html += (
            "<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:12px;'>"
            f"{phrase_cards}</div>"
        )
    else:
        html += "<div style='font-size:12px; color:#64748b;'>No sentence examples retrieved yet.</div>"

    html += f"</div><div style='margin-top:12px;'>{dialogue_html}</div></div>"
    return html

def build_retrieved_table(retrieved_log):
    """Compiles HTML overview of retrieved context phrases for the debug drawer."""
    if not retrieved_log:
        return "<p>No examples retrieved yet.</p>"
        
    html = "<table class='vocab-table'><thead><tr><th>Swedish</th><th>English</th><th>Base Match</th><th>Mistake Boost</th><th>Final Rank Score</th></tr></thead><tbody>"
    for r in retrieved_log:
        boost_str = f"<span style='color:#ff3333;'>+{r['boost']:.2f}</span>" if r['boost'] > 0 else "0.0"
        html += (
            f"<tr><td><b>{r['text']}</b></td>"
            f"<td>{r['english']}</td>"
            f"<td>{r['base_score']:.3f}</td>"
            f"<td>{boost_str}</td>"
            f"<td><b>{r['final_score']:.3f}</b></td></tr>"
        )
    html += "</tbody></table>"
    return html

def build_progress_vault_html(memory_summary):
    """
    Renders a learner-facing memory board: what the agent remembers,
    what it will recycle next, and compact progress by topic.
    """
    if not memory_summary:
        return (
            "<div style='background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:16px;'>"
            "<h3 style='margin:0 0 8px 0; color:#1f2937;'>Memory Review Coach</h3>"
            "<p style='margin:0; color:#64748b; font-size:13px;'>No practice memory yet. After a few answers, this panel will show what the tutor should review with you next.</p>"
            "</div>"
        )

    def scenario_title(sc):
        for label, key in SCENARIO_MAP.items():
            if key == sc:
                plain = label.split("(", 1)[0].strip()
                return plain
        return sc.replace("_", " ").title()

    review_queue = []
    total_correct = 0
    total_mistakes = 0
    active_topics = 0

    for sc, data in memory_summary.items():
        sc_mem = agent.memory_tool.memory_data.get(sc, {})
        wrong_words = sc_mem.get("wrong_words", {})
        total_correct += sc_mem.get("correct_count", data.get("successes", 0))
        total_mistakes += sc_mem.get("mistake_count", data.get("mistakes", 0))
        if wrong_words:
            active_topics += 1
        for word, score in wrong_words.items():
            if score > 0:
                review_queue.append({
                    "word": word,
                    "score": score,
                    "scenario": sc,
                    "meaning": vocab_meaning(word),
                })

    review_queue.sort(key=lambda item: item["score"], reverse=True)
    active_words = len(review_queue)
    total_answers = total_correct + total_mistakes
    overall_acc = round((total_correct / total_answers) * 100, 1) if total_answers else 100

    html = (
        "<div style='background:rgba(255,255,255,0.96); border:1px solid #e5e7eb; "
        "border-radius:10px; padding:16px; box-shadow:0 4px 12px rgba(0,0,0,0.02);'>"
        "<div style='display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap;'>"
        "<div>"
        "<h3 style='margin:0 0 6px 0; color:#1f2937;'>Memory Review Coach / 记忆复习教练</h3>"
        "<p style='margin:0; color:#64748b; font-size:13px;'>"
        "The tutor remembers words that need review, then brings them back in retrieval, examples, and quiz choices.</p>"
        "</div>"
        f"<span style='background:#ecfeff; color:#0e7490; border:1px solid #a5f3fc; border-radius:999px; "
        f"font-size:12px; font-weight:800; padding:5px 10px;'>Overall {overall_acc}%</span>"
        "</div>"
        "<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(145px, 1fr)); gap:10px; margin-top:14px;'>"
        f"<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px;'>"
        f"<div style='font-size:11px; color:#64748b; font-weight:800;'>Practice answers</div>"
        f"<div style='font-size:22px; color:#0f172a; font-weight:900;'>{total_answers}</div></div>"
        f"<div style='background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:10px;'>"
        f"<div style='font-size:11px; color:#15803d; font-weight:800;'>Correct memory</div>"
        f"<div style='font-size:22px; color:#166534; font-weight:900;'>{total_correct}</div></div>"
        f"<div style='background:#fff7ed; border:1px solid #fed7aa; border-radius:8px; padding:10px;'>"
        f"<div style='font-size:11px; color:#c2410c; font-weight:800;'>Review queue</div>"
        f"<div style='font-size:22px; color:#9a3412; font-weight:900;'>{active_words}</div></div>"
        f"<div style='background:#eef2ff; border:1px solid #c7d2fe; border-radius:8px; padding:10px;'>"
        f"<div style='font-size:11px; color:#4338ca; font-weight:800;'>Topics with memory</div>"
        f"<div style='font-size:22px; color:#3730a3; font-weight:900;'>{active_topics}</div></div>"
        "</div>"
    )

    html += (
        "<div style='margin-top:14px; background:#ffffff; border:1px solid #e5e7eb; border-radius:8px; padding:12px;'>"
        "<div style='font-size:13px; color:#334155; font-weight:900; margin-bottom:8px;'>Next Review Queue / 下一轮优先复习</div>"
    )
    if review_queue:
        html += "<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(190px, 1fr)); gap:8px;'>"
        for idx, item in enumerate(review_queue[:8]):
            word = item["word"]
            score = item["score"]
            priority = "Review now" if score >= 4 else "Warm-up soon"
            mp3_path = agent.tts_avatar_tool.get_cached_tts(word)
            mp3_url = f"/gradio_api/file={mp3_path}" if mp3_path else ""
            audio_id = f"audio-memory-{idx}"
            click_attr = f"onclick=\"document.getElementById('{audio_id}').play();\"" if mp3_url else ""
            html += (
                f"<div {click_attr} style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px; "
                f"cursor:{'pointer' if mp3_url else 'default'};'>"
                f"<audio id='{audio_id}' src='{mp3_url}' style='display:none;'></audio>"
                "<div style='display:flex; justify-content:space-between; align-items:center; gap:8px;'>"
                f"<b style='font-size:16px; color:#0f172a;'>{escape(word)}</b>"
                f"<span style='font-size:10px; color:#0f766e; font-weight:900;'>🔊 {priority}</span>"
                "</div>"
                f"<div style='font-size:12px; color:#475569; margin-top:3px;'>{escape(item['meaning'])}</div>"
                f"<div style='font-size:11px; color:#64748b; margin-top:5px;'>{escape(scenario_title(item['scenario']))} · review weight {score}</div>"
                "</div>"
            )
        html += "</div>"
    else:
        html += (
            "<div style='background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:10px; "
            "color:#166534; font-size:13px;'>No active review words right now. The tutor will start building this queue after new mistakes.</div>"
        )
    html += "</div>"

    html += (
        "<div style='margin-top:12px; display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:10px;'>"
    )
    for sc, data in memory_summary.items():
        sc_mem = agent.memory_tool.memory_data.get(sc, {})
        wrong_words = sc_mem.get("wrong_words", {})
        mistakes = sc_mem.get("mistake_count", data.get("mistakes", 0))
        correct = sc_mem.get("correct_count", data.get("successes", 0))
        attempts = mistakes + correct
        acc = round((correct / attempts) * 100, 1) if attempts else 100
        html += (
            "<div style='background:#ffffff; border:1px solid #edf2f7; border-radius:8px; padding:10px;'>"
            f"<div style='display:flex; justify-content:space-between; gap:8px; align-items:center;'>"
            f"<b style='color:#1f2937; font-size:13px;'>{escape(scenario_title(sc))}</b>"
            f"<span style='background:#f1f5f9; color:#475569; font-size:11px; font-weight:800; padding:2px 7px; border-radius:999px;'>{acc}%</span>"
            "</div>"
            f"<div style='font-size:11px; color:#64748b; margin-top:6px;'>{correct} correct · {len(wrong_words)} review words</div>"
        )
        if wrong_words:
            chips = sorted(wrong_words.items(), key=lambda item: item[1], reverse=True)[:4]
            html += "<div style='display:flex; gap:5px; flex-wrap:wrap; margin-top:8px;'>"
            for word, score in chips:
                html += (
                    f"<span style='background:#fff7ed; color:#9a3412; border:1px solid #fed7aa; "
                    f"border-radius:999px; font-size:11px; padding:2px 7px;'>{escape(word)} · {score}</span>"
                )
            html += "</div>"
        else:
            html += "<div style='font-size:11px; color:#059669; margin-top:8px;'>Clear for now</div>"
        html += "</div>"
    html += "</div></div>"
    return html

def scenario_title(sc):
    """Returns the friendly learner-facing topic label for a scenario key."""
    for label, key in SCENARIO_MAP.items():
        if key == sc:
            return label.split("(", 1)[0].strip()
    return sc.replace("_", " ").title()

def find_vocab_item(word):
    """Finds the structured vocabulary record for a Swedish word."""
    return resolve_vocab(word, getattr(agent, "vocab_items", []), OFFLINE_DICT).get("item") or {}

def clean_offline_meaning(word):
    """Creates a compact option label from the offline dictionary fallback."""
    resolved = resolve_vocab(word, getattr(agent, "vocab_items", []), OFFLINE_DICT)
    return resolved.get("english") or resolver_clean_offline_meaning(OFFLINE_DICT.get((word or "").strip().lower(), "")) or "vocabulary word"

def vocab_meaning(word):
    resolved = resolve_vocab(word, getattr(agent, "vocab_items", []), OFFLINE_DICT)
    return resolved.get("english") or "vocabulary word"

def vocab_chinese(word):
    resolved = resolve_vocab(word, getattr(agent, "vocab_items", []), OFFLINE_DICT)
    return resolved.get("chinese") or ""

def vocab_example(word):
    resolved = resolve_vocab(word, getattr(agent, "vocab_items", []), OFFLINE_DICT)
    return resolved.get("example") or ""

def build_memory_review_items(limit=12):
    """
    Converts memory struggle words into interactive review cards.
    The queue is sorted by review weight so the most urgent words appear first.
    """
    queue = []
    for sc in config.SCENARIOS:
        sc_mem = agent.memory_tool.memory_data.get(sc, {})
        for word, score in (sc_mem.get("wrong_words", {}) or {}).items():
            if score <= 0:
                continue
            answer = vocab_meaning(word)
            queue.append({
                "word": word,
                "scenario": sc,
                "score": score,
                "answer": answer,
                "chinese": vocab_chinese(word),
                "example": vocab_example(word),
            })

    queue.sort(key=lambda item: item["score"], reverse=True)

    all_meanings = []
    for item in getattr(agent, "vocab_items", []) or []:
        meaning = (item.get("english") or "").strip()
        if meaning and meaning.lower() not in [m.lower() for m in all_meanings]:
            all_meanings.append(meaning)
    if not all_meanings:
        all_meanings = [clean_offline_meaning(w) for w in OFFLINE_DICT.keys()]

    cards = []
    for item in queue[:limit]:
        answer = item["answer"]
        distractors = [m for m in all_meanings if m and m.lower() != answer.lower()]
        rng = random.Random(f"{item['scenario']}::{item['word']}::{item['score']}")
        rng.shuffle(distractors)
        options = [answer] + distractors[:3]
        rng.shuffle(options)
        item["options"] = options
        cards.append(item)
    return cards

def render_memory_review_card(review_items, review_index):
    """Returns HTML, option updates, and next-button state for a review card."""
    if not review_items:
        empty_html = (
            "<div style='background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:22px; text-align:center;'>"
            "<h2 style='margin:0 0 8px 0; color:#1f2937;'>Memory Review Quiz</h2>"
            "<p style='margin:0; color:#64748b;'>No active review words right now. Answer a few lesson questions first and missed words will appear here.</p>"
            "</div>"
        )
        hidden_buttons = [gr.update(value="", visible=False, interactive=False) for _ in range(4)]
        return empty_html, hidden_buttons, gr.update(value="No cards yet", interactive=False)

    if review_index >= len(review_items):
        done_html = (
            "<div style='background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:22px; text-align:center;'>"
            "<h2 style='margin:0 0 8px 0; color:#166534;'>Review Round Complete</h2>"
            "<p style='margin:0; color:#166534;'>Nice work. The memory queue has been updated based on your answers.</p>"
            "</div>"
        )
        hidden_buttons = [gr.update(value="", visible=False, interactive=False) for _ in range(4)]
        return done_html, hidden_buttons, gr.update(value="Finished", interactive=False)

    item = review_items[review_index]
    word = item["word"]
    item["answer"] = vocab_meaning(word)
    item["chinese"] = vocab_chinese(word)
    item["example"] = vocab_example(word)
    current_options = [
        opt for opt in (item.get("options") or [])
        if opt and opt.strip().lower() not in {"vocabulary word", item["answer"].strip().lower()}
    ]
    existing_option_values = [opt.strip().lower() for opt in (item.get("options") or [])]
    needs_option_repair = (
        item["answer"].strip().lower() not in existing_option_values
        or "vocabulary word" in existing_option_values
    )
    if needs_option_repair:
        all_meanings = []
        for vocab in getattr(agent, "vocab_items", []) or []:
            meaning = (vocab.get("english") or "").strip()
            if meaning and meaning.lower() != item["answer"].strip().lower() and meaning.lower() not in [m.lower() for m in all_meanings]:
                all_meanings.append(meaning)
        rng = random.Random(f"repair::{item['scenario']}::{word}::{item['score']}")
        rng.shuffle(all_meanings)
        current_options = (current_options + all_meanings)[:3]
        repaired_options = [item["answer"]] + current_options
        rng.shuffle(repaired_options)
        item["options"] = repaired_options
    mp3_path = agent.tts_avatar_tool.get_cached_tts(word)
    mp3_url = f"/file={mp3_path}" if mp3_path else ""
    audio_html, click_attr = build_audio_click_markup(word, f"audio-review-card-{review_index}", mp3_url)
    example_html = ""
    if item.get("example"):
        example_html = (
            f"<div style='margin-top:10px; font-size:13px; color:#475569;'>"
            f"Example: <b>{escape(item['example'])}</b></div>"
        )

    card_html = (
        "<div style='background:#ffffff; border:1px solid #dbeafe; border-radius:10px; padding:18px;'>"
        "<div style='display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;'>"
        "<div>"
        "<div style='font-size:12px; color:#2563eb; font-weight:900;'>Memory Review Quiz / 错词强化复习</div>"
        f"<h2 style='margin:5px 0 0 0; color:#0f172a; font-size:34px;'>{escape(word)}</h2>"
        "</div>"
        f"<span style='background:#fff7ed; color:#9a3412; border:1px solid #fed7aa; border-radius:999px; "
        f"font-size:12px; font-weight:900; padding:5px 10px;'>Card {review_index + 1}/{len(review_items)} · weight {item['score']}</span>"
        "</div>"
        f"{audio_html}"
        f"<button {click_attr} style='margin-top:12px; background:#10b981; color:#ffffff; border:0; border-radius:8px; "
        f"padding:8px 12px; font-size:13px; font-weight:900; cursor:pointer;'>🔊 Click to hear Swedish</button>"
        f"<p style='margin:12px 0 0 0; color:#475569;'>Choose the meaning. Topic: <b>{escape(scenario_title(item['scenario']))}</b></p>"
        f"{example_html}"
        "</div>"
    )

    option_updates = [
        gr.update(value=opt, visible=True, interactive=True, variant="secondary")
        for opt in item.get("options", [])
    ]
    while len(option_updates) < 4:
        option_updates.append(gr.update(value="", visible=False, interactive=False))

    return card_html, option_updates, gr.update(value="Next Card", interactive=False)

def handle_open_memory_review():
    review_items = build_memory_review_items()
    card_html, option_updates, next_update = render_memory_review_card(review_items, 0)
    return [
        gr.update(visible=False),  # setup_panel
        gr.update(visible=False),  # practice_panel
        gr.update(visible=False),  # congrats_panel
        gr.update(visible=True),   # memory_review_panel
        review_items,
        0,
        card_html,
        option_updates[0], option_updates[1], option_updates[2], option_updates[3],
        "",
        next_update
    ]

def handle_memory_review_answer(choice, review_items, review_index):
    if not review_items or review_index >= len(review_items):
        return [
            gr.update(interactive=False), gr.update(interactive=False),
            gr.update(interactive=False), gr.update(interactive=False),
            "No active review card.",
            gr.update(interactive=False)
        ]

    item = review_items[review_index]
    correct_answer = vocab_meaning(item["word"])
    chinese = vocab_chinese(item["word"])
    is_correct = (choice or "").strip().lower() == correct_answer.strip().lower()
    if is_correct:
        agent.memory_tool.record_success(item["scenario"], item["word"])
        feedback = (
            f"✅ Correct. **{item['word']}** means **{correct_answer}**"
            + (f" / {chinese}." if chinese else ".")
        )
    else:
        agent.memory_tool.record_mistake(item["scenario"], item["word"], "memory_review")
        feedback = (
            f"🔁 Review again. **{item['word']}** means **{correct_answer}**"
            + (f" / {chinese}." if chinese else ".")
        )

    disabled_options = []
    for opt in item.get("options", []):
        variant = "primary" if opt.strip().lower() == correct_answer.strip().lower() else "secondary"
        disabled_options.append(gr.update(value=opt, visible=True, interactive=False, variant=variant))
    while len(disabled_options) < 4:
        disabled_options.append(gr.update(value="", visible=False, interactive=False))

    return [
        disabled_options[0], disabled_options[1], disabled_options[2], disabled_options[3],
        feedback,
        gr.update(value="Next Card", interactive=True)
    ]

def handle_next_memory_review_card(review_items, review_index):
    next_index = review_index + 1
    card_html, option_updates, next_update = render_memory_review_card(review_items, next_index)
    return [
        next_index,
        card_html,
        option_updates[0], option_updates[1], option_updates[2], option_updates[3],
        "",
        next_update
    ]

def handle_restart_memory_review():
    review_items = build_memory_review_items()
    card_html, option_updates, next_update = render_memory_review_card(review_items, 0)
    return [
        review_items,
        0,
        card_html,
        option_updates[0], option_updates[1], option_updates[2], option_updates[3],
        "",
        next_update
    ]

def handle_back_to_practice_from_review():
    return [
        gr.update(visible=False),  # setup_panel
        gr.update(visible=True),   # practice_panel
        gr.update(visible=False),  # congrats_panel
        gr.update(visible=False),  # memory_review_panel
        build_progress_vault_html(agent.memory_tool.get_summary())
    ]

def handle_start_agent(mode, endpoint, local_model, online_key, online_base, online_model, scenario, quiz_type, lang):
    """Initializes session settings and launches practice dialogue."""
    # Resolve friendly UI names to technical keys
    scenario = SCENARIO_MAP.get(scenario, scenario)
    quiz_type = QUIZ_TYPE_MAP.get(quiz_type, quiz_type)
    lang = LANG_MAP.get(lang, lang)
    
    ok, msg = agent.initialize_provider(
        mode=mode,
        ollama_endpoint=endpoint,
        local_model=local_model,
        online_key=online_key,
        online_base=online_base,
        online_model=online_model
    )
    
    state = agent.start_practice(
        scenario_label=scenario,
        quiz_type=quiz_type,
        lang=lang
    )
    
    avatar_emoji = agent.tts_avatar_tool.get_avatar_emoji("speaking")
    avatar_img = agent.tts_avatar_tool.get_avatar_image("speaking")
    
    study_guide_html = build_study_guide_html(agent.retrieved_examples_log, agent.topic_context)
    memory_html = build_progress_vault_html(agent.memory_tool.get_summary())
    grader_ir_html = build_retrieved_table(agent.retrieved_examples_log)
    thought_trace = "\n".join(agent.thought_logs)

    # Sven's spoken sentence and direct translation inside Sven's card
    spoken_sv_html = f"<div style='background:#ffffff; border-left:4px solid #4f46e5; border-radius:4px; padding:12px; margin-bottom:8px;'><h2 style='color:#1f2937; margin:0 0 4px 0; font-size:24px; font-weight:800;'>{state['avatar_sentence']}</h2><span style='color:#4b5563; font-size:14px; font-style:italic;'>Translation: {state['translation']}</span></div>"
    
    # Compile active dialogue transcript scrolling logs
    transcript_html = build_chat_transcript_html(agent.chat_history, lang)

    # Vocabulary Options explains (Looked up instantly in 0 ms!)
    vocab_exps_html = f"<div style='background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:10px;'><span style='color:#1d4ed8; font-size:13px;'>💡 <b>Vocab Help:</b> {state['vocab_hints']}</span></div>"

    # Build options buttons updates
    opt_updates = []
    for i in range(4):
        if quiz_type == "multiple_choice" and i < len(state["options"]):
            opt_updates.append(gr.update(value=state["options"][i], visible=True))
        else:
            opt_updates.append(gr.update(value="", visible=False))

    stage_lbl_html = build_stage_lbl_html(state['stage_num'], state['stage_desc'], agent.dialogue_tool.max_stages)
    status_msg = "Ready! Tap the options below or fill in the blank to reply."
    if agent.selected_plan_info:
        status_msg += f" ({agent.selected_plan_info})"

    return [
        gr.update(visible=False), # Hide Setup tab
        gr.update(visible=True),  # Show Practice tab
        # Main updates
        spoken_sv_html,
        transcript_html,
        state["quiz_sentence"],
        avatar_emoji,
        avatar_img if avatar_img else None,
        # Options
        opt_updates[0], opt_updates[1], opt_updates[2], opt_updates[3],
        # Fill in blank text box visibility
        gr.update(visible=(quiz_type == "fill_in_the_blank")),
        # Feedback resets
        "",
        state["audio_path"] if state["audio_path"] else None,
        # Dialogue stage indicator
        stage_lbl_html,
        # Visual Cards
        thought_trace,
        study_guide_html,
        memory_html,
        grader_ir_html,
        vocab_exps_html,
        # Hide continue controls, show quiz area on start
        gr.update(visible=(quiz_type == "multiple_choice")),  # options_row
        gr.update(visible=True),  # next_turn_panel stays mounted; buttons are reset below
        gr.update(value="Answer this turn first", visible=True, interactive=False), # continue_btn
        gr.update(value="Try This Turn Again", visible=True, interactive=False), # retry_btn
        gr.update(value="Skip & Continue", visible=True, interactive=False), # skip_btn
        status_msg
    ]

def handle_submit_answer(user_input, quiz_type, lang):
    """
    Validates user answer, logs metrics in memory, updates visual avatar expressions,
    locks options/inputs to allow study time on success, and keeps inputs active on incorrect answers.
    """
    # Resolve friendly UI names to technical keys
    quiz_type = QUIZ_TYPE_MAP.get(quiz_type, quiz_type)
    lang = LANG_MAP.get(lang, lang)
    
    if not user_input or user_input.strip() == "":
        return [gr.update()] * 23 + ["⚠️ Please select or type an answer first!"]

    res = agent.process_answer(user_input, lang=lang)
    
    avatar_emoji = agent.tts_avatar_tool.get_avatar_emoji(res["avatar_state"])
    avatar_img = agent.tts_avatar_tool.get_avatar_image(res["avatar_state"])
    
    # Refresh stats & debug tables
    study_guide_html = build_study_guide_html(agent.retrieved_examples_log, agent.topic_context)
    memory_html = build_progress_vault_html(agent.memory_tool.get_summary())
    grader_ir_html = build_retrieved_table(agent.retrieved_examples_log)
    thought_trace = "\n".join(agent.thought_logs)

    # Sven's spoken sentence and direct translation inside Sven's card
    spoken_sv_html = f"<div style='background:#ffffff; border-left:4px solid #4f46e5; border-radius:4px; padding:12px; margin-bottom:8px;'><h2 style='color:#1f2937; margin:0 0 4px 0; font-size:24px; font-weight:800;'>{res['avatar_sentence']}</h2><span style='color:#4b5563; font-size:14px; font-style:italic;'>Translation: {res['translation']}</span></div>"
    
    # Compile active dialogue transcript scrolling logs
    transcript_html = build_chat_transcript_html(agent.chat_history, lang)

    # Vocabulary Options explains (Looked up instantly in 0 ms!)
    vocab_exps_html = f"<div style='background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:10px;'><span style='color:#1d4ed8; font-size:13px;'>💡 <b>Vocab Help:</b> {res['vocab_hints']}</span></div>"

    stage_lbl_html = build_stage_lbl_html(res['stage_num'], res['stage_desc'], agent.dialogue_tool.max_stages)

    # Auto-advance on correct answer (unless already at final turn).
    if False and res["is_correct"] and not res["completed"]:
        state = agent.load_next_dialogue_turn(quiz_type=quiz_type, lang=lang)

        avatar_emoji = agent.tts_avatar_tool.get_avatar_emoji("speaking")
        avatar_img = agent.tts_avatar_tool.get_avatar_image("speaking")

        study_guide_html = build_study_guide_html(agent.retrieved_examples_log, agent.topic_context)
        memory_html = build_progress_vault_html(agent.memory_tool.get_summary())
        grader_ir_html = build_retrieved_table(agent.retrieved_examples_log)
        thought_trace = "\n".join(agent.thought_logs)

        spoken_sv_html = (
            "<div style='background:#ffffff; border-left:4px solid #4f46e5; border-radius:4px; padding:12px; margin-bottom:8px;'>"
            f"<h2 style='color:#1f2937; margin:0 0 4px 0; font-size:24px; font-weight:800;'>{state['avatar_sentence']}</h2>"
            f"<span style='color:#4b5563; font-size:14px; font-style:italic;'>Translation: {state['translation']}</span></div>"
        )
        transcript_html = build_chat_transcript_html(agent.chat_history, lang)
        vocab_exps_html = (
            "<div style='background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:10px;'>"
            f"<span style='color:#1d4ed8; font-size:13px;'>💡 <b>Vocab Help:</b> {state['vocab_hints']}</span></div>"
        )

        opt_updates = []
        for i in range(4):
            if quiz_type == "multiple_choice" and i < len(state["options"]):
                opt_updates.append(gr.update(value=state["options"][i], visible=True))
            else:
                opt_updates.append(gr.update(value="", visible=False))

        status_msg = "Bra! Correct. Auto-advanced to the next turn."
        if agent.selected_plan_info:
            status_msg += f" ({agent.selected_plan_info})"

        return [
            state["quiz_sentence"],
            avatar_emoji,
            avatar_img if avatar_img else None,
            opt_updates[0], opt_updates[1], opt_updates[2], opt_updates[3],
            res["feedback_text"],
            state["audio_path"] if state["audio_path"] else None,
            build_stage_lbl_html(state['stage_num'], state['stage_desc'], agent.dialogue_tool.max_stages),
            thought_trace,
            study_guide_html,
            memory_html,
            grader_ir_html,
            vocab_exps_html,
            spoken_sv_html,
            transcript_html,
            gr.update(visible=(quiz_type == "multiple_choice")),
            gr.update(visible=(quiz_type == "fill_in_the_blank")),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            status_msg
        ]

    # Set up review controls panel
    if res["is_correct"]:
        # Correct: Show 'Continue' button (If finished, changes text in handle_load_next_turn)
        continue_text = "🎉 Complete Scenario / 完成场景" if res["completed"] else "➡️ Continue to Next Turn / 继续下一轮"
        continue_btn_update = gr.update(value=continue_text, visible=True, interactive=True)
        retry_btn_update = gr.update(value="Try This Turn Again", visible=True, interactive=False)
        skip_btn_update = gr.update(value="Skip & Continue", visible=True, interactive=False)
        status_msg = "Bra! (Correct!) Sven is happy. Study this turn, then click 'Continue'."
        
        # Hide options during review
        opt_updates = [gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)]
        
        # Hide standard inputs to prevent duplicate submission
        options_row_update = gr.update(visible=False)
        fill_blank_column_update = gr.update(visible=False)
        next_turn_panel_update = gr.update(visible=True)
    else:
        # Incorrect: always provide explicit next-step controls to avoid dead-end UX.
        continue_btn_update = gr.update(value="Answer correctly or use Skip", visible=True, interactive=False)
        retry_btn_update = gr.update(value="🔄 Try This Turn Again", visible=True, interactive=True)
        skip_btn_update = gr.update(value="➡️ Skip & Continue", visible=True, interactive=True)
        status_msg = "Oj! (Incorrect). You can retry this turn, or click 'Skip & Continue' to move on."
        
        # Hide standard inputs while showing recovery actions.
        opt_updates = [gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)]
        options_row_update = gr.update(visible=False)
        fill_blank_column_update = gr.update(visible=False)
        next_turn_panel_update = gr.update(visible=True)

    if agent.selected_plan_info:
        status_msg += f" ({agent.selected_plan_info})"

    return [
        res["quiz_sentence"],
        avatar_emoji,
        avatar_img if avatar_img else None,
        # Option buttons updates
        opt_updates[0], opt_updates[1], opt_updates[2], opt_updates[3],
        # Feedback & Audio
        res["feedback_text"],
        res["audio_path"] if res["audio_path"] else None,
        stage_lbl_html,
        thought_trace,
        study_guide_html,
        memory_html,
        grader_ir_html,
        vocab_exps_html,
        spoken_sv_html,
        transcript_html,
        # Quiz panel row visibilities
        options_row_update,
        fill_blank_column_update,
        # Next turn buttons row visibilities
        next_turn_panel_update,
        continue_btn_update,
        retry_btn_update,
        skip_btn_update,
        status_msg
    ]

def handle_load_next_turn(quiz_type, lang):
    """
    Executes actual turn progression when student clicks '➡️ Continue to Next Turn' / '➡️ Skip & Continue'.
    Fetches next intent, compiles Swedish expressions, and reveals congrats_panel on completion!
    """
    # Resolve friendly UI names to technical keys
    quiz_type = QUIZ_TYPE_MAP.get(quiz_type, quiz_type)
    lang = LANG_MAP.get(lang, lang)
    
    if agent.dialogue_tool.is_completed():
        completion_html = (
            "<div style='background:#ecfdf5; border-left:4px solid #10b981; border-radius:6px; "
            "padding:16px; margin-bottom:8px;'>"
            "<h2 style='color:#065f46; margin:0 0 6px 0; font-size:24px; font-weight:800;'>"
            "Bra jobbat! Scenario complete.</h2>"
            "<span style='color:#047857; font-size:14px;'>You finished this full Swedish dialogue flow.</span>"
            "</div>"
        )
        transcript_html = build_chat_transcript_html(agent.chat_history, lang)
        thought_trace = "\n".join(agent.thought_logs)
        memory_html = build_progress_vault_html(agent.memory_tool.get_summary())
        stage_done_html = (
            "<div class='stage-lbl-banner' style='display:flex; justify-content:space-between; align-items:center; "
            "background:linear-gradient(90deg, #059669, #10b981); color:#ffffff !important; "
            "padding:10px 16px; border-radius:10px; margin-bottom:16px;'>"
            "<span style='font-weight:700; font-size:14px; color:#ffffff !important;'>Scenario Complete</span>"
            "<span class='stage-badge' style='background:#ffffff !important; color:#047857 !important; "
            "font-size:12px; font-weight:800; padding:2px 10px; border-radius:20px;'>Done</span>"
            "</div>"
        )
        return [
            gr.update(visible=False), # setup_panel (1)
            gr.update(visible=True),  # practice_panel (2)
            gr.update(visible=False), # congrats_panel (3)
            completion_html,          # avatar_sv_sentence (4)
            transcript_html,          # dialogue_transcript_card (5)
            "Scenario complete.",     # quiz_blank_sentence (6)
            agent.tts_avatar_tool.get_avatar_emoji("happy"), # avatar_state_lbl (7)
            agent.tts_avatar_tool.get_avatar_image("happy"), # avatar_image (8)
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(visible=False), # fill_blank_column (13)
            "🎉 Bra jobbat! You completed the full scenario.", # feedback_output (14)
            None,                     # audio_player (15)
            stage_done_html,          # stage_lbl (16)
            thought_trace,            # thought_tracer_out (17)
            build_study_guide_html(agent.retrieved_examples_log, agent.topic_context), # top_study_guide_card (18)
            memory_html,              # top_progress_vault_card (19)
            build_retrieved_table(agent.retrieved_examples_log), # grader_ir_table (20)
            "",                       # vocab_exps_card (21)
            gr.update(visible=False), # options_row (22)
            gr.update(visible=True),  # next_turn_panel (23)
            gr.update(value="Scenario complete", visible=True, interactive=False), # continue_btn
            gr.update(value="Try This Turn Again", visible=True, interactive=False), # retry_btn
            gr.update(value="Skip & Continue", visible=True, interactive=False), # skip_btn
            "Completed! Use Back to Topic Selection or Back to Configuration Screen to start another scenario." # status_lbl (24)
        ]

    # Load next turn data
    state = agent.load_next_dialogue_turn(quiz_type=quiz_type, lang=lang)
    
    avatar_emoji = agent.tts_avatar_tool.get_avatar_emoji("speaking")
    avatar_img = agent.tts_avatar_tool.get_avatar_image("speaking")
    
    study_guide_html = build_study_guide_html(agent.retrieved_examples_log, agent.topic_context)
    memory_html = build_progress_vault_html(agent.memory_tool.get_summary())
    grader_ir_table_html = build_retrieved_table(agent.retrieved_examples_log)
    thought_trace = "\n".join(agent.thought_logs)

    # Sven's spoken sentence and direct translation inside Sven's card
    spoken_sv_html = f"<div style='background:#ffffff; border-left:4px solid #4f46e5; border-radius:4px; padding:12px; margin-bottom:8px;'><h2 style='color:#1f2937; margin:0 0 4px 0; font-size:24px; font-weight:800;'>{state['avatar_sentence']}</h2><span style='color:#4b5563; font-size:14px; font-style:italic;'>Translation: {state['translation']}</span></div>"
    
    # Compile active dialogue transcript scrolling logs
    transcript_html = build_chat_transcript_html(agent.chat_history, lang)

    # Vocabulary Options explains (Looked up instantly in 0 ms!)
    vocab_exps_html = f"<div style='background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:10px;'><span style='color:#1d4ed8; font-size:13px;'>💡 <b>Vocab Help:</b> {state['vocab_hints']}</span></div>"

    # Build options buttons updates
    opt_updates = []
    for i in range(4):
        if quiz_type == "multiple_choice" and i < len(state["options"]):
            opt_updates.append(gr.update(value=state["options"][i], visible=True))
        else:
            opt_updates.append(gr.update(value="", visible=False))

    return [
        gr.update(visible=False), # setup_panel (1)
        gr.update(visible=True),  # practice_panel (2)
        gr.update(visible=False), # congrats_panel (3)
        spoken_sv_html,           # avatar_sv_sentence (4)
        transcript_html,          # dialogue_transcript_card (5)
        state["quiz_sentence"],   # quiz_blank_sentence (6)
        avatar_emoji,             # avatar_state_lbl (7)
        avatar_img if avatar_img else None, # avatar_image (8)
        opt_updates[0], opt_updates[1], opt_updates[2], opt_updates[3], # opt_btn1-4 (9, 10, 11, 12)
        gr.update(visible=(quiz_type == "fill_in_the_blank")), # fill_blank_column (13)
        "",                       # feedback_output (14)
        state["audio_path"] if state["audio_path"] else None, # audio_player (15)
        build_stage_lbl_html(state['stage_num'], state['stage_desc'], agent.dialogue_tool.max_stages), # stage_lbl (16)
        thought_trace,            # thought_tracer_out (17)
        study_guide_html,         # top_study_guide_card (18)
        memory_html,              # top_progress_vault_card (19)
        grader_ir_table_html,     # grader_ir_table (20)
        vocab_exps_html,          # vocab_exps_card (21)
        gr.update(visible=(quiz_type == "multiple_choice")),  # options_row (22)
        gr.update(visible=True),  # next_turn_panel (23)
        gr.update(value="Answer this turn first", visible=True, interactive=False), # continue_btn
        gr.update(value="Try This Turn Again", visible=True, interactive=False), # retry_btn
        gr.update(value="Skip & Continue", visible=True, interactive=False), # skip_btn
        "Ready! Tap the options below or fill in the blank to reply." + (f" ({agent.selected_plan_info})" if agent.selected_plan_info else "") # status_lbl (24)
    ]

def handle_retry_turn(quiz_type):
    """
    Instantaneous offline retry function. Restores options buttons / text inputs
    to let the user re-attempt the same turn without any API waiting delays.
    """
    # Resolve friendly UI names to technical keys
    quiz_type = QUIZ_TYPE_MAP.get(quiz_type, quiz_type)
    
    avatar_emoji = agent.tts_avatar_tool.get_avatar_emoji("neutral")
    avatar_img = agent.tts_avatar_tool.get_avatar_image("neutral")
    
    # Restore options buttons
    opt_updates = []
    for i in range(4):
        if quiz_type == "multiple_choice" and i < len(agent.active_quiz["options"]):
            opt_updates.append(gr.update(value=agent.active_quiz["options"][i], visible=True))
        else:
            opt_updates.append(gr.update(value="", visible=False))

    return [
        avatar_emoji,
        avatar_img if avatar_img else None,
        # Reveal options
        opt_updates[0], opt_updates[1], opt_updates[2], opt_updates[3],
        # Reset feedback
        "",
        # Reveal standard inputs, hide review panel
        gr.update(visible=True),  # options_row
        gr.update(visible=(quiz_type == "fill_in_the_blank")), # fill_blank_column
        gr.update(visible=True),  # next_turn_panel stays mounted
        gr.update(value="Answer this turn first", visible=True, interactive=False), # continue_btn
        gr.update(value="Try This Turn Again", visible=True, interactive=False), # retry_btn
        gr.update(value="Skip & Continue", visible=True, interactive=False), # skip_btn
        "Let's try again! Select the correct option or type the word."
    ]

def select_scenario(sc):
    """Updates selected scenario state and sets active primary button highlight."""
    updates = []
    scenarios = ["food_shop", "family_school", "health_places", "transport", "home_places", "social_intro"]
    for s in scenarios:
        if s == sc:
            updates.append(gr.update(variant="primary"))
        else:
            updates.append(gr.update(variant="secondary"))
    return [sc] + updates

def reset_to_setup():
    """Returns interface to config tab."""
    return [
        gr.update(visible=True),  # Show Setup tab
        gr.update(visible=False)  # Hide Practice tab
    ]

# Gradio Block Construction
with gr.Blocks() as demo:
    
    gr.HTML("<h1 class='accent-title'>🇸🇪 Swedish Listening & Reading Comprehension Practice Agent 🇸🇪</h1>")
    gr.HTML("<p style='text-align:center;'>A memory-aware Information Retrieval agent for pre-A1 beginner learners. Powered by dynamic local/online LLM pipelines.</p>")
    
    # ------------------ TAB 1: SETUP SCREEN ------------------
    with gr.Column(visible=True) as setup_panel:
        
        # 1. Warm Swedish Greeting Card (Short and sweet)
        with gr.Row():
            with gr.Column(elem_classes=["glass-panel"]):
                gr.HTML(
                    "<div style='text-align: center; padding: 6px;'>"
                    "<h2 style='color: #4f46e5; margin: 0 0 6px 0; font-size: 20px;'>Hej och välkommen! 🇸🇪</h2>"
                    "<p style='color: #374151; font-size: 14px; max-width: 600px; margin: 0 auto; line-height: 1.4;'>"
                    "Build your Swedish listening and reading comprehension with Sven, your interactive AI tutor. "
                    "No speaking required—just choose a scenario below to start!</p>"
                    "</div>"
                )
        
        # 2. Main Study & Scenario Selection Card (Student-Friendly Clickable Cards with 3D Illustrations)
        with gr.Row():
            with gr.Column(elem_classes=["glass-panel"]):
                gr.HTML("<h3 style='color: #4f46e5; margin-top: 0; margin-bottom: 4px; display:flex; align-items:center; gap:6px;'>🎒 Choose Your Study Scenario</h3>")
                gr.HTML("<p style='font-size: 13.5px; color: #4b5563; margin: 0 0 12px 0;'>Select an everyday immersion topic below to practice vocabulary and listening comprehension:</p>")
                
                # Define physical image file paths for gr.Image
                food_shop_path = os.path.join(config.ASSETS_DIR, 'scenario_food_shop.png')
                family_school_path = os.path.join(config.ASSETS_DIR, 'scenario_family_school.png')
                health_places_path = os.path.join(config.ASSETS_DIR, 'scenario_health_places.png')
                transport_path = os.path.join(config.ASSETS_DIR, 'scenario_transport.png')
                home_places_path = os.path.join(config.ASSETS_DIR, 'scenario_home_places.png')
                social_intro_path = os.path.join(config.ASSETS_DIR, 'scenario_social_intro.png')

                # Hidden textbox for Gradio to track state
                scenario_select = gr.Textbox(value="food_shop", visible=False)

                # Beautiful 3x2 interactive grid using native Gradio Rows and Columns
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Image(food_shop_path, show_label=False, interactive=False, container=False, height=130)
                        food_shop_btn = gr.Button("🛒 Matbutik", variant="primary")
                    with gr.Column(scale=1):
                        gr.Image(family_school_path, show_label=False, interactive=False, container=False, height=130)
                        family_school_btn = gr.Button("🏫 Familj & Skola", variant="secondary")
                    with gr.Column(scale=1):
                        gr.Image(health_places_path, show_label=False, interactive=False, container=False, height=130)
                        health_places_btn = gr.Button("🏥 Hälsa & Vård", variant="secondary")

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Image(transport_path, show_label=False, interactive=False, container=False, height=130)
                        transport_btn = gr.Button("🚌 Transport", variant="secondary")
                    with gr.Column(scale=1):
                        gr.Image(home_places_path, show_label=False, interactive=False, container=False, height=130)
                        home_places_btn = gr.Button("🏡 Hem & Platser", variant="secondary")
                    with gr.Column(scale=1):
                        gr.Image(social_intro_path, show_label=False, interactive=False, container=False, height=130)
                        social_intro_btn = gr.Button("👋 Presentationer", variant="secondary")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        quiz_type_select = gr.Radio(
                            choices=[
                                "🎯 Multiple Choice Quiz (单选题)",
                                "✍️ Fill-in-the-Blank Exercise (填空题)"
                            ],
                            label="Practice Exercise Style",
                            value="🎯 Multiple Choice Quiz (单选题)"
                        )
                    with gr.Column(scale=1):
                        lang_select = gr.Radio(
                            choices=[
                                "🇬🇧 English (英文)",
                                "🇨🇳 Chinese (中文)"
                            ],
                            label="Tutor Explanation Language",
                            value="🇬🇧 English (英文)"
                        )
                
                # Prominent orange action button
                start_btn = gr.Button("🚀 Start My Swedish Lesson", variant="primary")
        
        # 3. Technical Config Accordion (Closed by default - User Friendly)
        with gr.Accordion("⚙️ Advanced Engine Connection Settings (Ollama / Online LLM)", open=False):
            gr.HTML(
                "<div style='background: #f3f4f6; border-left: 4px solid #9ca3af; padding: 12px; border-radius: 4px; margin-bottom: 12px; font-size: 13px; color: #4b5563;'>"
                "💡 <b>Note for Learners:</b> You don't need to change these settings! By default, the application runs locally using a standard Ollama server. "
                "Only open this panel if you want to switch to Online Mode (OpenAI / Berget.ai) or test your server connection diagnostics."
                "</div>"
            )
            with gr.Row():
                with gr.Column(elem_classes=["glass-panel"]):
                    gr.Markdown("### ⚙️ Engine Mode Configuration")
                    mode_select = gr.Radio(
                        ["Local Mode", "Online Mode"],
                        label="LLM Execution Mode",
                        value="Local Mode"
                    )
                    
                    # Local controls
                    with gr.Column(visible=True) as local_controls:
                        local_endpoint = gr.Textbox(
                            label="Ollama Server Endpoint URL",
                            value=config.OLLAMA_ENDPOINT
                        )
                        local_model = gr.Textbox(
                            label="Ollama Model Name (multilingual / Swedish capable)",
                            value=config.DEFAULT_LOCAL_MODEL,
                            placeholder="e.g. qwen2.5, llama3.1, mistral"
                         )
                    
                    # Online controls
                    with gr.Column(visible=False) as online_controls:
                        online_key = gr.Textbox(
                            label="OpenAI / Berget.ai API Key",
                            placeholder="sk-...",
                            type="password"
                        )
                        online_base = gr.Textbox(
                            label="API base URL URL",
                            value=config.OPENAI_API_BASE,
                            placeholder="e.g. https://api.openai.com/v1"
                        )
                        online_model = gr.Textbox(
                            label="Online Model Name",
                            value=config.DEFAULT_ONLINE_MODEL
                        )
                    
                    check_btn = gr.Button("⚡ Check Server Connection Diagnostics", variant="secondary")
                    check_out = gr.Textbox(label="Diagnostic Logs Output", interactive=False)
        
        # Link dynamic setup swap
        mode_select.change(
            update_mode_visibility,
            inputs=[mode_select],
            outputs=[local_controls, online_controls]
        )
        
        check_btn.click(
            handle_check_connection,
            inputs=[mode_select, local_endpoint, local_model, online_key, online_base, online_model],
            outputs=[check_out]
        )


    # ------------------ TAB 3: CONGRATULATIONS PANEL ------------------
    with gr.Column(visible=False) as congrats_panel:
        with gr.Row():
            with gr.Column(elem_classes=["glass-panel"]):
                gr.HTML(
                    "<div style='text-align: center; padding: 32px 16px;'>"
                    "<h1 style='font-size: 64px; margin: 0 0 16px 0;'>🏆</h1>"
                    "<h2 style='color: #4f46e5; font-size: 32px; margin: 0 0 12px 0; font-weight: 800;'>Bra jobbat! Scenario Complete! 🇸🇪</h2>"
                    "<p style='color: #374151; font-size: 16.5px; max-width: 600px; margin: 0 auto 24px auto; line-height: 1.6;'>"
                    "Congratulations! You have completed all 5 dialogue turns with Sven! "
                    "Your Swedish listening, vocabulary, and reading comprehension are improving step by step."
                    "</p>"
                    "<div style='background: rgba(79, 70, 229, 0.04); border: 1px solid rgba(79, 70, 229, 0.1); "
                    "border-radius: 12px; padding: 20px; max-width: 480px; margin: 0 auto 32px auto;'>"
                    "<h3 style='margin: 0 0 8px 0; color: #4f46e5; font-size: 16px; font-weight: 700;'>📈 Practice Vault Recorded</h3>"
                    "<p style='margin: 0; font-size: 14px; color: #4b5563;'>Immersion Scenario: <b>Everyday Conversations</b><br>"
                    "Practice Mode: <b>Spaced Repetition Review Model</b><br>"
                    "Status: 🟢 <b>Progress logged successfully</b></p>"
                    "</div>"
                    "</div>"
                )
                back_to_topics_btn = gr.Button("🎒 Back to Topic Selection (返回主题选择)", variant="primary")

    def click_back_to_topics():
        return [
            gr.update(visible=True),  # Show Setup tab
            gr.update(visible=False), # Hide Congrats tab
            gr.update(visible=False)  # Hide Practice tab
        ]

    # ------------------ TAB 2: PRACTICE PANEL ------------------
    with gr.Column(visible=False) as practice_panel:
        
        # TOP INTRO: Scenario Knowledge Reading Card (IR generated)
        with gr.Row():
            top_study_guide_card = gr.HTML("<p>Retrieved phrases are loading...</p>")

        # CORE WORKSPACE (Clean dual column layout)
        with gr.Row():
            # Column A: Your Tutor (Audio, Avatar Visuals)
            with gr.Column(scale=1, elem_classes=["glass-panel"]):
                gr.Markdown("#### 🧑‍🏫 Your Swedish Tutor: Sven")
                avatar_state_lbl = gr.Label(value="😐 Ready", label="Avatar Status")
                avatar_image = gr.Image(value=None, label="Vocal Avatar Image", height=280)
                
                gr.Markdown("#### 🔊 Swedish Narration")
                audio_player = gr.Audio(label="Swedish Audio playback", autoplay=True)

                gr.Markdown("#### 💬 Dialogue Transcript")
                dialogue_transcript_card = gr.HTML("<p>Dialogue transcript loading...</p>")

            # Column B: Conversation, Quizzes, Peeking Translation
            with gr.Column(scale=2, elem_classes=["glass-panel"]):
                stage_lbl = gr.HTML("<div style='background:linear-gradient(90deg, #4f46e5, #3b82f6); color:#ffffff; padding:10px 16px; border-radius:10px; margin-bottom:16px; font-weight:700;'>Turn 1/5: Loading...</div>")

                # Sven's Turn Card
                with gr.Column(elem_classes=["sven-card"]):
                    gr.HTML("<span class='card-header-tag tag-sven'>🗣️ Sven says (Sven 的表达)</span>")
                    avatar_sv_sentence = gr.HTML("<div style='background:#ffffff; border-left:4px solid #4f46e5; padding:12px;'><h2 style='margin:0 0 4px 0; font-size:24px; font-weight:800;'>Hej!</h2><span style='color:#4b5563; font-size:14px; font-style:italic;'>🇬🇧 English: Hello!</span></div>")
                
                # Practice Quiz Card
                with gr.Column(elem_classes=["quiz-card"]):
                    gr.HTML("<span class='card-header-tag tag-quiz'>📝 Practice Quiz Exercise (测验练习)</span>")
                    quiz_blank_sentence = gr.Textbox(label="Complete the blank space to reply:", interactive=False)
                    
                    # Dynamic Multiple Choice options
                    with gr.Row() as options_row:
                        opt_btn1 = gr.Button("Option A", variant="secondary")
                        opt_btn2 = gr.Button("Option B", variant="secondary")
                        opt_btn3 = gr.Button("Option C", variant="secondary")
                        opt_btn4 = gr.Button("Option D", variant="secondary")
                        
                    # Dynamic Fill in the blank text box
                    with gr.Column(visible=False) as fill_blank_column:
                        text_blank_input = gr.Textbox(label="Type the Swedish word here:", placeholder="e.g. kaffe")
                        text_submit_btn = gr.Button("Submit Answer", variant="primary")

                    # Dynamic options vocabulary explanations hint sheet (Instant offline lookup!)
                    vocab_exps_card = gr.HTML("<p>Loading vocabulary explanations...</p>")

                # Feedback & Corrections Card
                with gr.Column(elem_classes=["feedback-card"]):
                    gr.HTML("<span class='card-header-tag tag-feedback'>📣 Tutor Correction & Feedback Details (导师反馈与纠错)</span>")
                    feedback_output = gr.Markdown("Feedback is generated after answer submission.")
                
                # --- STEP-BY-STEP DIALOGUE CONTROLS PANEL ---
                # Hides standard answers and reveals study review buttons
                with gr.Column(visible=True, elem_classes=["glass-panel"]) as next_turn_panel:
                    gr.Markdown("<p style='margin:0 0 8px 0; color:#4f46e5; font-weight:bold;'>🎯 Review turn study guides, then choose next step:</p>")
                    with gr.Row():
                        continue_btn = gr.Button("Answer this turn first", variant="primary", visible=True, interactive=False)
                        retry_btn = gr.Button("Try This Turn Again", variant="secondary", visible=True, interactive=False)
                        skip_btn = gr.Button("Skip & Continue", variant="secondary", visible=True, interactive=False)

                status_lbl = gr.Textbox(label="Status", value="Ready", interactive=False)
                
                back_btn = gr.Button("⬅️ Back to Configuration Screen", variant="secondary")

        # Visual Flashcards Study Progress Board (Memory Vault)
        with gr.Row():
            top_progress_vault_card = gr.HTML("<p>Memory progress data is loading...</p>")
        with gr.Row():
            open_memory_review_btn = gr.Button("🧠 Start Memory Review Quiz (复习错词卡片)", variant="primary")

        # ------------------ COLLAPSIBLE DEV DEBUG DRAWER ------------------
        with gr.Accordion("🛠️ Developer & Evaluator Debug Drawer (Chain of Thought & Vector weights)", open=False):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🔍 Retrieved Semantic Context (Technical IR Weights)")
                    grader_ir_table = gr.HTML("<p>Technical IR scores are loading...</p>")
                with gr.Column(scale=1):
                    gr.Markdown("### 🤖 Agent Heartbeat Thought Tracer (Chain of Thought logs)")
                    thought_tracer_out = gr.Textbox(
                        value="", 
                        label="Visual thought trace (thought -> action -> observation -> respond)", 
                        interactive=False, 
                        lines=10, 
                        elem_classes=["terminal-debug"]
                    )

    # ------------------ TAB 4: MEMORY REVIEW QUIZ PANEL ------------------
    review_items_state = gr.State([])
    review_index_state = gr.State(0)

    with gr.Column(visible=False) as memory_review_panel:
        with gr.Row():
            with gr.Column(elem_classes=["glass-panel"]):
                gr.HTML(
                    "<div style='text-align:center; padding:6px 0 12px 0;'>"
                    "<h2 style='margin:0 0 6px 0; color:#4f46e5;'>🧠 Memory Review Quiz</h2>"
                    "<p style='margin:0; color:#4b5563; font-size:14px;'>"
                    "Practice the words your tutor marked for review. Listen, choose the meaning, then move to the next card."
                    "</p></div>"
                )
                review_card_html = gr.HTML("<p>Review cards are loading...</p>")
                with gr.Row():
                    review_opt1 = gr.Button("Option A", variant="secondary")
                    review_opt2 = gr.Button("Option B", variant="secondary")
                    review_opt3 = gr.Button("Option C", variant="secondary")
                    review_opt4 = gr.Button("Option D", variant="secondary")
                review_feedback = gr.Markdown("")
                with gr.Row():
                    review_next_btn = gr.Button("Next Card", variant="primary", interactive=False)
                    review_restart_btn = gr.Button("Restart Review Queue", variant="secondary")
                    review_back_btn = gr.Button("Back to Lesson", variant="secondary")

    # Wire scenario selection grid native buttons
    scenario_buttons = [food_shop_btn, family_school_btn, health_places_btn, transport_btn, home_places_btn, social_intro_btn]
    
    food_shop_btn.click(lambda: select_scenario("food_shop"), outputs=[scenario_select] + scenario_buttons)
    family_school_btn.click(lambda: select_scenario("family_school"), outputs=[scenario_select] + scenario_buttons)
    health_places_btn.click(lambda: select_scenario("health_places"), outputs=[scenario_select] + scenario_buttons)
    transport_btn.click(lambda: select_scenario("transport"), outputs=[scenario_select] + scenario_buttons)
    home_places_btn.click(lambda: select_scenario("home_places"), outputs=[scenario_select] + scenario_buttons)
    social_intro_btn.click(lambda: select_scenario("social_intro"), outputs=[scenario_select] + scenario_buttons)

    # Wire start trigger
    start_btn.click(
        handle_start_agent,
        inputs=[
            mode_select, local_endpoint, local_model, online_key, online_base, online_model,
            scenario_select, quiz_type_select, lang_select
        ],
        outputs=[
            setup_panel, practice_panel,
            avatar_sv_sentence, dialogue_transcript_card, quiz_blank_sentence,
            avatar_state_lbl, avatar_image,
            opt_btn1, opt_btn2, opt_btn3, opt_btn4,
            fill_blank_column,
            feedback_output,
            audio_player,
            stage_lbl,
            thought_tracer_out,
            top_study_guide_card,
            top_progress_vault_card,
            grader_ir_table,
            vocab_exps_card,
            options_row,
            next_turn_panel,
            continue_btn,
            retry_btn,
            skip_btn,
            status_lbl
        ]
    )

    # Wire Back trigger
    back_btn.click(
        reset_to_setup,
        outputs=[setup_panel, practice_panel]
    )

    # Wire options selections
    practice_outputs = [
        quiz_blank_sentence, avatar_state_lbl, avatar_image,
        opt_btn1, opt_btn2, opt_btn3, opt_btn4,
        feedback_output, audio_player, stage_lbl,
        thought_tracer_out, top_study_guide_card, top_progress_vault_card,
        grader_ir_table, vocab_exps_card, avatar_sv_sentence,
        dialogue_transcript_card,
        options_row, fill_blank_column,
        next_turn_panel, continue_btn, retry_btn, skip_btn,
        status_lbl
    ]

    opt_btn1.click(
        handle_submit_answer,
        inputs=[opt_btn1, quiz_type_select, lang_select],
        outputs=practice_outputs
    )
    opt_btn2.click(
        handle_submit_answer,
        inputs=[opt_btn2, quiz_type_select, lang_select],
        outputs=practice_outputs
    )
    opt_btn3.click(
        handle_submit_answer,
        inputs=[opt_btn3, quiz_type_select, lang_select],
        outputs=practice_outputs
    )
    opt_btn4.click(
        handle_submit_answer,
        inputs=[opt_btn4, quiz_type_select, lang_select],
        outputs=practice_outputs
    )

    # Wire text blanks
    text_submit_btn.click(
        handle_submit_answer,
        inputs=[text_blank_input, quiz_type_select, lang_select],
        outputs=practice_outputs
    )

    # Wire turn control panel actions
    next_turn_outputs = [
        setup_panel, practice_panel, congrats_panel,
        avatar_sv_sentence, dialogue_transcript_card, quiz_blank_sentence,
        avatar_state_lbl, avatar_image,
        opt_btn1, opt_btn2, opt_btn3, opt_btn4,
        fill_blank_column,
        feedback_output,
        audio_player,
        stage_lbl,
        thought_tracer_out,
        top_study_guide_card,
        top_progress_vault_card,
        grader_ir_table,
        vocab_exps_card,
        options_row,
        next_turn_panel,
        continue_btn,
        retry_btn,
        skip_btn,
        status_lbl
    ]
    
    continue_btn.click(
        handle_load_next_turn,
        inputs=[quiz_type_select, lang_select],
        outputs=next_turn_outputs
    )
    skip_btn.click(
        handle_load_next_turn,
        inputs=[quiz_type_select, lang_select],
        outputs=next_turn_outputs
    )

    # Retry triggers
    retry_outputs = [
        avatar_state_lbl, avatar_image,
        opt_btn1, opt_btn2, opt_btn3, opt_btn4,
        feedback_output,
        options_row, fill_blank_column,
        next_turn_panel,
        continue_btn, retry_btn, skip_btn,
        status_lbl
    ]
    retry_btn.click(
        handle_retry_turn,
        inputs=[quiz_type_select],
        outputs=retry_outputs
    )

    memory_review_open_outputs = [
        setup_panel, practice_panel, congrats_panel, memory_review_panel,
        review_items_state, review_index_state,
        review_card_html,
        review_opt1, review_opt2, review_opt3, review_opt4,
        review_feedback, review_next_btn
    ]
    open_memory_review_btn.click(
        handle_open_memory_review,
        outputs=memory_review_open_outputs
    )

    memory_review_answer_outputs = [
        review_opt1, review_opt2, review_opt3, review_opt4,
        review_feedback, review_next_btn
    ]
    review_opt1.click(
        handle_memory_review_answer,
        inputs=[review_opt1, review_items_state, review_index_state],
        outputs=memory_review_answer_outputs
    )
    review_opt2.click(
        handle_memory_review_answer,
        inputs=[review_opt2, review_items_state, review_index_state],
        outputs=memory_review_answer_outputs
    )
    review_opt3.click(
        handle_memory_review_answer,
        inputs=[review_opt3, review_items_state, review_index_state],
        outputs=memory_review_answer_outputs
    )
    review_opt4.click(
        handle_memory_review_answer,
        inputs=[review_opt4, review_items_state, review_index_state],
        outputs=memory_review_answer_outputs
    )

    memory_review_next_outputs = [
        review_index_state,
        review_card_html,
        review_opt1, review_opt2, review_opt3, review_opt4,
        review_feedback, review_next_btn
    ]
    review_next_btn.click(
        handle_next_memory_review_card,
        inputs=[review_items_state, review_index_state],
        outputs=memory_review_next_outputs
    )

    memory_review_restart_outputs = [
        review_items_state, review_index_state,
        review_card_html,
        review_opt1, review_opt2, review_opt3, review_opt4,
        review_feedback, review_next_btn
    ]
    review_restart_btn.click(
        handle_restart_memory_review,
        outputs=memory_review_restart_outputs
    )

    review_back_btn.click(
        handle_back_to_practice_from_review,
        outputs=[setup_panel, practice_panel, congrats_panel, memory_review_panel, top_progress_vault_card]
    )

    back_to_topics_btn.click(
        click_back_to_topics,
        outputs=[setup_panel, congrats_panel, practice_panel]
    )

if __name__ == "__main__":
    # Force light mode by stripping any 'dark' classes on launch
    # Expose the assets directory so Gradio can serve cached audio files securely via /file=
    demo.launch(
        theme=gr.themes.Default(),
        css=CUSTOM_CSS,
        allowed_paths=[config.ASSETS_DIR],
        js="() => { document.body.classList.remove('dark'); }"
    )
