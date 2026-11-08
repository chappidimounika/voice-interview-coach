# Voice Interview Coach: Solution Pitch

**Built by:** Chappidi Mounika  |  **Challenge:** The Great Indian AI Internship Challenge  
**Live app:** https://voice-interview-coach.streamlit.app  
**Code:** https://github.com/chappidimounika/voice-interview-coach

## The problem
Campus placements in India depend on interviews, but good practice is hard to get. Mock interviews need another person, and almost every AI practice tool expects typed or English-only input. Students from Tier 2 and Tier 3 towns are most comfortable in their mother tongue (Telugu, Hindi), so they get little chance to practise speaking confidently, and their effort is judged on language fluency before content.

## The solution
**Voice Interview Coach** is a voice-first web app where a student practises an interview alone, in Telugu, Hindi or English, and gets instant, structured feedback.

1. **Listen:** the app asks a common interview question out loud (Gnani **Timbre** text-to-speech).
2. **Answer:** the student records the answer in their own language.
3. **Transcribe:** Gnani **Prisma** speech-to-text converts the spoken Telugu, Hindi or English into text.
4. **Feedback:** an LLM scores the answer on Content, Structure, Clarity and Confidence, lists what was good and what to improve, and writes a better sample answer using only the facts the student actually said.
5. **Learn:** the student can hear the better answer read aloud (Timbre) and track attempts, average score and best score across a session.

## Why it matters
- **Regional-language first:** students can think and speak in Telugu or Hindi, then see how to say it better in English.
- **Free, private, always available:** practise any time, as many times as needed, without needing a mentor.
- **Real-world impact:** helps students from smaller towns prepare for placements on equal footing.

## How Gnani models are used
- **Prisma (STT):** core of the product. Converts spoken answers (Telugu, Hindi, English, including code-mixed speech) to text.
- **Timbre (TTS):** gives the app a voice. Reads interview questions and the improved sample answer aloud.

## Tech stack
Python, Streamlit, Gnani Prisma + Timbre APIs, Gemini for feedback generation, deployed on Streamlit Community Cloud.

## What's next
More question banks by role (software, HR, core engineering), pronunciation and filler-word analysis, progress tracking across days, and more Indian languages.

#GnaniAI #GreatIndianAIInternshipChallenge
