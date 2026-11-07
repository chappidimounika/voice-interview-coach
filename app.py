import html
import json
import os
import random
import re

import requests
import streamlit as st


def get_key(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, "")


GNANI_KEY = get_key("GNANI_API_KEY")
GEMINI_KEY = get_key("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
STT_URL = "https://api.vachana.ai/stt/v3"
TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"

LANGS = {"Telugu": "te-IN", "English": "en-IN", "Hindi": "hi-IN"}

QUESTIONS = [
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Why should we hire you?",
    "Tell me about a project you are proud of.",
    "Where do you see yourself in five years?",
    "Describe a time you faced a challenge and how you handled it.",
    "Why do you want to work in this company?",
]


# ---------------------------------------------------------------- Gnani APIs
def transcribe(audio_bytes: bytes, lang_code: str) -> str:
    resp = requests.post(
        STT_URL,
        headers={"X-API-Key-ID": GNANI_KEY},
        files={"audio_file": ("answer.wav", audio_bytes, "audio/wav")},
        data={"language_code": lang_code, "format": "verbatim"},
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Prisma error {resp.status_code}: {resp.text[:300]}")
    return resp.json().get("transcript", "")


@st.cache_data(show_spinner=False)
def speak(text: str) -> bytes:
    resp = requests.post(
        TTS_URL,
        headers={"X-API-Key-ID": GNANI_KEY, "Content-Type": "application/json"},
        json={
            "text": text,
            "voice": "Kaveri",
            "model": "timbre-v2.5",
            "language": "en-IN",
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 24000,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Timbre error {resp.status_code}: {resp.text[:300]}")
    return resp.content


# ------------------------------------------------------------------ Feedback
def get_feedback(question: str, transcript: str) -> dict:
    prompt = f"""You are a friendly interview coach for Indian college students preparing for campus placements.

Interview question: {question}
Candidate's spoken answer (auto-transcribed, may be Telugu/Hindi/English mix): {transcript}

Return ONLY valid JSON (no markdown, no code fences) in exactly this shape:
{{
  "scores": {{"content": 0-10, "structure": 0-10, "clarity": 0-10, "confidence": 0-10}},
  "summary": "one encouraging sentence",
  "good": ["point 1", "point 2"],
  "improve": ["point 1", "point 2", "point 3"],
  "sample_answer": "a better 5-6 line answer in English"
}}
Rules: use ONLY facts the candidate actually said. Do not invent degree year, skills, tools or goals. If the sample answer needs a detail they did not give, use a [placeholder in brackets]. Mention filler words or repeated words in "improve" if any. Keep every point short. Scores must be numbers."""
    models = [GEMINI_MODEL, "gemini-3.5-flash"]
    last_error = ""
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for _ in range(2):
            try:
                resp = requests.post(
                    url,
                    headers={"x-goog-api-key": GEMINI_KEY, "Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"responseMimeType": "application/json"},
                    },
                    timeout=90,
                )
            except requests.exceptions.RequestException as e:
                last_error = f"{model}: network/timeout ({type(e).__name__})"
                continue
            if resp.status_code == 200:
                text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                return parse_feedback(text)
            last_error = f"{model}: {resp.status_code} {resp.text[:200]}"
            if resp.status_code in (404, 400, 401, 403):
                break
    raise RuntimeError("Gemini could not respond. " + last_error)


def parse_feedback(text: str) -> dict:
    clean = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(clean)
        scores = {}
        for k in ("content", "structure", "clarity", "confidence"):
            v = float(data.get("scores", {}).get(k, 0))
            scores[k] = max(0.0, min(10.0, v))
        return {
            "scores": scores,
            "summary": str(data.get("summary", "")),
            "good": [str(x) for x in data.get("good", [])],
            "improve": [str(x) for x in data.get("improve", [])],
            "sample_answer": str(data.get("sample_answer", "")),
        }
    except Exception:
        return {"raw": text}


# ------------------------------------------------------------------ UI helpers
CSS = """
<style>
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"] {display: none !important;}
.block-container {max-width: 780px; padding-top: 1.2rem; padding-bottom: 3rem;}
.hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #ec4899 100%);
    border-radius: 22px; padding: 24px 28px; color: white; margin-bottom: 16px;
    box-shadow: 0 12px 30px rgba(79,70,229,.25);
}
.hero h1 {margin: 0; font-size: 2rem; color: white; padding: 0;}
.hero p {margin: 6px 0 0 0; opacity: .95; font-size: 1rem;}
.chips {margin-top: 12px;}
.chip {display: inline-block; background: rgba(255,255,255,.18); border-radius: 999px;
    padding: 4px 12px; margin: 0 6px 6px 0; font-size: .8rem;}
.stats {display: flex; gap: 10px; margin-bottom: 14px;}
.stat {flex: 1; background: white; border: 1px solid #ece8ff; border-radius: 14px;
    padding: 10px 12px; text-align: center; box-shadow: 0 3px 10px rgba(124,58,237,.06);}
.stat b {display: block; font-size: 1.35rem; color: #5b21b6;}
.stat span {font-size: .75rem; color: #6b7280; letter-spacing: .04em;}
.qcard {background: white; border: 1px solid #e5e7eb; border-left: 6px solid #7c3aed;
    border-radius: 16px; padding: 18px 22px; margin: 10px 0 12px 0;
    box-shadow: 0 6px 18px rgba(0,0,0,.05);}
.qlabel {color: #7c3aed; font-size: .75rem; font-weight: 800; letter-spacing: .08em;}
.qtext {font-size: 1.5rem; font-weight: 700; color: #1f2937; margin-top: 4px;}
.heard {background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 14px;
    padding: 14px 18px; color: #065f46; font-size: 1.05rem; line-height: 1.6;}
.resultcard {background: white; border: 1px solid #ece8ff; border-radius: 20px; padding: 22px;
    box-shadow: 0 10px 28px rgba(124,58,237,.10); margin-top: 8px;}
.resulttop {display: flex; gap: 22px; align-items: center; flex-wrap: wrap;}
.ring {width: 118px; height: 118px; border-radius: 50%; flex-shrink: 0;
    background: conic-gradient(#7c3aed calc(var(--p) * 1%), #ece8ff 0);
    display: flex; align-items: center; justify-content: center;}
.ringin {width: 92px; height: 92px; border-radius: 50%; background: white;
    display: flex; flex-direction: column; align-items: center; justify-content: center;}
.ringin b {font-size: 1.7rem; color: #4c1d95; line-height: 1;}
.ringin span {font-size: .75rem; color: #6b7280;}
.bars {flex: 1; min-width: 220px;}
.bar {margin-bottom: 9px;}
.barlabel {display: flex; justify-content: space-between; font-size: .82rem; color: #374151; margin-bottom: 3px;}
.track {height: 9px; background: #ece8ff; border-radius: 99px; overflow: hidden;}
.fill {height: 100%; border-radius: 99px; background: linear-gradient(90deg, #7c3aed, #ec4899);}
.summary {margin: 16px 0 4px 0; font-size: 1.02rem; color: #374151;}
.panel {border-radius: 14px; padding: 14px 18px; margin-top: 12px; font-size: .95rem; line-height: 1.6;}
.panel h4 {margin: 0 0 6px 0; font-size: .95rem;}
.panel ul {margin: 0; padding-left: 18px;}
.good {background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46;}
.improve {background: #fffbeb; border: 1px solid #fde68a; color: #92400e;}
.sample {background: #f5f3ff; border: 1px solid #ddd6fe; color: #3b2a7a;}
.footer {text-align: center; color: #9ca3af; font-size: .8rem; margin-top: 28px;}
div.stButton > button {border-radius: 12px; font-weight: 600;}
</style>
"""


def esc(x) -> str:
    return html.escape(str(x))


def ring_html(score: float) -> str:
    pct = int(round(score * 10))
    return (
        f'<div class="ring" style="--p:{pct}"><div class="ringin">'
        f"<b>{score:.1f}</b><span>/ 10</span></div></div>"
    )


def bars_html(scores: dict) -> str:
    out = ""
    for k, v in scores.items():
        out += (
            f'<div class="bar"><div class="barlabel"><span>{k.title()}</span>'
            f"<span>{v:.1f}/10</span></div>"
            f'<div class="track"><div class="fill" style="width:{int(v * 10)}%"></div></div></div>'
        )
    return out


def list_html(items) -> str:
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def render_result(res: dict):
    fb = res["fb"]
    st.markdown("#### 📝 What I heard")
    st.markdown(
        f'<div class="heard">{esc(res["transcript"]) or "Nothing detected."}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("#### 🎯 Your feedback")
    if "raw" in fb:
        with st.container(border=True):
            st.markdown(fb["raw"])
        return
    overall = sum(fb["scores"].values()) / 4
    st.markdown(
        f"""<div class="resultcard">
        <div class="resulttop">{ring_html(overall)}<div class="bars">{bars_html(fb["scores"])}</div></div>
        <div class="summary">💬 {esc(fb["summary"])}</div>
        <div class="panel good"><h4>✅ What was good</h4>{list_html(fb["good"])}</div>
        <div class="panel improve"><h4>🚀 What to improve</h4>{list_html(fb["improve"])}</div>
        <div class="panel sample"><h4>⭐ A better answer</h4>{esc(fb["sample_answer"])}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    if fb["sample_answer"] and st.button("🔊 Hear the better answer", use_container_width=True):
        try:
            st.audio(speak(fb["sample_answer"]), format="audio/wav")
        except Exception as e:
            st.warning(f"Voice not available right now: {e}")


# ------------------------------------------------------------------------ App
st.set_page_config(page_title="Voice Interview Coach", page_icon="🎤", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

if not GNANI_KEY or not GEMINI_KEY:
    st.error("API keys missing. Add GNANI_API_KEY and GEMINI_API_KEY in .streamlit/secrets.toml.")
    st.stop()

ss = st.session_state
ss.setdefault("question", random.choice(QUESTIONS))
ss.setdefault("history", [])
ss.setdefault("result", None)
ss.setdefault("rec_n", 0)

attempts = len(ss.history)
avg = f"{sum(ss.history) / attempts:.1f}" if attempts else "–"
best = f"{max(ss.history):.1f}" if attempts else "–"

st.markdown(
    f"""
<div class="hero">
  <h1>🎤 Voice Interview Coach</h1>
  <p>Practice placement interviews in Telugu, Hindi or English and get instant AI feedback.</p>
  <div class="chips">
    <span class="chip">🗣️ Gnani Prisma · speech-to-text</span>
    <span class="chip">🔊 Gnani Timbre · text-to-speech</span>
    <span class="chip">🤖 AI feedback</span>
  </div>
</div>
<div class="stats">
  <div class="stat"><b>{attempts}</b><span>ATTEMPTS</span></div>
  <div class="stat"><b>{avg}</b><span>AVERAGE SCORE</span></div>
  <div class="stat"><b>{best}</b><span>BEST SCORE</span></div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("**🌐 I will answer in**")
lang_name = st.radio("Answer language", list(LANGS), horizontal=True, label_visibility="collapsed")

st.markdown(
    f"""<div class="qcard"><div class="qlabel">INTERVIEW QUESTION</div>
    <div class="qtext">{esc(ss.question)}</div></div>""",
    unsafe_allow_html=True,
)

b1, b2 = st.columns(2)
listen = b1.button("🔊 Listen to question", use_container_width=True)
if b2.button("🔄 New question", use_container_width=True):
    ss.question = random.choice([q for q in QUESTIONS if q != ss.question])
    ss.result = None
    ss.rec_n += 1
    st.rerun()

if listen:
    try:
        q_audio = speak(ss.question)
        try:
            st.audio(q_audio, format="audio/wav", autoplay=True)
        except TypeError:
            st.audio(q_audio, format="audio/wav")
    except Exception as e:
        st.warning(f"Voice not available right now: {e}")

audio = st.audio_input("🎙️ Record your answer (max 60 seconds)", key=f"rec_{ss.rec_n}")

if audio is not None:
    if st.button("✨ Get feedback", type="primary", use_container_width=True):
        with st.spinner("Listening to your answer..."):
            try:
                transcript = transcribe(audio.getvalue(), LANGS[lang_name])
            except Exception as e:
                st.error(str(e))
                st.stop()
        if not transcript:
            st.warning("Nothing detected. Try again closer to the mic.")
            st.stop()
        with st.spinner("Preparing your feedback..."):
            try:
                fb = get_feedback(ss.question, transcript)
            except Exception as e:
                st.error(str(e))
                st.stop()
        ss.result = {"transcript": transcript, "fb": fb}
        if "scores" in fb:
            ss.history.append(sum(fb["scores"].values()) / 4)
        st.rerun()

if ss.result:
    render_result(ss.result)

st.markdown(
    '<div class="footer">Built for the Great Indian AI Internship Challenge · #GnaniAI #GreatIndianAIInternshipChallenge</div>',
    unsafe_allow_html=True,
)