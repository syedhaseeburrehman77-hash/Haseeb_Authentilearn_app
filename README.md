# 🧠 AuthentiLearn AI — Academic Integrity Evaluator

**AuthentiLearn AI** is a production-ready, highly aesthetic Streamlit web application designed to evaluate a student's actual understanding of their submitted coursework through an interactive, AI-driven viva (oral exam). It does not just check for plagiarized text; it checks for **deep conceptual comprehension**.

---

## 🚀 Key Features

1. **Interactive Demo Mode (No API Key Required)**: Toggle "Demo Mode" in the sidebar to bypass the API key checking. Evaluates a pre-loaded Python Machine Learning classifier code structure using dynamic mock JSON evaluations. Excellent for immediate review and testing!
2. **Dynamic 5-Question Oral Viva**: Generates specific questions mapped directly to the submission content, spanning conceptual queries, application modifications, and gotcha/edge case constraint limits.
3. **Adaptive Follow-up Inquiries**: If an answer shows high ambiguity, vague definitions, or AI-style hedging, the engine triggers a purple-themed pointed follow-up question to test student logic.
4. **Voice Synthesizer (TTS)**: Built-in speaker audio allows students to hear questions read aloud.
5. **Confidence Answering Timeline**: Evaluates how long the student takes to respond to questions, translating speed metrics into confidence signals.
6. **Plotly Diagnostics & Expected Benchmarks**: Displays an interactive Radar chart comparing student scores against expected difficulty thresholds, alongside a Line chart tracing their chronological progression.
7. **Student vs Educator Modes**: Toggling "Educator Mode" displays advanced suspicious patterns, detailed red flag indices, and consolidated next-step actions.
8. **Multi-Language UI Support**: Dynamic on-the-fly toggling between **English**, **Urdu**, and **Arabic** UI labels for localized testing environments.

---

## 📁 Project Folder Structure

```text
authentilearn/
├── app.py                        # Main Streamlit UI & 4-Stage Orchestrator
├── requirements.txt              # Standardized package dependencies
├── .env.example                  # Environment variable configuration template
├── README.md                     # Documentation
├── assets/
│   └── style.css                 # Advanced Sci-Fi dark theme styling system
├── modules/
│   ├── __init__.py
│   ├── document_parser.py        # PDF, DOCX, TXT, and Source Code text extraction
│   ├── question_engine.py        # Gemini: question generation & submission summaries
│   ├── viva_engine.py            # Gemini: step-by-step adaptive answer scoring
│   ├── scoring_engine.py         # Gemini: consolidated final integrity audits
│   ├── voice_engine.py           # TTS question player (gTTS)
│   └── analytics.py              # Answering speeds, word counts, and progression curves
└── utils/
    ├── __init__.py
    └── prompts.py                # Fully optimized, robust LLM JSON templates
```

---

## 🔧 Installation & Setup

### Option A: Standard Run (Using Gemini API)
1. **Clone/Move** to the `authentilearn` directory.
2. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```
3. **Supply your Google AI API key**:
   Open `.env` and fill in `GOOGLE_API_KEY` (Get a free key from [Google AI Studio](https://aistudio.google.com)).
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Start Streamlit App**:
   ```bash
   streamlit run app.py
   ```

### Option B: Quick Hackathon Demo (No Setup Needed!)
1. Keep the **Demo Mode (No API Key)** toggle active in the sidebar.
2. Select any of the **Demo Samples** in Stage 1 (e.g., Python ML Code).
3. Press **Start AI Analysis & Generate Questions**.
4. Enjoy the full interactive 5-question viva interface, speech output, and advanced Plotly dashboards entirely offline with **zero API calls**!

---

## 🌿 Version Control (GitHub Practices)
This project follows strict version control practices to ensure stability and seamless collaboration:
- **Main Branch (`main`)**: Always contains the production-ready code. Commits to `main` must pass all tests.
- **Feature Branches**: All new development (e.g., adding a new module or UI changes) should occur on separate branches (e.g., `feature/voice-synthesis`).
- **Commit Messages**: Follow standard conventional commits. E.g., `feat: added adaptive follow-ups`, `fix: resolved API key environment loading`.
- **Pull Requests (PRs)**: PRs must be used to merge feature branches into `main`. Ensure documentation (`README.md`) is updated if structural changes are made.
- **Ignored Files**: The `.gitignore` file strictly prohibits committing `.env` credentials, `__pycache__` directories, and local `.db` databases to maintain security.
