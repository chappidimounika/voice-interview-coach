# 🎤 Voice Interview Coach

Practice placement interviews in **Telugu, Hindi or English** and get instant AI feedback.

Built for the **Great Indian AI Internship Challenge** by Gnani AI.

## How it works
1. 🔊 The app asks an interview question out loud (Gnani **Timbre** text-to-speech)
2. 🎙️ You answer in your own language
3. 🗣️ Gnani **Prisma** converts your speech to text
4. 🎯 AI gives a score, what was good, what to improve, and a better sample answer

## Tech stack
- Python, Streamlit
- Gnani AI Prisma (STT) and Timbre (TTS)
- Gemini for feedback

## Run locally
pip install -r requirements.txt

Create `.streamlit/secrets.toml`:
GNANI_API_KEY = "your-gnani-key"
GEMINI_API_KEY = "your-gemini-key"

Then run:
streamlit run app.py

## Live demo
(https://voice-interview-coach.streamlit.app/)
#GnaniAI #GreatIndianAIInternshipChallenge
