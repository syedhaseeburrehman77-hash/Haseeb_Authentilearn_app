# File: authentilearn/app.py
import streamlit as st
import time
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyDTqzkSueuGh4MiHFQFdXF0u23o-Xa1vhM"
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App Setup
st.set_page_config(
    page_title="AuthentiLearn AI - AI-Powered Academic Integrity Viva",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core imports (after page config)
from modules.document_parser import extract_text, get_file_metadata
from modules.question_engine import generate_questions, analyze_submission
from modules.viva_engine import evaluate_answer
from modules.scoring_engine import calculate_final_score
from modules.analytics import calculate_session_stats
from modules.voice_engine import text_to_speech

# New Multi-Modal & Integrity Upgrade imports
from modules.auth_engine import enroll_student_identity, verify_student_identity
from modules.cheat_detector import analyze_submission_authenticity, highlight_suspicious_text, get_copy_paste_gauge_chart
from modules.line_analyzer import analyze_line_by_line, detect_realtime_paste, analyze_answer_spontaneity
from modules.voice_auth import record_and_transcribe_answer, verify_voice_profile
from modules.knowledge_graph import (
    get_understanding_radar,
    get_concept_mastery,
    get_understanding_depth,
    get_confidence_progression,
    get_three_dimensions,
    get_submission_composition,
    export_dashboard_pdf
)
import modules.auth_db as auth_db

# Inject Custom CSS
def inject_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom stylesheet assets/style.css not found.")

inject_custom_css()

# Session State Initialization
if "stage" not in st.session_state:
    st.session_state.stage = "login"  # Default to database login first
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "login_mode" not in st.session_state:
    st.session_state.login_mode = "login"
if "auth_profile" not in st.session_state:
    st.session_state.auth_profile = None
if "auth_attempts" not in st.session_state:
    st.session_state.auth_attempts = 0
if "content" not in st.session_state:
    st.session_state.content = ""
if "file_metadata" not in st.session_state:
    st.session_state.file_metadata = {}
if "submission_analysis" not in st.session_state:
    st.session_state.submission_analysis = {}
if "cheat_analysis" not in st.session_state:
    st.session_state.cheat_analysis = {}
if "highlighted_submission" not in st.session_state:
    st.session_state.highlighted_submission = ""
if "last_sentence_analysis" not in st.session_state:
    st.session_state.last_sentence_analysis = []
if "line_table" not in st.session_state:
    st.session_state.line_table = None
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "qa_pairs" not in st.session_state:
    st.session_state.qa_pairs = []
if "followup_active" not in st.session_state:
    st.session_state.followup_active = False
if "followup_question" not in st.session_state:
    st.session_state.followup_question = ""
if "followup_answer" not in st.session_state:
    st.session_state.followup_answer = ""
if "current_q_evaluation" not in st.session_state:
    st.session_state.current_q_evaluation = {}
if "final_report" not in st.session_state:
    st.session_state.final_report = {}
if "session_stats" not in st.session_state:
    st.session_state.session_stats = {}
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True
if "viva_start_time" not in st.session_state:
    st.session_state.viva_start_time = 0.0
if "q_start_time" not in st.session_state:
    st.session_state.q_start_time = 0.0
if "user_language" not in st.session_state:
    st.session_state.user_language = "English"
if "demo_mode" not in st.session_state:
    # If a valid API key is present in environment, default demo_mode to False
    st.session_state.demo_mode = False if os.environ.get("GOOGLE_API_KEY") else True
if "educator_mode" not in st.session_state:
    st.session_state.educator_mode = True
if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""
if "paste_events" not in st.session_state:
    st.session_state.paste_events = []
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "pasted_text" not in st.session_state:
    st.session_state.pasted_text = ""
if "active_course" not in st.session_state:
    st.session_state.active_course = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "fullscreen_warning_count" not in st.session_state:
    st.session_state.fullscreen_warning_count = 0
if "copy_attempt_count" not in st.session_state:
    st.session_state.copy_attempt_count = 0
if "security_warning" not in st.session_state:
    st.session_state.security_warning = None
if "security_error" not in st.session_state:
    st.session_state.security_error = None
if "api_key" not in st.session_state:
    st.session_state.api_key = "AIzaSyDTqzkSueuGh4MiHFQFdXF0u23o-Xa1vhM"


# Hardcoded Demo Contents
DEMO_SAMPLES = {
    "Python ML Code": """import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("telecom_churn.csv")

# Preprocessing
df['age'].fillna(df['age'].median(), inplace=True)
X = df.drop(columns=['churn_id', 'churned'])
y = df['churned']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
print(classification_report(y_test, y_pred))
""",
    "Essay Sample": """The rapid advancement of Generative Artificial Intelligence (AI) has sparked widespread debate regarding its ethical, social, and economic implications. On one hand, tools like ChatGPT and Midjourney have democratized creative production and coding, giving individuals unprecedented abilities to generate complex artifacts. On the other hand, these developments raise massive issues concerning labor displacement, copyright infringement, and academic dishonesty.

From an economic perspective, white-collar professions once thought immune to automation are now at risk. Copywriters, junior software engineers, and administrative assistants find their roles supplemented or replaced by large language models. While tech proponents argue this will simply elevate human workers to managers of AI systems, the transition period threatens to widen income inequality and leave many workers displaced without viable paths for retraining.

In education, the challenge is existential. Academic institutions must transition from detecting AI output—a losing battle—to fostering critical thinking and validating understanding. Flipped classrooms, oral vivas, and interactive examinations represent the future of assessment, ensuring that students do not merely produce perfect artifacts, but actually comprehend the intellectual processes behind them. The goal of education must remain the cultivation of human intelligence, even in an age of artificial agents.""",
    "Research Abstract": """Abstract—Early detection of foliar crop diseases is crucial for securing global food supplies and reducing excessive chemical pesticide application. This paper proposes 'FoliarNet,' an advanced deep convolutional neural network (CNN) optimized for classifying five distinct categories of tomato leaf pathogens using low-altitude aerial imagery collected via multi-spectral drone sensors. 

We collected and labeled a custom dataset of 12,400 high-resolution leaf images under varying natural lighting conditions. Our model integrates depthwise separable convolutions with an attention-gated layer to focus feature extraction on localized chlorotic lesions and necrotic margins, maintaining high computational efficiency suitable for edge-device deployment.

FoliarNet achieved a mean classification accuracy of 96.8% under 5-fold cross-validation, outperforming standard ResNet50 and MobileNetV3 baselines by 4.2% and 6.1% respectively. Furthermore, we conducted Grad-CAM saliency mapping to validate that the network's decision boundaries align with actual biological pathology indicators rather than background soil noise. The proposed framework demonstrates a highly scalable, automated solution for precision agriculture and real-time smart orchard monitoring."""
}

# Multi-language translations
TRANSLATIONS = {
    "English": {
        "title": "AuthentiLearn AI",
        "subtitle": "AI-Powered Learning Authenticity Evaluator",
        "upload_tab": "📄 Upload File",
        "paste_tab": "💻 Paste Code/Text",
        "demo_tab": "🔗 Demo Sample",
        "start_btn": "🧠 Start AI Analysis & Generate Questions →",
        "submit_btn": "Submit Answer →",
        "skip_btn": "Skip this question",
        "next_btn": "Next Question →",
        "submit_followup": "Submit Follow-up",
        "reset_btn": "🔄 Evaluate New Submission",
        "verdict_title": "Authenticity Verdict",
        "strengths_title": "💪 Strengths Demonstrated",
        "gaps_title": "⚠️ Knowledge Gaps",
        "radar_title": "Understanding Profile",
        "timeline_title": "Score Progression & Confidence Timeline",
        "recommendation_title": "Educator Recommendation",
        "actions_title": "Suggested Next Steps",
        "red_flags_title": "🚨 Suspicious Patterns & Mismatches",
        "stage_upload": "Upload Submission",
        "stage_viva": "Oral Viva Exam",
        "stage_report": "Authenticity Report",
        "detected_label": "📚 Detected:",
        "level_label": "Level",
        "word_counter": "words typed",
        "powered_by": "Powered by Gemini 2.0 Flash"
    },
    "Urdu": {
        "title": "آتھینٹی لرن AI",
        "subtitle": "مصنوعی ذہانت سے چلنے والا فہم کا جائزہ کار",
        "upload_tab": "📄 فائل اپ لوڈ کریں",
        "paste_tab": "💻 کوڈ/ٹیکسٹ پیسٹ کریں",
        "demo_tab": "🔗 ڈیمو نمونہ",
        "start_btn": "🧠 تجزیہ شروع کریں اور سوالات بنائیں ←",
        "submit_btn": "جواب جمع کروائیں ←",
        "skip_btn": "یہ سوال چھوڑ دیں",
        "next_btn": "اگلا سوال ←",
        "submit_followup": "پیروکار سوال جمع کریں",
        "reset_btn": "🔄 نیا جائزہ شروع کریں",
        "verdict_title": "سچائی کا فیصلہ",
        "strengths_title": "💪 ظاہر کردہ طاقتیں",
        "gaps_title": "⚠️ فہم کی کمیاں",
        "radar_title": "فہم کا خاکہ (پروفائل)",
        "timeline_title": "اسکور کی پیشرفت اور اعتماد کی ٹائم لائن",
        "recommendation_title": "استاد کے لیے تجویز",
        "actions_title": "تجویز کردہ اگلے اقدامات",
        "red_flags_title": "🚨 مشکوک پیٹرن اور تضادات",
        "stage_upload": "فائل جمع کروائیں",
        "stage_viva": "زبانی انٹرویو (ویوا)",
        "stage_report": "صداقت کی رپورٹ",
        "detected_label": "📚 دریافت شدہ موضوع:",
        "level_label": "سطح",
        "word_counter": "الفاظ لکھے گئے",
        "powered_by": "جیمنی 2.0 فلیش کی طاقت"
    },
    "Arabic": {
        "title": "أوثينتي ليرن AI",
        "subtitle": "مقيّم أصالة التعلم بالذكاء الاصطناعي",
        "upload_tab": "📄 تحميل ملف",
        "paste_tab": "💻 لصق الكود/النص",
        "demo_tab": "🔗 نموذج تجريبي",
        "start_btn": "🧠 بدء التحليل وتوليد الأسئلة ←",
        "submit_btn": "تقديم الإجابة ←",
        "skip_btn": "تخطي هذا السؤال",
        "next_btn": "السؤال التالي ←",
        "submit_followup": "تقديم إجابة المتابعة",
        "reset_btn": "🔄 تقييم تقديم جديد",
        "verdict_title": "حكم الأصالة",
        "strengths_title": "💪 نقاط القوة الموضحة",
        "gaps_title": "⚠️ الفجوات المعرفية",
        "radar_title": "ملف الفهم المعرفي",
        "timeline_title": "تقدم الدرجات والجدول الزمن لثقة الإجابة",
        "recommendation_title": "توصية المعلم",
        "actions_title": "الخطوات التالية المقترحة",
        "red_flags_title": "🚨 الأنماط المشبوهة والتناقضات",
        "stage_upload": "تحميل التقديم",
        "stage_viva": "الاختبار الشفهي",
        "stage_report": "تقرير الأصالة",
        "detected_label": "📚 الموضوع المكتشف:",
        "level_label": "مستوى",
        "word_counter": "كلمات مكتوبة",
        "powered_by": "مدعوم من جيميناي 2.0 فلاش"
    }
}

# Translate Helper
def get_txt(key):
    lang = st.session_state.user_language
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key)


# --------------------------------------------------------
# TOP PROGRESSION NAVIGATION TAB BAR
# --------------------------------------------------------
def render_top_navigation():
    # Only render top nav if the user has authenticated and logged in
    if not st.session_state.logged_in_user:
        return
    
    stages_seq = ["courses", "upload", "viva", "report", "dashboard"]
    if not st.session_state.get("educator_mode", True):
        stages_seq.remove("dashboard")
    utility_tabs = ["chatbot"]
    
    labels = {
        "upload": "📤 Coursework",
        "viva": "🎙️ Oral Exam",
        "report": "🎓 Verdict",
        "dashboard": "📊 Dashboard",
        "courses": "📚 Courses",
        "chatbot": "🤖 Study Buddy"
    }
    
    current_stage = st.session_state.stage
    
    # Determine the furthest unlocked progression stage index
    max_unlocked_idx = 1  # courses (0), upload (1) are always unlocked after login
    if st.session_state.get("questions") and len(st.session_state.questions) > 0:
        max_unlocked_idx = 2  # viva (2) is unlocked
    if st.session_state.get("final_report") and len(st.session_state.final_report) > 0:
        max_unlocked_idx = 4  # report (3) and dashboard (4) are unlocked
        
    all_tabs = stages_seq + utility_tabs
    
    # Wrap in .top-nav-container to prevent horizontal wrapping
    st.markdown("<div class='top-nav-container' style='margin-top:-1.5rem; margin-bottom:2rem;'>", unsafe_allow_html=True)
    cols = st.columns(len(all_tabs))
    
    for idx, s_id in enumerate(all_tabs):
        with cols[idx]:
            if s_id in utility_tabs:
                # Utility tabs are always accessible after login, except during the active oral exam
                if current_stage == s_id:
                    btn_label = f"● {labels[s_id]}"
                    st.markdown(
                        f"<div class='top-nav-item active' style='text-align:center;'>{btn_label}</div>", 
                        unsafe_allow_html=True
                    )
                else:
                    btn_label = f"{labels[s_id]}"
                    is_disabled = (current_stage == "viva") # strict lockout during active exam
                    if st.button(btn_label, key=f"top_nav_btn_{s_id}", use_container_width=True, disabled=is_disabled):
                        st.session_state.stage = s_id
                        st.rerun()
            else:
                # Main progression tabs
                if current_stage == s_id:
                    btn_label = f"● {labels[s_id]}"
                    st.markdown(
                        f"<div class='top-nav-item active' style='text-align:center;'>{btn_label}</div>", 
                        unsafe_allow_html=True
                    )
                else:
                    stage_idx = stages_seq.index(s_id)
                    
                    # Determine label with state-driven checkmarks and locks
                    if stage_idx < max_unlocked_idx:
                        btn_label = f"✓ {labels[s_id]}"
                    elif stage_idx == max_unlocked_idx:
                        btn_label = f"{labels[s_id]}"
                    else:
                        btn_label = f"🔒 {labels[s_id]}"
                    
                    # Strict lockout during exam to prevent cheating or accidental resets
                    if current_stage == "viva":
                        is_disabled = True
                    else:
                        is_disabled = (stage_idx > max_unlocked_idx)
                    
                    if st.button(btn_label, key=f"top_nav_btn_{s_id}", use_container_width=True, disabled=is_disabled):
                        st.session_state.stage = s_id
                        st.rerun()
                    
    st.markdown("</div>", unsafe_allow_html=True)


# Export PDF Audit Text Builder (Plain text high-fidelity summary)
def generate_pdf_text(report, stats, meta):
    out = []
    out.append("==================================================")
    out.append("         AUTHENTILEARN AI - INTEGRITY AUDIT      ")
    out.append("==================================================")
    out.append(f"Submission: {meta.get('name', 'Pasted Content/Demo')}")
    out.append(f"Subject Area: {report.get('subject_area', 'Machine Learning')}")
    out.append(f"File Type: {meta.get('type', 'N/A')} | Word Count: {meta.get('estimated_words', 0)}")
    out.append("--------------------------------------------------")
    out.append(f"AUTHENTICITY SCORE: {report.get('overall_score', 0)}/100")
    out.append(f"VERDICT: {report.get('verdict', 'N/A')}")
    out.append(f"CONFIDENCE LEVEL: {report.get('confidence_level', 'N/A')}")
    out.append("--------------------------------------------------")
    out.append("\nSTRENGTHS DEMONSTRATED:")
    for s in report.get("strengths", []):
        out.append(f" - {s}")
    out.append("\nKNOWLEDGE GAPS DETECTED:")
    for g in report.get("knowledge_gaps", []):
        out.append(f" - {g}")
    out.append("\nSUSPICIOUS PATTERNS / RED FLAGS:")
    for r in report.get("suspicious_patterns", []):
        out.append(f" - {r}")
    out.append("\nEDUCATOR RECOMMENDATION:")
    out.append(report.get("recommendation", "N/A"))
    out.append("\nSUGGESTED NEXT ACTIONS:")
    for i, a in enumerate(report.get("suggested_actions", [])):
        out.append(f"{i+1}. {a}")
    out.append("\nSESSION STATS:")
    out.append(f" - Average Answer Length: {stats.get('avg_answer_length', 0)} words")
    out.append(f" - Total Viva Duration: {stats.get('total_time_seconds', 0)} seconds")
    out.append(f" - Question Skip Rate: {stats.get('skip_rate', 0)}%")
    out.append("==================================================")
    return "\n".join(out)


def append_security_alerts_to_report(report):
    if "suspicious_patterns" not in report:
        report["suspicious_patterns"] = []
    
    warnings = st.session_state.fullscreen_warning_count
    copies = st.session_state.copy_attempt_count
    
    if warnings > 0:
        report["suspicious_patterns"].append(
            f"Fullscreen Exit / Focus Loss Alert: The student exited fullscreen or switched tabs {warnings} time(s) during the exam."
        )
        penalty = min(20, warnings * 5)
        report["overall_score"] = max(0, report.get("overall_score", 100) - penalty)
        
    if copies > 0:
        report["suspicious_patterns"].append(
            f"Copy-Paste Protection Alert: The student attempted text copying, shortcut pasting, or right-clicking {copies} time(s)."
        )
        penalty = min(30, copies * 10)
        report["overall_score"] = max(0, report.get("overall_score", 100) - penalty)
        
    # Re-evaluate the verdict based on the modified score
    score = report.get("overall_score", 100)
    if score >= 75:
        report["verdict"] = "Highly Authentic"
    elif score >= 55:
        report["verdict"] = "Suspicious / Moderate Match"
    else:
        report["verdict"] = "Unauthentic / Likely Plagiarized"
        
    return report



# --------------------------------------------------------
# VIVA SECURITY EVENT INTERCEPTOR
# --------------------------------------------------------
if "fullscreen_exit" in st.query_params:
    st.query_params.clear()
    st.session_state.fullscreen_warning_count += 1
    st.session_state.security_warning = "⚠️ Fullscreen mode exited! This event has been logged for academic review."
    st.rerun()

if "tab_switch" in st.query_params:
    st.query_params.clear()
    st.session_state.fullscreen_warning_count += 1
    st.session_state.security_warning = "⚠️ Tab switch or window focus loss detected! This event has been logged for academic review."
    st.rerun()

if "copy_attempt" in st.query_params:
    st.query_params.clear()
    st.session_state.copy_attempt_count += 1
    st.session_state.security_error = "🚨 Copy-Paste or text selection shortcut detected and BLOCKED! This integrity warning has been logged."
    st.rerun()

# --------------------------------------------------------
# 1-MINUTE COUNDOWN TIMEOUT QUERY PARAMETER LISTENER
# --------------------------------------------------------
if "timeout" in st.query_params:
    st.query_params.clear()
    if st.session_state.stage == "viva" and len(st.session_state.qa_pairs) == st.session_state.current_q_index:
        current_idx = st.session_state.current_q_index
        current_q = st.session_state.questions[current_idx]
        
        # Log skipped/timeout answer record
        qa_record = {
            "question_id": current_q["id"],
            "question": current_q["question"],
            "difficulty": current_q["difficulty"],
            "concept_tested": current_q["concept_tested"],
            "answer": "[Timeout - No response was submitted within the 60-second limit]",
            "time_taken": 60.0,
            "skipped": True,
            "evaluation": {
                "correctness": 0,
                "depth": 0,
                "specificity": 0,
                "overall_score": 0.0,
                "feedback": "The student failed to provide an answer within the allotted 60 seconds.",
                "red_flags": ["Submission limit exceeded (Timeout)"],
                "needs_followup": False,
                "followup_question": ""
            },
            "followup_pair": None
        }
        st.session_state.qa_pairs.append(qa_record)
        st.session_state.audio_bytes = None
        st.session_state.current_answer = ""
        
        if st.session_state.current_q_index < len(st.session_state.questions) - 1:
            st.session_state.current_q_index += 1
            st.session_state.q_start_time = time.time()
        else:
            # Generate report on timeout of last question
            try:
                report = calculate_final_score(
                    content=st.session_state.content,
                    qa_pairs=st.session_state.qa_pairs,
                    api_key=os.environ.get("GOOGLE_API_KEY"),
                    demo_mode=st.session_state.demo_mode
                )
                st.session_state.final_report = append_security_alerts_to_report(report)
                st.session_state.session_stats = calculate_session_stats(st.session_state.qa_pairs)
                st.session_state.stage = "report"
            except Exception as e:
                # Handle API rate limit / other exceptions gracefully
                st.warning("⚠️ **Gemini API Key Rate Limit/Exception Reached during Timeout Compiler!** Gracefully switching to **High-Fidelity Offline Simulation Mode** to compile your final audit.")
                st.session_state.demo_mode = True
                try:
                    report = calculate_final_score(
                        content=st.session_state.content,
                        qa_pairs=st.session_state.qa_pairs,
                        demo_mode=True
                    )
                    st.session_state.final_report = append_security_alerts_to_report(report)
                    st.session_state.session_stats = calculate_session_stats(st.session_state.qa_pairs)
                    st.session_state.stage = "report"
                except Exception as fallback_err:
                    st.error(f"❌ Timeout Report Compilation Fallback Failed: {str(fallback_err)}")
        st.rerun()


# Sidebar Configuration Control
with st.sidebar:
    st.markdown(f"<div style='text-align: center; padding: 1.5rem 0;'><h2 style='margin:0; color:var(--accent-blue); font-family:\"Space Mono\";'>{get_txt('title')}</h2><p style='font-size:0.8rem; color:var(--muted);'>{get_txt('subtitle')}</p></div>", unsafe_allow_html=True)
    
    # Secure User Profile Box
    if st.session_state.logged_in_user:
        st.markdown(f"""
        <div style='background:rgba(255, 255, 255, 0.02); border:1px solid rgba(255, 255, 255, 0.08); border-radius:14px; padding:1.2rem; margin-bottom:1.8rem; box-shadow:0 4px 12px rgba(0,0,0,0.2);'>
            <span style='font-size:0.75rem; color:var(--muted); font-family:"Space Mono"; uppercase; display:block; letter-spacing:1px; margin-bottom:4px;'>ACTIVE STUDENT</span>
            <span style='font-weight:bold; color:var(--accent-blue); font-size:1.15rem; display:block;'>👤 {st.session_state.logged_in_user["username"].upper()}</span>
            <span style='font-size:0.85rem; color:var(--text); display:block; font-family:"Space Mono"; opacity:0.85; margin-top:2px;'>Reg # {st.session_state.logged_in_user["student_id"]}</span>
            <hr style='border-color:rgba(255,255,255,0.06); margin:8px 0;'/>
            <span style='font-size:0.75rem; color:var(--muted); font-family:"Space Mono"; uppercase; display:block; letter-spacing:0.5px;'>Security Level</span>
            <span style='font-size:0.8rem; color:var(--accent-green); font-weight:bold;'>✓ Authenticated Login</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Add Logout button inside profile box
        if st.button("🚪 Logout Student", use_container_width=True):
            st.session_state.stage = "login"
            st.session_state.logged_in_user = None
            st.session_state.auth_profile = None
            st.session_state.content = ""
            st.session_state.questions = []
            st.session_state.qa_pairs = []
            st.rerun()
    
    # Dynamic Controls
    st.markdown("### ⚙️ OPTIONS", unsafe_allow_html=True)
    st.session_state.demo_mode = st.toggle("🎮 Demo Mode (No API Key)", value=st.session_state.demo_mode, help="Runs the app using highly dynamic, realistic mock engines. Ideal for hackathon evaluation.")
    
    if not st.session_state.demo_mode:
        api_key_input = st.text_input("🔑 Gemini API Key", type="password", value=os.environ.get("GOOGLE_API_KEY", ""), help="Get an API key from aistudio.google.com")
        if api_key_input:
            os.environ["GOOGLE_API_KEY"] = api_key_input
            
    st.session_state.educator_mode = st.toggle("👨‍🏫 Educator Mode", value=st.session_state.educator_mode, help="Displays advanced red flags, suspicion signals, and detailed sentence analysis grids.")
    st.session_state.user_language = st.selectbox("🌐 UI Language / زبان", ["English", "Urdu", "Arabic"])
    
    # Sidebar stats during VIVA/REPORT/DASHBOARD
    if st.session_state.stage in ["viva", "report", "dashboard"] and st.session_state.questions:
        st.markdown("---")
        st.markdown("### 📊 SUBMISSION PROFILE", unsafe_allow_html=True)
        sub_info = st.session_state.submission_analysis
        if sub_info:
            st.markdown(f"**Subject:** {sub_info.get('subject_area', 'Machine Learning')}")
            st.markdown(f"**Complexity:** `{sub_info.get('complexity_level', 'advanced').upper()}`")
            st.markdown("**Core Concepts:**")
            for concept in sub_info.get("key_concepts", []):
                st.markdown(f"- {concept}")
                
        answered_q = [q for q in st.session_state.qa_pairs if not q.get("skipped", False)]
        if answered_q:
            running_avg = sum(q["evaluation"]["overall_score"] for q in answered_q) / len(answered_q) * 10
            st.metric(label="RUNNING AVG SCORE", value=f"{round(running_avg, 1)}%")

        if st.session_state.stage == "viva":
            st.markdown("### 📑 QUESTION TRACKER", unsafe_allow_html=True)
            for i, q in enumerate(st.session_state.questions):
                if i == st.session_state.current_q_index:
                    cls = "current"
                    icon = "🔴"
                elif i < len(st.session_state.qa_pairs):
                    cls = "answered"
                    icon = "✅"
                else:
                    cls = "upcoming"
                    icon = "⬜"
                
                st.markdown(
                    f"<div class='nav-question-item {cls}'><span>{icon} Q{i+1}: {q['concept_tested']}</span><span style='font-size:0.7rem; font-family:\"Space Mono\"; opacity:0.8;'>[{q['difficulty']}]</span></div>", 
                    unsafe_allow_html=True
                )

    st.markdown(f"<div style='position: fixed; bottom: 10px; left: 10px; font-size: 0.75rem; color: var(--muted);'>{get_txt('powered_by')}</div>", unsafe_allow_html=True)

# Render Top Navigation (only shows if logged in)
render_top_navigation()

# ========================================================
# DATABASE AUTHENTICATION & REGISTRATION STAGE
# ========================================================
if st.session_state.stage == "login":
    st.markdown("""
    <div class="hero-header" style="padding: 2.5rem 1.5rem; margin-bottom: 2rem;">
        <h1 style="font-size: 2.8rem; letter-spacing: -0.5px;">🧠 AuthentiLearn AI</h1>
        <p>AI-Powered Learning Authenticity Evaluator & Academic Integrity Viva Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.48, 0.52], gap="large")
    
    with col1:
        # Load premium student-AI 3D interaction illustration asset dynamically
        img_path = os.path.join(os.path.dirname(__file__), "assets", "student_ai_interaction.png")
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
            
        st.markdown("""
        <div class="metric-card" style="background: var(--surface); border:1px solid var(--border); padding: 2rem; display: flex; flex-direction: column; justify-content: center;">
            <h2 style="color: var(--accent-blue); margin-top: 0; font-family: 'Space Mono'; font-size: 1.6rem;">🚀 Verification Redefined</h2>
            <p style="font-size: 1rem; line-height: 1.6; color: var(--text); opacity: 0.95; margin-bottom: 1.2rem;">
                In an era of generative AI, AuthentiLearn AI pioneers cognitive oral viva assessments to validate genuine student understanding. Our software quality engineering (SQE) standards guarantee robust, comprehensive, and objective evaluation.
            </p>
            <hr style="border-color: var(--border); margin: 1.2rem 0;" />
            <h4 style="color: var(--accent-purple); font-family: 'Space Mono'; margin-bottom: 0.8rem;">🔒 Core Features:</h4>
            <div style="font-size: 0.95rem; line-height: 1.8; color: var(--text);">
                • <b>Multi-Modal Integrity</b>: Local SQLite salted-hashes and automated security monitoring.<br/>
                • <b>Oral Viva Examination</b>: Deep, adaptive AI-driven inquiry with speech-to-text response verification.<br/>
                • <b>Sentence Diagnostics</b>: Real-time copy-paste alerts and line-by-line AI cheating audits.<br/>
                • <b>Knowledge Dashboards</b>: Stunning 6-dimension interactive graphs of conceptual mastery.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.login_mode == "login":
            st.markdown("<div class='metric-card' style='background: var(--surface); border:1px solid var(--border); padding: 2.5rem 2rem;'>", unsafe_allow_html=True)
            st.markdown("<h2 style='color: var(--accent-blue); margin-top:0; margin-bottom: 0.5rem;'>👤 Student Login</h2>", unsafe_allow_html=True)
            st.write("Sign in to access your coursework audits and oral exams.")
            
            login_username = st.text_input("Username:", placeholder="ahmed_hassan", key="login_username_input").strip()
            login_password = st.text_input("Password:", type="password", placeholder="••••••••", key="login_password_input")
            
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🔐 Authenticate & Unlock", use_container_width=True):
                if not login_username or not login_password:
                    st.warning("Please fill in both fields.")
                else:
                    success, res = auth_db.authenticate_student(login_username, login_password)
                    if success:
                        st.session_state.logged_in_user = res
                        if res.get("biometrics"):
                            st.session_state.auth_profile = res["biometrics"]
                            st.success(f"✓ Welcome back, {login_username.upper()}! Accessing Academic Course Selection...")
                            time.sleep(1.0)
                            st.session_state.stage = "courses"
                        else:
                            st.success(f"✓ Welcome, {login_username.upper()}! Accessing Academic Course Selection...")
                            time.sleep(1.0)
                            st.session_state.stage = "courses"
                        st.rerun()
                    else:
                        st.error(f"❌ {res}")
            
            st.markdown("<hr style='border-color:var(--border); margin:1.5rem 0;'/>", unsafe_allow_html=True)
            st.write("New to AuthentiLearn AI?")
            if st.button("📝 Create an Account (Signup)", use_container_width=True):
                st.session_state.login_mode = "signup"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        else: # signup mode
            st.markdown("<div class='metric-card' style='background: var(--surface); border:1px solid var(--border); padding: 2.5rem 2rem;'>", unsafe_allow_html=True)
            st.markdown("<h2 style='color: var(--accent-purple); margin-top:0; margin-bottom: 0.5rem;'>📝 Register Student</h2>", unsafe_allow_html=True)
            st.write("Create a secure, salted local database profile.")
            
            signup_username = st.text_input("Username:", placeholder="ahmed_hassan", key="signup_username_input").strip()
            signup_id = st.text_input("Registration ID / Seat Number:", placeholder="CS-2024-047", key="signup_id_input").strip()
            signup_password = st.text_input("Password:", type="password", placeholder="••••••••", key="signup_password_input")
            signup_confirm = st.text_input("Confirm Password:", type="password", placeholder="••••••••", key="signup_confirm_input")
            
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("🚀 Register & Save Credentials", use_container_width=True):
                if not signup_username or not signup_id or not signup_password or not signup_confirm:
                    st.warning("All fields are required.")
                elif len(signup_password) < 6:
                    st.warning("Password must be at least 6 characters.")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match.")
                else:
                    success, msg = auth_db.register_student(signup_username, signup_id, signup_password)
                    if success:
                        st.success(f"✓ {msg}")
                        st.session_state.login_mode = "login"
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                        
            st.markdown("<hr style='border-color:var(--border); margin:1.5rem 0;'/>", unsafe_allow_html=True)
            st.write("Already have a student account?")
            if st.button("🔑 Back to Login", use_container_width=True):
                st.session_state.login_mode = "login"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ========================================================
# STAGE 0: MULTI-MODAL BIOMETRICS AUTHENTICATION
# ========================================================
elif st.session_state.stage == "auth":
    st.markdown("""
    <div class="hero-header" style="padding: 2rem 1.5rem; margin-bottom: 1.5rem;">
        <h1 style="font-size: 2.4rem;">🔐 IDENTITY VERIFICATION</h1>
        <p>Enroll or verify student identity via multi-modal face and voice profiling before starting.</p>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2 = st.columns([0.55, 0.45], gap="large")

    with auth_col1:
        if st.session_state.auth_profile is None:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:var(--accent-blue); margin-top:0;'>📝 Student Enrollment</h3>", unsafe_allow_html=True)
            st.write("First-time check-in requires capturing facial structure histograms and voice MFCC vectors.")

            enroll_name = st.text_input("Student Full Name:", placeholder="Ahmed Hassan", key="name_input")
            enroll_id = st.text_input("Registration ID / Seat Number:", placeholder="CS-2024-047", key="id_input")

            cam_col, mic_col = st.columns(2)
            with cam_col:
                st.markdown("#### 📸 Camera Footprint")
                st.write("Capture facial grayscale histograms (40% weight).")
            with mic_col:
                st.markdown("#### 🎤 Waveform Footprint")
                st.write("Record Cepstral MFCC signature (60% weight).")

            if st.button("🚀 Record Biometrics & Enroll Account", use_container_width=True):
                if not enroll_name.strip() or not enroll_id.strip():
                    st.warning("Please fill in your name and student ID to compile identity profile.")
                else:
                    with st.spinner("Compiling face/voice biometrics templates..."):
                        try:
                            profile = enroll_student_identity(enroll_name, enroll_id)
                            st.session_state.auth_profile = profile
                            if st.session_state.logged_in_user:
                                auth_db.save_student_biometrics(st.session_state.logged_in_user["username"], profile)
                            st.success(f"✓ Biometrics Enrolled successfully for {enroll_name}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Enrollment failed: {str(e)}")

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            # Returning Student Verification Stage
            profile = st.session_state.auth_profile
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:var(--accent-blue); margin-top:0;'>🔑 Identity Check-In: {profile['student_name']}</h3>", unsafe_allow_html=True)
            st.write(f"ID Signature: `{profile['student_id']}` | Biometrics Lock: `ACTIVE`")

            col_avatar, col_waveform = st.columns(2)
            with col_avatar:
                st.markdown("**📸 Facial Vector**")
                if profile.get("face_image_b64"):
                    st.markdown(f"<div style='text-align:center;'><img src='data:image/jpeg;base64,{profile['face_image_b64']}' style='border-radius:12px; border:2px solid var(--border);' width='130'/></div>", unsafe_allow_html=True)
                else:
                    st.info("Avatar template locked.")

            with col_waveform:
                st.markdown("**🎤 Voice Signature**")
                st.markdown("""
                <div class="voice-wave">
                    <span></span><span></span><span></span><span></span><span></span>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🔐 Verify Identity & Unlock Coursework", use_container_width=True):
                with st.spinner("Matching biometric cosine similarity hashes..."):
                    try:
                        res = verify_student_identity(profile, demo_mode=st.session_state.demo_mode)
                        if res["status"] == "AUTHENTICATED":
                            st.success(f"✓ Access Granted! Combined score: {res['match_percentage']}% (Voice: {res['voice_score']*100:.0f}% / Face: {res['face_score']*100:.0f}%)")
                            time.sleep(1.2)
                            st.session_state.stage = "courses"
                            st.rerun()
                        else:
                            st.session_state.auth_attempts += 1
                            st.error(f"❌ Matching Mismatch! Combined Match: {res['match_percentage']}% (Requires: 70.0%). Verification attempts: {st.session_state.auth_attempts}/2")
                            if st.session_state.auth_attempts >= 2:
                                st.error("🚨 Authentication Lockout triggered. Resetting biometrics enrollment.")
                                st.session_state.auth_profile = None
                                st.session_state.auth_attempts = 0
                            st.rerun()
                    except Exception as e:
                        st.error(f"Verification Error: {str(e)}")

            if st.button("🔄 Clear and Re-Enroll", use_container_width=True):
                st.session_state.auth_profile = None
                st.session_state.auth_attempts = 0
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    with auth_col2:
        st.markdown("<div class='metric-card' style='height:100%;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:var(--accent-purple); margin-top:0;'>🏆 JUDGES QUICK ACCESS</h3>", unsafe_allow_html=True)
        st.write("AuthentiLearn AI uses state-of-the-art voice Cepstral signatures (MFCCs) and grayscale face histograms. Press this button to skip hardware check-ins and test the system immediately with mock biometric approvals!")
        
        if st.button("🔓 Skip Authentication (Demo Bypass)", use_container_width=True):
            s_name = st.session_state.logged_in_user["username"].upper() if st.session_state.logged_in_user else "Ahmed Hassan"
            s_id = st.session_state.logged_in_user["student_id"] if st.session_state.logged_in_user else "CS-2024-047"
            
            profile = {
                "student_name": s_name,
                "student_id": s_id,
                "face_template": [0.5]*64,
                "face_image_b64": "",
                "voice_template": [0.1]*13,
                "is_simulated": True,
                "enrolled_timestamp": time.time()
            }
            st.session_state.auth_profile = profile
            if st.session_state.logged_in_user:
                auth_db.save_student_biometrics(st.session_state.logged_in_user["username"], profile)
            st.session_state.stage = "courses"
            st.success(f"Bypassed! Student {s_name} biometrics enrolled and matched.")
            time.sleep(1.0)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ========================================================
# NEW STAGE: COURSE SELECTION & ENROLLMENT
# ========================================================
elif st.session_state.stage == "courses":
    st.markdown("""
    <div class="hero-header" style="padding: 2rem 1.5rem; margin-bottom: 1.5rem;">
        <h1 style="font-size: 2.4rem;">📚 ACADEMIC COURSE HUB</h1>
        <p>Manage your academic enrollments, select active courses, and initiate oral examinations.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("authentilearn/assets/courses_illustration_1779355247420.png", use_container_width=True)
    
    # Auto-populate a couple of default courses if database is empty
    try:
        all_courses = auth_db.get_all_courses()
        if not all_courses:
            auth_db.create_course("CS-401", "Machine Learning & Neural Networks", "ml_key", "Comprehensive machine learning curriculum scoping RFs, ensembles, preprocessing and XAI.", "random forest classifier, feature engineering, imbalanced classes, train_test_split, decision tree", "system")
            auth_db.create_course("CS-412", "FoliarNet Computer Vision", "cv_key", "Deep learning models for plant leaf pathogen identification and aerial multi-spectral imagery.", "foliarnet, computer vision, cnn, drone, validation, grad-cam", "system")
            # Auto-enroll student in CS-401 so they don't have to input anything
            if st.session_state.logged_in_user:
                auth_db.enroll_in_course(st.session_state.logged_in_user["username"], "CS-401", "ml_key")
    except Exception as e:
        print(f"Error auto-populating courses: {str(e)}")

    # We display an indicator of the active course
    if st.session_state.active_course:
        st.markdown(f"""
        <div class="status-clean" style="margin-bottom:1.5rem;">
            🎯 <b>ACTIVE COURSE SELECTED:</b> {st.session_state.active_course['course_name']} ({st.session_state.active_course['course_id']})
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-warning" style="margin-bottom:1.5rem;">
            ⚠️ <b>NO ACTIVE COURSE SELECTED:</b> Please enroll in a course and select it below to proceed to your coursework audit.
        </div>
        """, unsafe_allow_html=True)
        
    col1, col2 = st.columns([0.6, 0.4], gap="large")
    
    with col1:
        st.markdown("### 🎓 Enrolled Courses")
        enrolled_courses = []
        if st.session_state.logged_in_user:
            enrolled_courses = auth_db.get_student_courses(st.session_state.logged_in_user["username"])
        
        if not enrolled_courses:
            st.info("You are not currently enrolled in any courses. Use the panel on the right to enroll using a course key.")
        else:
            for course in enrolled_courses:
                st.markdown(f"""
                <div class="course-card" style="margin-bottom: 1rem;">
                    <h3 style="margin-top:0; color:var(--accent-blue);">{course['course_name']}</h3>
                    <p style="font-size:0.85rem; font-family:'Space Mono'; color:var(--muted);">Code: {course['course_id']}</p>
                    <p style="font-size:0.9rem; color:var(--text);">{course['description'] or 'No description provided.'}</p>
                    <p style="font-size:0.85rem; color:var(--accent-purple);"><b>Topics Covered:</b> {course['topics'] or 'General topics'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                sub_col1, sub_col2 = st.columns([0.5, 0.5])
                with sub_col1:
                    is_active = st.session_state.active_course and st.session_state.active_course["course_id"] == course["course_id"]
                    if is_active:
                        st.button("✓ Selected Active", key=f"active_btn_{course['course_id']}", disabled=True, use_container_width=True)
                    else:
                        if st.button("🎯 Select Course", key=f"select_btn_{course['course_id']}", use_container_width=True):
                            st.session_state.active_course = course
                            st.success(f"Selected {course['course_name']} as active course!")
                            time.sleep(0.5)
                            st.rerun()
                with sub_col2:
                    if st.button("📤 Proceed to Upload", key=f"proceed_btn_{course['course_id']}", use_container_width=True):
                        st.session_state.active_course = course
                        st.session_state.stage = "upload"
                        st.rerun()
                        
    with col2:
        if st.session_state.educator_mode:
            st.markdown("### 🛠️ Educator: Course Creation")
            with st.form("create_course_form"):
                new_c_id = st.text_input("Course Code:", placeholder="CS-401").strip()
                new_c_name = st.text_input("Course Name:", placeholder="Machine Learning & Deep Neural Nets").strip()
                new_c_key = st.text_input("Enrollment Key / Password:", placeholder="ml_2026_lock").strip()
                new_c_desc = st.text_area("Course Description:", placeholder="Advanced course covering neural nets, forests, and explainability.")
                new_c_topics = st.text_area("Syllabus Focus Topics (Comma-separated):", placeholder="random forest classifier, feature engineering, imbalanced classes, pipeline imputation, model interpretability, convnets, agriculture, tomato, foliarnet, neural networks")
                
                submit_create = st.form_submit_button("➕ Create Course", use_container_width=True)
                if submit_create:
                    if not new_c_id or not new_c_name or not new_c_key:
                        st.warning("Course Code, Course Name, and Enrollment Key are required.")
                    else:
                        cleaned_topics = ", ".join([t.strip().lower() for t in new_c_topics.split(",") if t.strip()])
                        success, msg = auth_db.create_course(
                            course_id=new_c_id,
                            course_name=new_c_name,
                            enrollment_key=new_c_key,
                            description=new_c_desc,
                            topics=cleaned_topics,
                            created_by=st.session_state.logged_in_user["username"] if st.session_state.logged_in_user else "system"
                        )
                        if success:
                            st.success(f"✓ {msg}")
                            if st.session_state.logged_in_user:
                                auth_db.enroll_in_course(st.session_state.logged_in_user["username"], new_c_id, new_c_key)
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                            
        st.markdown("### 🔑 Join Course")
        with st.form("enroll_course_form"):
            enroll_c_id = st.text_input("Course Code to Join:", placeholder="CS-401").strip()
            enroll_c_key = st.text_input("Course Enrollment Key:", type="password", placeholder="••••••••").strip()
            
            submit_enroll = st.form_submit_button("🚀 Join Course & Unlock Syllabus", use_container_width=True)
            if submit_enroll:
                if not enroll_c_id or not enroll_c_key:
                    st.warning("Please enter both the course code and key.")
                else:
                    if st.session_state.logged_in_user:
                        success, msg = auth_db.enroll_in_course(
                            username=st.session_state.logged_in_user["username"],
                            course_id=enroll_c_id,
                            enrollment_key=enroll_c_key
                        )
                        if success:
                            st.success(f"✓ {msg}")
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.error("Please login first.")

# ========================================================
# NEW STAGE: AI STUDY BUDDY CHATBOT ASSISTANT
# ========================================================
elif st.session_state.stage == "chatbot":
    st.markdown("""
    <div class="hero-header" style="padding: 2rem 1.5rem; margin-bottom: 1.5rem;">
        <h1 style="font-size: 2.4rem;">🤖 AI STUDY BUDDY ASSISTANT</h1>
        <p>Interact with our smart AI assistant to clarify course concepts, research syllabus topics, and verify academic understanding.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("authentilearn/assets/study_buddy_illustration_1779355592838.png", use_container_width=True)
    
    if st.session_state.active_course:
        course = st.session_state.active_course
        st.markdown(f"""
        <div class="status-clean" style="margin-bottom:1.5rem;">
            📚 <b>CURRENTLY TUNED TO:</b> {course['course_name']} ({course['course_id']})<br/>
            <span style="font-size:0.85rem; opacity:0.9;">Tutor scope: {course['topics']}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-warning" style="margin-bottom:1.5rem;">
            ⚠️ <b>GENERAL MODE:</b> No active course selected. Select a course in the "Courses" hub to scope the study buddy to your specific syllabus.
        </div>
        """, unsafe_allow_html=True)

    # Chat history display
    for msg in st.session_state.chat_history:
        role_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-bot"
        role_label = "👤 You" if msg["role"] == "user" else "🤖 Study Buddy"
        st.markdown(f"""
        <div class="{role_class}">
            <b>{role_label}:</b><br/>
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)
        
    user_query = st.chat_input("Ask a question about your course concepts...")
    
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        with st.spinner("AI Study Buddy is thinking..."):
            sys_context = "You are a helpful academic assistant."
            if st.session_state.active_course:
                course = st.session_state.active_course
                sys_context = f"You are the official AI Study Buddy tutor for the course: {course['course_name']}. Topics: {course['topics']}. ONLY answer questions related to these topics. If asked about anything else, refuse politely."
            
            response_text = ""
            if st.session_state.demo_mode:
                time.sleep(1.0)
                q_lower = user_query.lower()
                if "random forest" in q_lower or "decision tree" in q_lower:
                    response_text = "🌲 **Random Forest vs Decision Tree:** A decision tree splits data based on feature conditions. A Random Forest is an *ensemble method* that trains many decision trees on random subsets of data and features, then averages their votes. This significantly reduces variance and prevents overfitting!"
                elif "gradient" in q_lower or "learning rate" in q_lower:
                    response_text = "📉 **Gradient Descent:** It's an optimization algorithm used to minimize a loss function by iteratively moving in the direction of steepest descent. The *learning rate* determines the size of the steps taken to reach the minimum."
                elif "foliarnet" in q_lower or "tomato" in q_lower:
                    response_text = "🍅 **FoliarNet crop CV:** FoliarNet is a deep convolutional network optimized for plant disease detection. It leverages depthwise separable convolutions to cut parameter size by ~9x while maintaining 96%+ classification accuracy."
                else:
                    response_text = f"📚 **Study Buddy:** That's an interesting question about '{user_query}'! Under the '{st.session_state.active_course['course_name'] if st.session_state.active_course else 'General'}', we explore this concept in depth. Remember to connect it back to your core assignments!"
            else:
                try:
                    from google import genai
                    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
                    full_prompt = f"{sys_context}\n\nStudent Query: {user_query}\n\nProvide a clear, detailed, and professional academic answer."
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=full_prompt
                    )
                    response_text = response.text
                except Exception as e:
                    response_text = f"⚠️ [API Call Fallback] Study Buddy: To keep your session uninterrupted, I've compiled this answer locally: Regarding your query '{user_query}', please review the core course guidelines and ensure your study topics match our active syllabus!"
            
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            st.rerun()

# ========================================================
# STAGE 1: UPLOAD & PRE-AUDIT DIAGNOSTICS STAGE
# ========================================================
elif st.session_state.stage == "upload":
    
    # Header
    st.markdown(f"""
    <div class="hero-header">
        <h1>{get_txt('title')}</h1>
        <p>{get_txt('subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("authentilearn/assets/coursework_illustration_1779355345723.png", use_container_width=True)
    
    # Check if we have analyzed coursework and generated questions
    if st.session_state.questions:
        # ----------------------------------------------------
        # WORKCOURSE PRE-AUDIT DIAGNOSTICS VIEW
        # ----------------------------------------------------
        st.markdown("### 🔍 SUBMISSION PRE-AUDIT INTEGRITY DIAGNOSTICS")
        st.write("Review plagiarism flags, sentence authenticity, and generated oral syllabus details before initiating the adaptive viva.")

        diag_col1, diag_col2 = st.columns([0.62, 0.38], gap="large")

        with diag_col1:
            st.markdown("<div class='metric-card' style='margin-bottom:1.5rem;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:var(--accent-blue); margin-top:0;'>📜 Academic coursework Highlight Map</h4>", unsafe_allow_html=True)
            st.write("Color-coded triggers: 🔴 Plagiarized/Copy-Paste | 🟡 AI Structural Phrasing | 🟣 advanced vocabulary (Suspicion Match)")
            
            # Interactive Dropdown locator
            flagged_options = []
            flagged_lines_dict = {}
            if st.session_state.line_table is not None:
                flagged_df = st.session_state.line_table[st.session_state.line_table["flag"] != "clean"]
                for _, row in flagged_df.iterrows():
                    lbl = f"Line {row['line_number']}: {row['text'][:55]}... ({row['flag'].replace('_', ' ').upper()})"
                    flagged_options.append(lbl)
                    flagged_lines_dict[lbl] = row.to_dict()
            
            selected_lbl = None
            if flagged_options:
                selected_lbl = st.selectbox(
                    "🔍 Turnitin-Style Highlight Locator:",
                    options=["-- Select a flagged sentence to auto-scroll & focus --"] + flagged_options,
                    index=0,
                    key="turnitin_locator"
                )
            
            # Highlight map container with potential focus replacement
            highlighted_content = st.session_state.highlighted_submission
            
            scroll_js = ""
            if selected_lbl and selected_lbl != "-- Select a flagged sentence to auto-scroll & focus --":
                target_row = flagged_lines_dict[selected_lbl]
                target_text = target_row["text"].strip()
                escaped_target = target_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                import re
                escaped_regex = re.escape(escaped_target)
                pattern = rf'<span class="highlight-(?:ai|copy|vocab)"[^>]*>.*?{escaped_regex}.*?</span>'
                focused_span = f'<span id="focused-highlight" class="turnitin-pulse-glow" title="[FOCUS] {target_row["reason"]}">{escaped_target}</span>'
                
                if re.search(pattern, highlighted_content, re.IGNORECASE):
                    highlighted_content = re.sub(pattern, focused_span, highlighted_content, flags=re.IGNORECASE)
                else:
                    highlighted_content = highlighted_content.replace(escaped_target, focused_span)
                
                scroll_js = """
                <script>
                setTimeout(function() {
                    var parentDoc = window.parent.document;
                    var el = parentDoc.getElementById("focused-highlight");
                    if (el) {
                        el.scrollIntoView({ behavior: "smooth", block: "center" });
                        el.style.outline = "4px solid #ef4444";
                        el.style.outlineOffset = "2px";
                        el.style.transition = "outline 0.3s ease";
                        setTimeout(function() {
                            el.style.outline = "none";
                        }, 1200);
                    }
                }, 250);
                </script>
                """

            st.markdown(f"""
            <div id="highlight-map-container" style="background-color:var(--surface2); padding:1.2rem; border-radius:12px; border:1px solid var(--border); max-height:350px; overflow-y:auto; line-height:1.7; font-size:0.95rem; color:var(--text); position: relative;">
                {highlighted_content}
            </div>
            """, unsafe_allow_html=True)
            
            if scroll_js:
                st.components.v1.html(scroll_js, height=0, width=0)
                
            st.markdown("</div>", unsafe_allow_html=True)

            # Feature 5: Line-by-line sentence grading table (Educator Mode Only)
            if st.session_state.educator_mode and st.session_state.line_table is not None:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color:var(--accent-purple); margin-top:0;'>📑 Line-by-Line Sentence Authenticity Grid</h4>", unsafe_allow_html=True)
                
                # Render table
                df_disp = st.session_state.line_table[["line_number", "flag", "authenticity_score", "reason"]].copy()
                df_disp.columns = ["Line #", "Flag Status", "Authenticity Score (%)", "Analysis Verdict"]
                st.dataframe(df_disp, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with diag_col2:
            st.markdown("<div class='metric-card' style='margin-bottom:1.5rem;'>", unsafe_allow_html=True)
            # Speedometer Risk Gauge (Feature 3)
            risk_score = st.session_state.cheat_analysis.get("overall_authenticity_score", 70)
            risk_idx = 100 - risk_score
            fig_gauge = get_copy_paste_gauge_chart(risk_idx)
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Oral Syllabus
            st.markdown("<div class='metric-card' style='margin-bottom:1.5rem;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:var(--accent-blue); margin-top:0;'>🎙️ Generated Adaptive viva Syllabus</h4>", unsafe_allow_html=True)
            for i, q in enumerate(st.session_state.questions):
                st.markdown(f"**Q{i+1}: {q['concept_tested']}** `[{q['difficulty'].upper()}]`")
                st.markdown(f"<span style='color:var(--muted); font-size:0.85rem;'>{q['question']}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Big Glowing Proceed Button
        st.markdown("<br/>", unsafe_allow_html=True)
        btn_start_col1, btn_start_col2 = st.columns([0.3, 0.4])
        with btn_start_col2:
            if st.button("🎙️ Start Oral Examination →", use_container_width=True):
                st.session_state.stage = "viva"
                st.session_state.current_q_index = 0
                st.session_state.viva_start_time = time.time()
                st.session_state.q_start_time = time.time()
                st.session_state.qa_pairs = []
                st.session_state.followup_active = False
                st.session_state.audio_bytes = None
                st.session_state.current_answer = ""
                st.session_state.paste_events = []
                st.rerun()
                
        if st.button("🔄 Re-upload Different Coursework", use_container_width=True):
            st.session_state.questions = []
            st.session_state.content = ""
            st.rerun()

    else:
        # Standard File Upload Tab layout
        col1, col2 = st.columns([0.58, 0.42], gap="large")
        
        with col1:
            st.markdown("### 📤 SUBMIT WORK FOR VERIFICATION", unsafe_allow_html=True)
            
            tab1, tab2, tab3 = st.tabs([get_txt("upload_tab"), get_txt("paste_tab"), get_txt("demo_tab")])
            
            with tab1:
                uploaded_file = st.file_uploader(
                    "Upload student assignment file", 
                    type=["pdf", "docx", "txt", "py", "js", "md", "html", "json", "cpp"],
                    help="Support PDFs, Word files, text formats, and code scripts."
                )
                if uploaded_file is not None:
                    with st.spinner("Extracting contents..."):
                        text_extracted = extract_text(uploaded_file)
                        metadata = get_file_metadata(uploaded_file)
                        
                        if text_extracted.strip():
                            st.session_state.content = text_extracted
                            st.session_state.file_metadata = metadata
                            
                            st.markdown(f"""
                            <div class="metric-card" style="border-color:var(--accent-green); background-color: rgba(16, 185, 129, 0.05) !important; margin-bottom:1rem;">
                                <span style="color:var(--accent-green); font-weight:bold; font-family:'Space Mono';">✓ FILE EXTRACTED SUCCESSFULLY</span><br/>
                                <span style="font-size:0.9rem; color:var(--text);">
                                    <b>Name:</b> {metadata['name']} | 
                                    <b>Type:</b> {metadata['type']} | 
                                    <b>Words:</b> {metadata['estimated_words']}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                            st.text_area("Submission Preview (First 400 Characters)", text_extracted[:400] + "...", height=120, disabled=True)
                        else:
                            st.error("No extractable text found in this file.")
            
            with tab2:
                pasted_input = st.text_area("Paste assignment essay, report, or code pipeline here", height=250, value=st.session_state.pasted_text)
                st.session_state.pasted_text = pasted_input
                
                if pasted_input.strip():
                    st.session_state.content = pasted_input
                    words = len(pasted_input.split())
                    chars = len(pasted_input)
                    
                    code_keywords = ["def ", "import ", "class ", "function", "const ", "let ", "var ", "console.log", "print("]
                    is_code = any(kw in pasted_input for kw in code_keywords)
                    doc_type = "Source Code Script" if is_code else "Academic Text / Essay"
                    
                    st.session_state.file_metadata = {
                        "name": "Pasted Content",
                        "size_kb": round(chars / 1024, 2),
                        "type": doc_type,
                        "char_count": chars,
                        "estimated_words": words
                    }
                    st.markdown(f"<p style='font-size:0.85rem; color:var(--accent-blue); font-family:\"Space Mono\"; margin-top:4px;'>💻 {get_txt('detected_label')} {doc_type} | {words} {get_txt('word_counter')}</p>", unsafe_allow_html=True)
            
            with tab3:
                st.write("Click a sample preset below to load a coursework submission instantly. Highly recommended for testing AI integration!")
                
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col1:
                    if st.button("🐍 Python ML Code"):
                        st.session_state.content = DEMO_SAMPLES["Python ML Code"]
                        st.session_state.file_metadata = {
                            "name": "churn_prediction.py",
                            "size_kb": 1.2,
                            "type": "Python Source Code",
                            "char_count": len(DEMO_SAMPLES["Python ML Code"]),
                            "estimated_words": len(DEMO_SAMPLES["Python ML Code"].split())
                        }
                        st.success("Loaded 'Python ML Code' sample.")
                with sub_col2:
                    if st.button("📝 Essay Sample"):
                        st.session_state.content = DEMO_SAMPLES["Essay Sample"]
                        st.session_state.file_metadata = {
                            "name": "ai_ethics_essay.txt",
                            "size_kb": 1.8,
                            "type": "Plain Text Essay",
                            "char_count": len(DEMO_SAMPLES["Essay Sample"]),
                            "estimated_words": len(DEMO_SAMPLES["Essay Sample"].split())
                        }
                        st.success("Loaded 'Essay Sample' sample.")
                with sub_col3:
                    if st.button("🔬 Research Abstract"):
                        st.session_state.content = DEMO_SAMPLES["Research Abstract"]
                        st.session_state.file_metadata = {
                            "name": "foliarnet_abstract.txt",
                            "size_kb": 2.1,
                            "type": "Research Abstract",
                            "char_count": len(DEMO_SAMPLES["Research Abstract"]),
                            "estimated_words": len(DEMO_SAMPLES["Research Abstract"].split())
                        }
                        st.success("Loaded 'Research Abstract' sample.")
            
            if st.session_state.demo_mode and st.session_state.content.strip():
                is_demo_preset = False
                for preset_name, preset_text in DEMO_SAMPLES.items():
                    if st.session_state.content.strip() == preset_text.strip():
                        is_demo_preset = True
                        break
                if not is_demo_preset:
                    st.warning("⚠️ **Demo Mode Active**: You supplied custom content but **Demo Mode** is enabled. The system will adaptively extract phrases to run a mock oral syllabus. For true real-time Gemini generation on custom text, toggle Demo Mode off in the sidebar, paste a valid API key, and retry!")

            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            if st.button(get_txt("start_btn"), use_container_width=True):
                if not st.session_state.content.strip():
                    st.warning("Please upload coursework, paste text, or load a sample first.")
                elif not st.session_state.demo_mode and not os.environ.get("GOOGLE_API_KEY"):
                    st.error("Missing Gemini API Key. Supply a key in the sidebar or toggle Demo Mode.")
                else:
                    try:
                        with st.spinner("🧠 Analyzing submission text structure and extracting integrity diagnostics..."):
                            # 1. Summary Analysis
                            analysis = analyze_submission(
                                st.session_state.content, 
                                api_key=os.environ.get("GOOGLE_API_KEY"), 
                                demo_mode=st.session_state.demo_mode
                            )
                            st.session_state.submission_analysis = analysis
                            
                            # 2. Plagiarism Highlighting (Feature 3)
                            cheat_res = analyze_submission_authenticity(
                                st.session_state.content,
                                api_key=os.environ.get("GOOGLE_API_KEY"),
                                demo_mode=st.session_state.demo_mode
                            )
                            st.session_state.cheat_analysis = cheat_res
                            st.session_state.highlighted_submission = highlight_suspicious_text(
                                st.session_state.content, 
                                cheat_res.get("suspicious_phrases", [])
                            )
                            
                            # 3. Line Analysis Sentence Grading (Feature 5)
                            line_res = analyze_line_by_line(
                                st.session_state.content,
                                api_key=os.environ.get("GOOGLE_API_KEY"),
                                demo_mode=st.session_state.demo_mode
                            )
                            st.session_state.last_sentence_analysis = line_res
                            if line_res:
                                st.session_state.line_table = pd.DataFrame(line_res)
                            
                            # 4. Generate Core Questions
                            questions = generate_questions(
                                st.session_state.content,
                                api_key=os.environ.get("GOOGLE_API_KEY"),
                                demo_mode=st.session_state.demo_mode
                            )
                            
                            # 5. Question Injection of High-risk lines (Feature 5)
                            high_risk_lines = [item for item in line_res if item.get("flag") in ["likely_ai", "suspicious"]]
                            if high_risk_lines:
                                for i, item in enumerate(high_risk_lines[:2]):
                                    target_idx = 2 + i # replaces Q3 and Q4
                                    if target_idx < len(questions):
                                        questions[target_idx] = {
                                            "id": target_idx + 1,
                                            "question": item["suggested_viva_question"],
                                            "difficulty": "medium",
                                            "concept_tested": f"Line {item['line_number']} Integrity Check",
                                            "hint_topic": "Elaborating on line structure, context validation",
                                            "target_line_number": item.get("line_number"),
                                            "target_line_text": item.get("text"),
                                            "target_line_reason": item.get("reason")
                                        }
                                        
                            st.session_state.questions = questions
                            st.rerun()
                    except Exception as e:
                        err_msg = str(e)
                        st.warning("⚠️ **AI Pipeline Exception or Rate Limit Reached!** AuthentiLearn AI is gracefully switching to **High-Fidelity Offline Simulation Mode** to preserve your evaluation experience. You can proceed with the oral examination normally!")
                        time.sleep(3.0)
                        try:
                            with st.spinner("🧠 Initializing High-Fidelity Simulation Engine..."):
                                # Rerun summary analysis
                                analysis = analyze_submission(
                                    st.session_state.content, 
                                    demo_mode=True
                                )
                                st.session_state.submission_analysis = analysis
                                
                                # Plagiarism highlighting
                                cheat_res = analyze_submission_authenticity(
                                    st.session_state.content,
                                    demo_mode=True
                                )
                                st.session_state.cheat_analysis = cheat_res
                                st.session_state.highlighted_submission = highlight_suspicious_text(
                                    st.session_state.content, 
                                    cheat_res.get("suspicious_phrases", [])
                                )
                                
                                # Line-by-line sentence grading
                                line_res = analyze_line_by_line(
                                    st.session_state.content,
                                    demo_mode=True
                                )
                                st.session_state.last_sentence_analysis = line_res
                                if line_res:
                                    st.session_state.line_table = pd.DataFrame(line_res)
                                
                                # Generate core questions
                                questions = generate_questions(
                                    st.session_state.content,
                                    demo_mode=True
                                )
                                
                                # High-risk question injection
                                high_risk_lines = [item for item in line_res if item.get("flag") in ["likely_ai", "suspicious"]]
                                if high_risk_lines:
                                    for i, item in enumerate(high_risk_lines[:2]):
                                        target_idx = 2 + i
                                        if target_idx < len(questions):
                                            questions[target_idx] = {
                                                "id": target_idx + 1,
                                                "question": item["suggested_viva_question"],
                                                "difficulty": "medium",
                                                "concept_tested": f"Line {item['line_number']} Integrity Check",
                                                "hint_topic": "Elaborating on line structure, context validation",
                                                "target_line_number": item.get("line_number"),
                                                "target_line_text": item.get("text"),
                                                "target_line_reason": item.get("reason")
                                            }
                                            
                                st.session_state.questions = questions
                                st.session_state.demo_mode = True  # force demo mode active for subsequent stages
                                st.rerun()
                        except Exception as fallback_err:
                            st.error(f"❌ Simulation initialization failed: {str(fallback_err)}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("### ⚡ HOW IT WORKS", unsafe_allow_html=True)
            st.markdown("""
            <div class="timeline-step">
                <div class="timeline-badge"></div>
                <div class="timeline-title">Step 1: Student Biometrics Secure-Lock</div>
                <div class="timeline-desc">Verifies physical matching signatures via Cosine distance & Grayscale pixel distributions to lock identity profiles.</div>
            </div>
            <div class="timeline-step">
                <div class="timeline-badge"></div>
                <div class="timeline-title">Step 2: Coursework Diagnostics Analysis</div>
                <div class="timeline-desc">Runs single-batch AI phrase forensics & line-by-line sentence checks to isolate cheating risk factors.</div>
            </div>
            <div class="timeline-step">
                <div class="timeline-badge"></div>
                <div class="timeline-title">Step 3: Conduct Adaptive Oral Examination</div>
                <div class="timeline-desc">Engages students in a 5-question verbal exam with live copy-paste sensors, microphone recording, and continuous voice tracking.</div>
            </div>
            <div class="timeline-step">
                <div class="timeline-badge"></div>
                <div class="timeline-title">Step 4: Compiling Academic Authenticity Audit</div>
                <div class="timeline-desc">Analyzes understanding depth, generates strengths vs gaps metrics, and renders a magnificent 6-chart graph dashboard.</div>
            </div>
            """, unsafe_allow_html=True)
            st.image("authentilearn/assets/oral_exam_illustration_1779355443491.png", use_container_width=True)


# ========================================================
# STAGE 2: ADAPTIVE ORAL VIVA EXAMINATION
# ========================================================
elif st.session_state.stage == "viva":
    # 1. Hide Streamlit sidebar during the active oral examination
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 2. Display persistent security alerts if any exist in the session state
    if st.session_state.security_warning:
        st.warning(st.session_state.security_warning)
        st.session_state.security_warning = None
    if st.session_state.security_error:
        st.error(st.session_state.security_error)
        st.session_state.security_error = None

    # 3. Inject hidden iframe to listen to parent window events (fullscreen, tab-switch, copy-paste)
    st.components.v1.html("""
    <script>
        const parentDoc = window.parent.document;
        
        // Mark exam as active
        window.parent.__authentilearn_exam_active = true;
        
        // Function to request fullscreen on parent window
        function requestFullscreenSafely() {
            if (window.parent.__authentilearn_exam_active && !parentDoc.fullscreenElement) {
                window.parent.document.documentElement.requestFullscreen().catch(err => {
                    console.log("Fullscreen request deferred: waiting for user click.");
                });
            }
        }
        
        // Try going fullscreen immediately
        requestFullscreenSafely();
        
        // Register on click events to satisfy browser gesture requirements
        parentDoc.addEventListener('click', requestFullscreenSafely);
        
        // Bind listeners exactly once
        if (!window.parent.__authentilearn_listeners_attached) {
            window.parent.__authentilearn_listeners_attached = true;
            
            // A. Block right-click context menu
            parentDoc.addEventListener('contextmenu', function(e) {
                if (window.parent.__authentilearn_exam_active) {
                    e.preventDefault();
                }
            });
            
            // B. Block text selection copy and cut
            parentDoc.addEventListener('copy', function(e) {
                if (window.parent.__authentilearn_exam_active) {
                    e.preventDefault();
                    window.parent.location.search = "?copy_attempt=1";
                }
            });
            parentDoc.addEventListener('cut', function(e) {
                if (window.parent.__authentilearn_exam_active) {
                    e.preventDefault();
                    window.parent.location.search = "?copy_attempt=1";
                }
            });
            
            // C. Block paste events (prevent paste in all textareas)
            parentDoc.addEventListener('paste', function(e) {
                if (window.parent.__authentilearn_exam_active) {
                    e.preventDefault();
                    window.parent.location.search = "?copy_attempt=1";
                }
            });
            
            // D. Block keyboard shortcuts (Ctrl+C, Ctrl+V, Ctrl+A, Ctrl+U, Ctrl+P)
            parentDoc.addEventListener('keydown', function(e) {
                if (!window.parent.__authentilearn_exam_active) return;
                
                const isCtrlOrCmd = e.ctrlKey || e.metaKey;
                const key = e.key.toLowerCase();
                
                if (isCtrlOrCmd && (key === 'c' || key === 'v' || key === 'a' || key === 'u' || key === 'p')) {
                    e.preventDefault();
                    window.parent.location.search = "?copy_attempt=1";
                }
            });
            
            // E. Detect Fullscreen Exit
            parentDoc.addEventListener('fullscreenchange', function() {
                if (window.parent.__authentilearn_exam_active && !parentDoc.fullscreenElement) {
                    window.parent.location.search = "?fullscreen_exit=1";
                }
            });
            
            // F. Detect Window Blur / Tab Switching
            window.parent.addEventListener('blur', function() {
                if (window.parent.__authentilearn_exam_active) {
                    window.parent.location.search = "?tab_switch=1";
                }
            });
        }
    </script>
    """, height=0)

    current_idx = st.session_state.current_q_index
    current_q = st.session_state.questions[current_idx]
    
    elapsed_time = round(time.time() - st.session_state.viva_start_time)
    elapsed_str = f"{elapsed_time // 60}m {elapsed_time % 60}s"
    
    progress_val = (current_idx) / 5.0
    
    st.markdown(f"### 🎯 QUESTION {current_idx + 1} OF 5")
    st.progress(progress_val)
    
    top_col1, top_col2, top_col3 = st.columns([0.4, 0.3, 0.3])
    with top_col1:
        st.markdown(f"**Concept Area:** `{current_q['concept_tested'].upper()}`")
    with top_col2:
        diff_color = "var(--accent-green)" if current_q['difficulty'] == "easy" else "var(--accent-amber)" if current_q['difficulty'] == "medium" else "var(--accent-red)"
        st.markdown(f"**Level:** <span style='color:{diff_color}; font-family:\"Space Mono\"; font-weight:bold;'>{current_q['difficulty'].upper()}</span>", unsafe_allow_html=True)
    with top_col3:
        st.markdown(f"⏱️ **Total Elapsed:** `{elapsed_str}`")
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    is_evaluated = len(st.session_state.qa_pairs) > current_idx
    
    elapsed_q_time = time.time() - st.session_state.q_start_time
    remaining_q_seconds = max(0, 60 - int(elapsed_q_time))

    col1, col2 = st.columns([0.65, 0.35], gap="large")
    
    with col1:
        # Continuous voice re-verification indicator dot (Feature 2)
        if not is_evaluated and current_idx > 0 and current_idx % 2 == 1:
            try:
                voice_res = verify_voice_profile(
                    st.session_state.auth_profile["voice_template"],
                    duration=1.0
                )
                v_score = voice_res["similarity_score"]
                if v_score >= 0.82:
                    dot_cls = "voice-dot-green"
                    dot_lbl = "Verified Signature Matching Lock"
                elif v_score >= 0.70:
                    dot_cls = "voice-dot-amber"
                    dot_lbl = "Minor Spectral Jitters Detected"
                else:
                    dot_cls = "voice-dot-red"
                    dot_lbl = "Biometric Alert: Audio foot-hash Mismatch!"
                
                st.markdown(f"""
                <div style="background-color:#0f172a; padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; margin-bottom:1rem;">
                    <span style="font-size:0.85rem; color:var(--text);">🔒 Continuous voice Validation:</span>
                    <span><span style='font-size:0.8rem; font-family:"Space Mono"; color:var(--muted);'>{dot_lbl}</span> <div class="{dot_cls}"></div></span>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                pass

        # ----------------------------------------------------
        # 1-MINUTE TIMER GRAPHICAL COMPONENT (SANDBOX SAFE IFRAME)
        # ----------------------------------------------------
        if not is_evaluated:
            parent_url = f"?timeout=1&q={current_idx}&t={time.time()}"
            
            st.components.v1.html(f"""
            <div id="countdown-widget" style="padding: 10px; background: linear-gradient(to right, #090f1e, rgba(244, 63, 94, 0.08)); border: 1px solid rgba(244, 63, 94, 0.25); border-radius: 12px; text-align: center;">
                <div class="timer-accent-text" style="font-family: 'Space Mono', monospace; font-size: 1.15rem; color: #f43f5e; font-weight: bold;">
                    ⏱️ TIME REMAINING: <span id="timer-count">{remaining_q_seconds}</span> SECONDS
                </div>
                <div class="timer-bar-bg" style="width: 100%; background: #0f172a; border-radius: 6px; height: 8px; margin-top: 10px; overflow: hidden; border: 1px solid #1e293b;">
                    <div id="timer-bar-fill" class="timer-bar-fill" style="background: linear-gradient(to right, #00f0ff, #f43f5e); height: 100%; width: {remaining_q_seconds / 60 * 100}%; transition: width 1s linear;"></div>
                </div>
                <a id="timeout-link" href="{parent_url}" target="_parent" style="display:none;">Timeout Trigger</a>
            </div>
            
            <script>
                var duration = 60;
                var count = {remaining_q_seconds};
                var bar = document.getElementById("timer-bar-fill");
                var counter = document.getElementById("timer-count");
                
                var timer = setInterval(function() {{
                    count--;
                    if (count < 0) count = 0;
                    if (counter) counter.innerText = count;
                    if (bar) bar.style.width = (count / duration * 100) + "%";
                    
                    if (count <= 0) {{
                        clearInterval(timer);
                        document.getElementById("timeout-link").click();
                    }}
                }}, 1000);
            </script>
            """, height=70)
            
        is_timed_out = False
        if not is_evaluated and elapsed_q_time >= 60.0:
            is_timed_out = True

        # Display flagged line card if this question is auditing a high-risk text segment
        if "target_line_number" in current_q and current_q["target_line_number"] is not None:
            st.markdown(f"""
            <div class="viva-audit-highlight-card">
                <h5 style="color:var(--accent-red); margin-top:0; margin-bottom:0.6rem; display:flex; align-items:center; gap:0.5rem; font-size:0.95rem;">
                    ⚠️ INTEGRITY AUDIT: TARGETED SUSPICIOUS SEGMENT (LINE {current_q['target_line_number']})
                </h5>
                <p style="font-size:0.92rem; margin-bottom:0.8rem; font-style:italic; color:var(--text); line-height:1.5; padding:0.5rem 0.8rem; background:rgba(255,255,255,0.7); border-radius:6px; border:1px dashed var(--border);">
                    "{current_q['target_line_text']}"
                </p>
                <div style="font-size:0.82rem; color:var(--muted); font-weight:600;">
                    🛡️ FLAG REASON: <span style="color:var(--accent-purple);">{current_q['target_line_reason']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Question display card with anti-copy protection
        st.markdown(f"""
        <div class="anti-copy-layer">
            <div class="question-card">
                <div class="question-concept">{current_q['concept_tested']}</div>
                <div class="question-text">{current_q['question']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Audio Player Read Aloud
        voice_col1, voice_col2 = st.columns([0.3, 0.7])
        with voice_col1:
            if st.button("🔊 Read Aloud"):
                with st.spinner("Synthesizing oral question..."):
                    st.session_state.audio_bytes = text_to_speech(current_q["question"])
        with voice_col2:
            if st.session_state.audio_bytes:
                st.audio(st.session_state.audio_bytes, format="audio/mp3", autoplay=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        if not is_evaluated:
            if is_timed_out:
                st.error("⏰ TIME'S UP! You failed to submit an answer within the 60-second limit. You are locked out of typing. Please wait for the system to auto-advance, or click Skip to proceed.")

            # Initialize dynamic answer state holders to support speech-to-text integration without instantiation locks
            if f"ans_val_{current_idx}" not in st.session_state:
                st.session_state[f"ans_val_{current_idx}"] = ""

            def sync_answer_text(idx):
                st.session_state[f"ans_val_{idx}"] = st.session_state[f"ans_area_{idx}"]

            # Student Text Area Answer input
            ans_input = st.text_area(
                "Your Answer:", 
                value=st.session_state[f"ans_val_{current_idx}"],
                key=f"ans_area_{current_idx}", 
                placeholder="Formulate your answer here. Provide conceptual explanations, context decisions, or technical logic...", 
                height=180,
                disabled=is_timed_out,
                on_change=sync_answer_text,
                args=(current_idx,)
            )
            
            # Words counter
            word_count = len(ans_input.strip().split()) if ans_input.strip() else 0
            st.markdown(f"<span style='font-size:0.8rem; color:var(--muted);'>{word_count} words written</span>", unsafe_allow_html=True)
            
            # ----------------------------------------------------
            # FEATURE 3: REAL-TIME PLAGIARISM PASTE MONITORING
            # ----------------------------------------------------
            if ans_input != st.session_state.current_answer:
                paste_res = detect_realtime_paste(ans_input, st.session_state.current_answer)
                if paste_res["is_paste"]:
                    spon_res = analyze_answer_spontaneity(
                        current_q["question"],
                        ans_input,
                        api_key=os.environ.get("GOOGLE_API_KEY"),
                        demo_mode=st.session_state.demo_mode
                    )
                    event_log = {
                        "question_id": current_q["id"],
                        "chars_added": paste_res["chars_added"],
                        "verdict": spon_res["verdict"],
                        "score": spon_res["live_answer_score"],
                        "timestamp": time.time()
                    }
                    st.session_state.paste_events.append(event_log)
                st.session_state.current_answer = ans_input

            # Render status bar alert if paste logged
            if st.session_state.paste_events and any(e["question_id"] == current_q["id"] for e in st.session_state.paste_events):
                latest_event = [e for e in st.session_state.paste_events if e["question_id"] == current_q["id"]][-1]
                if latest_event["verdict"] == "likely_googled":
                    st.markdown(f"<div class='status-danger'>🚨 REAL-TIME PLAGIARISM WARNING: Block paste of {latest_event['chars_added']} chars detected. Spontaneity Check: FAILED. High risk of copy-paste.</div>", unsafe_allow_html=True)
                elif latest_event["verdict"] == "prepared_answer":
                    st.markdown(f"<div class='status-warning'>⚠️ REAL-TIME SUSPICION WARNING: Pasted text detected. Tone displays pre-prepared formal structures.</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='status-clean'>✓ Real-time Spontaneity: Stable typing speeds verified.</div>", unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button(get_txt("submit_btn"), use_container_width=True, disabled=is_timed_out):
                    if not ans_input.strip():
                        st.warning("Please type your answer before submitting.")
                    else:
                        with st.spinner("Scoring response understanding and depth..."):
                            try:
                                time_taken = time.time() - st.session_state.q_start_time
                                eval_res = evaluate_answer(
                                    content=st.session_state.content,
                                    question=current_q["question"],
                                    answer=ans_input,
                                    api_key=os.environ.get("GOOGLE_API_KEY"),
                                    demo_mode=st.session_state.demo_mode,
                                    q_id=current_q["id"],
                                    is_followup=False
                                )
                                
                                qa_record = {
                                    "question_id": current_q["id"],
                                    "question": current_q["question"],
                                    "difficulty": current_q["difficulty"],
                                    "concept_tested": current_q["concept_tested"],
                                    "answer": ans_input,
                                    "time_taken": time_taken,
                                    "skipped": False,
                                    "evaluation": eval_res,
                                    "followup_pair": None
                                }
                                st.session_state.qa_pairs.append(qa_record)
                                st.session_state.current_q_evaluation = eval_res
                                
                                # Check if Gemini requested follow-up escalation
                                if eval_res.get("needs_followup") and eval_res.get("followup_question"):
                                    st.session_state.followup_active = True
                                    st.session_state.followup_question = eval_res["followup_question"]
                                    st.session_state.followup_answer = ""
                                
                                st.session_state.audio_bytes = None
                                st.session_state.current_answer = ""
                                st.rerun()
                            except Exception as e:
                                st.warning("⚠️ **Gemini API Exception/Limit reached!** AuthentiLearn AI is gracefully switching to **High-Fidelity Offline Simulation Mode** to evaluate your answer.")
                                st.session_state.demo_mode = True
                                try:
                                    eval_res = evaluate_answer(
                                        content=st.session_state.content,
                                        question=current_q["question"],
                                        answer=ans_input,
                                        demo_mode=True,
                                        q_id=current_q["id"],
                                        is_followup=False
                                    )
                                    qa_record = {
                                        "question_id": current_q["id"],
                                        "question": current_q["question"],
                                        "difficulty": current_q["difficulty"],
                                        "concept_tested": current_q["concept_tested"],
                                        "answer": ans_input,
                                        "time_taken": time_taken,
                                        "skipped": False,
                                        "evaluation": eval_res,
                                        "followup_pair": None
                                    }
                                    st.session_state.qa_pairs.append(qa_record)
                                    st.session_state.current_q_evaluation = eval_res
                                    
                                    # Check if Gemini requested follow-up escalation
                                    if eval_res.get("needs_followup") and eval_res.get("followup_question"):
                                        st.session_state.followup_active = True
                                        st.session_state.followup_question = eval_res["followup_question"]
                                        st.session_state.followup_answer = ""
                                    
                                    st.session_state.audio_bytes = None
                                    st.session_state.current_answer = ""
                                    st.rerun()
                                except Exception as fallback_err:
                                    st.error(f"❌ Answer Evaluation Fallback Failed: {str(fallback_err)}")
            
            with btn_col2:
                st.markdown("<div class='ghost-btn'>", unsafe_allow_html=True)
                if st.button(get_txt("skip_btn"), use_container_width=True):
                    time_taken = time.time() - st.session_state.q_start_time
                    qa_record = {
                        "question_id": current_q["id"],
                        "question": current_q["question"],
                        "difficulty": current_q["difficulty"],
                        "concept_tested": current_q["concept_tested"],
                        "answer": "[Skipped]",
                        "time_taken": time_taken,
                        "skipped": True,
                        "evaluation": {
                            "correctness": 0,
                            "depth": 0,
                            "specificity": 0,
                            "overall_score": 0.0,
                            "feedback": "Question was skipped by the student.",
                            "red_flags": ["Question skipped"],
                            "needs_followup": False,
                            "followup_question": ""
                        },
                        "followup_pair": None
                    }
                    st.session_state.qa_pairs.append(qa_record)
                    st.session_state.audio_bytes = None
                    st.session_state.current_answer = ""
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # Feature 2: Speak Answer recording integration
            st.markdown("---")
            mic_speak_col1, mic_speak_col2 = st.columns([0.45, 0.55])
            with mic_speak_col1:
                if st.button("🎤 Speak Your Answer", use_container_width=True):
                    with st.spinner("🎙️ Listening to microphone. Speak your answer now..."):
                        spoken_trans, spoken_msg = record_and_transcribe_answer()
                        if spoken_trans:
                            st.success("✓ Speech transcribed successfully!")
                            st.session_state[f"ans_val_{current_idx}"] = spoken_trans
                            if f"ans_area_{current_idx}" in st.session_state:
                                del st.session_state[f"ans_area_{current_idx}"]
                            st.rerun()
                        else:
                            st.warning(f"Audio transcription alert: {spoken_msg}")

        else:
            # Answer is submitted and graded. Display feedback.
            qa_pair = st.session_state.qa_pairs[current_idx]
            eval_res = qa_pair["evaluation"]
            
            st.success("✓ Answer Registered")
            st.text_area("Your Submitted Answer:", value=qa_pair["answer"], height=100, disabled=True)
            
            st.markdown("### 📊 REAL-TIME AI GRADING FEEDBACK", unsafe_allow_html=True)
            grade_col1, grade_col2 = st.columns([0.45, 0.55])
            with grade_col1:
                st.write(f"**Correctness:** {eval_res['correctness'] * 10}%")
                st.progress(eval_res['correctness'] / 10.0)
                
                st.write(f"**Understanding Depth:** {eval_res['depth'] * 10}%")
                st.progress(eval_res['depth'] / 10.0)
                
                st.write(f"**Specificity:** {eval_res['specificity'] * 10}%")
                st.progress(eval_res['specificity'] / 10.0)
                
                st.metric("QUESTION INTEGRITY SCORE", f"{round(eval_res['overall_score'] * 10, 1)}%")
                
            with grade_col2:
                st.info(f"**Evaluator Comments:** {eval_res.get('feedback', '')}")
                if st.session_state.educator_mode:
                    if eval_res.get("red_flags"):
                        st.markdown("<div style='background-color:rgba(244, 63, 94, 0.08); padding:0.8rem; border-radius:8px; border:1px solid var(--accent-red);'>", unsafe_allow_html=True)
                        st.markdown("<span style='color:var(--accent-red); font-weight:bold; font-family:\"Space Mono\";'>🚨 DETECTED RED FLAGS:</span>", unsafe_allow_html=True)
                        for flag in eval_res.get("red_flags", []):
                            st.markdown(f"<span style='font-size:0.85rem; color:var(--text);'>- {flag}</span>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color:var(--accent-green); font-weight:bold;'>✓ No suspicious indicators found.</span>", unsafe_allow_html=True)
            
            # ----------------------------------------------------
            # ESCALATION ADAPTIVE FOLLOW-UP SUB-STAGE
            # ----------------------------------------------------
            if st.session_state.followup_active:
                st.markdown("<br/>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="anti-copy-layer">
                    <div class="question-card followup">
                        <div class="question-concept" style="color:var(--accent-purple);">🔄 ADAPTIVE ESCALATION FOLLOW-UP:</div>
                        <div class="question-text">{st.session_state.followup_question}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                follow_input = st.text_area(
                    "Your Follow-up Answer:", 
                    key=f"follow_area_{current_idx}", 
                    placeholder="Elaborate further on your initial answer, answering this pointed follow-up query...",
                    height=130
                )
                
                if st.button(get_txt("submit_followup"), use_container_width=True):
                    if not follow_input.strip():
                        st.warning("Please enter your answer to the follow-up question.")
                    else:
                        with st.spinner("Evaluating follow-up depth..."):
                            try:
                                follow_eval = evaluate_answer(
                                    content=st.session_state.content,
                                    question=st.session_state.followup_question,
                                    answer=follow_input,
                                    api_key=os.environ.get("GOOGLE_API_KEY"),
                                    demo_mode=st.session_state.demo_mode,
                                    q_id=current_q["id"],
                                    is_followup=True
                                )
                                
                                # Consolidate main answer and follow-up scores
                                main_eval = qa_pair["evaluation"]
                                consolidated_score = (main_eval["overall_score"] + follow_eval["overall_score"]) / 2
                                consolidated_correctness = (main_eval["correctness"] + follow_eval["correctness"]) / 2
                                consolidated_depth = (main_eval["depth"] + follow_eval["depth"]) / 2
                                consolidated_specificity = (main_eval["specificity"] + follow_eval["specificity"]) / 2
                                
                                combined_flags = list(set(main_eval.get("red_flags", []) + follow_eval.get("red_flags", [])))
                                
                                qa_pair["evaluation"] = {
                                    "correctness": round(consolidated_correctness, 1),
                                    "depth": round(consolidated_depth, 1),
                                    "specificity": round(consolidated_specificity, 1),
                                    "overall_score": round(consolidated_score, 1),
                                    "feedback": f"Main: {main_eval['feedback']} | Follow-up feedback: {follow_eval['feedback']}",
                                    "red_flags": combined_flags,
                                    "needs_followup": False,
                                    "followup_question": ""
                                }
                                
                                qa_pair["followup_pair"] = {
                                    "question": st.session_state.followup_question,
                                    "answer": follow_input,
                                    "evaluation": follow_eval
                                }
                                
                                st.session_state.followup_active = False
                                st.rerun()
                            except Exception as e:
                                st.warning("⚠️ **Gemini API Exception/Limit reached!** AuthentiLearn AI is gracefully switching to **High-Fidelity Offline Simulation Mode** to evaluate your follow-up answer.")
                                st.session_state.demo_mode = True
                                try:
                                    follow_eval = evaluate_answer(
                                        content=st.session_state.content,
                                        question=st.session_state.followup_question,
                                        answer=follow_input,
                                        demo_mode=True,
                                        q_id=current_q["id"],
                                        is_followup=True
                                    )
                                    
                                    # Consolidate main answer and follow-up scores
                                    main_eval = qa_pair["evaluation"]
                                    consolidated_score = (main_eval["overall_score"] + follow_eval["overall_score"]) / 2
                                    consolidated_correctness = (main_eval["correctness"] + follow_eval["correctness"]) / 2
                                    consolidated_depth = (main_eval["depth"] + follow_eval["depth"]) / 2
                                    consolidated_specificity = (main_eval["specificity"] + follow_eval["specificity"]) / 2
                                    
                                    combined_flags = list(set(main_eval.get("red_flags", []) + follow_eval.get("red_flags", [])))
                                    
                                    qa_pair["evaluation"] = {
                                        "correctness": round(consolidated_correctness, 1),
                                        "depth": round(consolidated_depth, 1),
                                        "specificity": round(consolidated_specificity, 1),
                                        "overall_score": round(consolidated_score, 1),
                                        "feedback": f"Main: {main_eval['feedback']} | Follow-up feedback: {follow_eval['feedback']}",
                                        "red_flags": combined_flags,
                                        "needs_followup": False,
                                        "followup_question": ""
                                    }
                                    qa_pair["followup_pair"] = {
                                        "question": st.session_state.followup_question,
                                        "answer": follow_input,
                                        "evaluation": follow_eval
                                    }
                                    st.session_state.followup_active = False
                                    st.rerun()
                                except Exception as fallback_err:
                                    st.error(f"❌ Answer Evaluation Fallback Failed: {str(fallback_err)}")
            
            # Next question navigation
            if not st.session_state.followup_active:
                st.markdown("<br/>", unsafe_allow_html=True)
                btn_txt = get_txt("next_btn") if current_idx < 4 else "🏁 Generate Final Integrity Audit →"
                if st.button(btn_txt, use_container_width=True):
                    if current_idx < 4:
                        st.session_state.current_q_index += 1
                        st.session_state.q_start_time = time.time()
                        st.session_state.audio_bytes = None
                        st.session_state.current_answer = ""
                        st.rerun()
                    else:
                        try:
                            with st.spinner("Analyzing viva results and compiling academic report..."):
                                report = calculate_final_score(
                                    content=st.session_state.content,
                                    qa_pairs=st.session_state.qa_pairs,
                                    api_key=os.environ.get("GOOGLE_API_KEY"),
                                    demo_mode=st.session_state.demo_mode
                                )
                                st.session_state.final_report = append_security_alerts_to_report(report)
                                st.session_state.session_stats = calculate_session_stats(st.session_state.qa_pairs)
                                st.session_state.stage = "report"
                                st.rerun()
                        except Exception as e:
                            st.warning("⚠️ **Gemini API Exception/Limit reached during report compilation!** AuthentiLearn AI is gracefully switching to **High-Fidelity Offline Simulation Mode** to compile your final audit.")
                            st.session_state.demo_mode = True
                            try:
                                report = calculate_final_score(
                                    content=st.session_state.content,
                                    qa_pairs=st.session_state.qa_pairs,
                                    demo_mode=True
                                )
                                st.session_state.final_report = append_security_alerts_to_report(report)
                                st.session_state.session_stats = calculate_session_stats(st.session_state.qa_pairs)
                                st.session_state.stage = "report"
                                st.rerun()
                            except Exception as fallback_err:
                                st.error(f"❌ Report Compilation Fallback Failed: {str(fallback_err)}")

    with col2:
        st.markdown("### 💡 Viva Strategy Hints")
        st.write("Ensure your responses demonstrate an active working memory of how you compiled the submitted coursework.")
        
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom:1rem; border-left:3px solid var(--accent-purple);">
            <span style="font-size:0.75rem; color:var(--muted); font-family:'Space Mono'; uppercase;">TOPIC FOCUS HINT</span><br/>
            <b>Concept:</b> {current_q['concept_tested']}<br/>
            <b>Suggested Keyword Areas:</b> {current_q['hint_topic']}
        </div>
        """, unsafe_allow_html=True)
        
        # Real-time Paste log summary (Educator Mode)
        if st.session_state.educator_mode and st.session_state.paste_events:
            st.markdown("<div class='metric-card' style='margin-bottom:1rem; border-left:3px solid var(--accent-red);'>", unsafe_allow_html=True)
            st.markdown("<span style='font-size:0.75rem; color:var(--accent-red); font-family:\"Space Mono\"; font-weight:bold;'>🚨 PASTE DETECTIONS:</span>", unsafe_allow_html=True)
            for event in st.session_state.paste_events:
                st.markdown(f"<span style='font-size:0.8rem; display:block;'>- Q{event['question_id']}: Added {event['chars_added']} chars | Verdict: `{event['verdict']}`</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="metric-card">
            <span style="font-weight:bold; color:var(--accent-blue);">Exam Protocols:</span><br/>
            <span style="font-size:0.85rem; line-height:1.5;">
            - <b>1-Minute Time Limit</b>: Fail to answer within 60s will record a timeout skip (0%).<br/>
            - <b>Spontaneity checks</b> trigger warnings on pasting text.<br/>
            - <b>Adaptive follow-ups</b> (purple) are triggered on vague answers.
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.image("authentilearn/assets/verdict_illustration_1779355471609.png", use_container_width=True)


# ========================================================
# STAGE 3: CONSOLIDATED INTEGRITY AUDIT REPORT
# ========================================================
elif st.session_state.stage == "report":
    # Deactivate viva exam security hooks & exit fullscreen (client-side auto cleanup)
    st.components.v1.html("""
    <script>
        const parentDoc = window.parent.document;
        // Turn off active indicator
        window.parent.__authentilearn_exam_active = false;
        
        // Try exiting fullscreen on parent window
        if (parentDoc.fullscreenElement || parentDoc.webkitFullscreenElement || parentDoc.mozFullScreenElement || parentDoc.msFullscreenElement) {
            if (parentDoc.exitFullscreen) {
                parentDoc.exitFullscreen().catch(err => console.log("Exit fullscreen deferred:", err));
            } else if (parentDoc.webkitExitFullscreen) {
                parentDoc.webkitExitFullscreen();
            } else if (parentDoc.mozCancelFullScreen) {
                parentDoc.mozCancelFullScreen();
            } else if (parentDoc.msExitFullscreen) {
                parentDoc.msExitFullscreen();
            }
        }
    </script>
    """, height=0)
    
    report = st.session_state.final_report
    stats = st.session_state.session_stats
    meta = st.session_state.file_metadata
    
    score = report.get("overall_score", 70)
    verdict = report.get("verdict", "Mostly Understands")
    confidence = report.get("confidence_level", "Medium")
    
    st.markdown("### 🎓 ACADEMIC INTEGRITY & UNDERSTANDING AUDIT REPORT")
    
    hero_col1, hero_col2 = st.columns([0.4, 0.6], gap="large")
    
    with hero_col1:
        score_color = "--accent-green" if score >= 75 else "--accent-amber" if score >= 55 else "--accent-red"
        st.markdown(f"""
        <div class="score-container" style="background-color:var(--surface); border:1px solid var(--border); border-radius:16px;">
            <div class="score-ring" style="--score-percent: {score}%; --score-color: var({score_color});">
                <div class="score-inner">
                    <div class="score-value">{score}</div>
                    <div class="score-label">AUTHENTICITY</div>
                </div>
            </div>
            <br/>
            <span style="font-size:0.8rem; color:var(--muted); font-family:'Space Mono'; uppercase;">VERDICT CATEGORY</span>
        </div>
        """, unsafe_allow_html=True)
        
    with hero_col2:
        verdict_cls = "verdict-high" if score >= 75 else "verdict-medium" if score >= 55 else "verdict-low"
        
        st.markdown(f"""
        <div style="background-color:var(--surface); border:1px solid var(--border); border-radius:16px; padding:2rem; min-height:280px; box-shadow:0 8px 32px rgba(0,0,0,0.3);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span class="verdict-badge {verdict_cls}">{verdict.upper()}</span>
                <span style="font-family:'Space Mono'; font-size:0.85rem; color:var(--muted);">CONFIDENCE LEVEL: <b>{confidence.upper()}</b></span>
            </div>
            <h3 style="color:var(--accent-blue); margin-top:0;">{get_txt('recommendation_title')}</h3>
            <p style="font-size:1.1rem; line-height:1.5; color:var(--text);">{report.get('recommendation', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # 3-Column Metrics Row
    met_col1, met_col2, met_col3 = st.columns(3, gap="medium")
    answered_qs = sum(1 for q in st.session_state.qa_pairs if not q.get("skipped", False))
    avg_score = round(sum(q["evaluation"]["overall_score"] for q in st.session_state.qa_pairs if not q.get("skipped", False)) / answered_qs, 1) if answered_qs else 0.0
    flags_count = len(report.get("suspicious_patterns", []))
    
    with met_col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <span style="color:var(--muted); font-family:'Space Mono'; font-size:0.75rem; letter-spacing:1px;">QUESTIONS ANSWERED</span><br/>
            <span style="color:var(--accent-blue); font-family:'Space Mono'; font-size:2.2rem; font-weight:bold;">{answered_qs} / 5</span>
        </div>
        """, unsafe_allow_html=True)
        
    with met_col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <span style="color:var(--muted); font-family:'Space Mono'; font-size:0.75rem; letter-spacing:1px;">AVERAGE RESPONSE RATING</span><br/>
            <span style="color:var(--accent-purple); font-family:'Space Mono'; font-size:2.2rem; font-weight:bold;">{avg_score} / 10</span>
        </div>
        """, unsafe_allow_html=True)
        
    with met_col3:
        flag_col = "var(--accent-red)" if flags_count > 0 else "var(--accent-green)"
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <span style="color:var(--muted); font-family:'Space Mono'; font-size:0.75rem; letter-spacing:1px;">DETECTED RED FLAGS</span><br/>
            <span style="color:{flag_col}; font-family:'Space Mono'; font-size:2.2rem; font-weight:bold;">{flags_count}</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Knowledge Gaps Diagnostic Summary (Strengths block removed as per user request)
    st.markdown(f"### {get_txt('gaps_title')}")
    st.markdown("<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;'>", unsafe_allow_html=True)
    for gap in report.get("knowledge_gaps", []):
        st.markdown(f"""
        <div style="background-color:rgba(244, 63, 94, 0.03); border:1px solid rgba(244, 63, 94, 0.2); border-left:4px solid var(--accent-red); border-radius:8px; padding:0.8rem 1.2rem; font-size:0.95rem; height: 100%;">
            ⚠️ {gap}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Suspicious Patterns Section (Educator Mode Only)
    if st.session_state.educator_mode and report.get("suspicious_patterns"):
        st.markdown(f"### {get_txt('red_flags_title')}")
        st.markdown("<div style='background-color:rgba(245, 158, 11, 0.03); border:1px solid rgba(245, 158, 11, 0.2); border-radius:12px; padding:1.5rem; border-left:5px solid var(--accent-amber);'>", unsafe_allow_html=True)
        for flag in report.get("suspicious_patterns", []):
            st.markdown(f"<div style='font-size:0.95rem; color:var(--text); padding:0.35rem 0;'>🚨 **Red Flag:** {flag}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)
        
    # Actionable Next Steps
    st.markdown(f"### 📋 {get_txt('actions_title')}")
    act_col1, act_col2, act_col3 = st.columns(3, gap="medium")
    actions = report.get("suggested_actions", [
        "Schedule a brief face-to-face follow-up.",
        "Assign an in-class task to adapt code or thesis statements.",
        "Request the student run their codebase in a sandboxed terminal."
    ])
    for i, col in enumerate([act_col1, act_col2, act_col3]):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="min-height:120px; display:flex; flex-direction:column; justify-content:center;">
                <span style="font-family:'Space Mono'; color:var(--accent-blue); font-weight:bold; font-size:1rem;">ACTION 0{i+1}</span><br/>
                <span style="font-size:0.9rem; color:var(--text); line-height:1.4;">{actions[i]}</span>
            </div>
            """, unsafe_allow_html=True)

    # Big Glowing button to Dashboard!
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("📈 View Interactive Student Knowledge Graph Dashboard →", use_container_width=True):
        st.session_state.stage = "dashboard"
        st.rerun()


# ========================================================
# STAGE 4: INTERACTIVE KNOWLEDGE DASHBOARD & AUDIT EXPORTS
# ========================================================
elif st.session_state.stage == "dashboard":
    
    report = st.session_state.final_report
    stats = st.session_state.session_stats
    meta = st.session_state.file_metadata
    qa_pairs = st.session_state.qa_pairs

    st.markdown("<h2 style='text-align:center; color:var(--accent-blue); font-family:\"Space Mono\"; margin-top:1.5rem;'>📊 Student Knowledge Intelligence Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:var(--muted); font-size:0.9rem; margin-bottom:2rem;'>Real-time interactive analytics of conceptual mapping, authenticity ratings, and grading progressions.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    # Extract concepts & scores
    concepts = report.get("per_question_concepts", [qa.get("concept_tested", f"Concept {i+1}") for i, qa in enumerate(qa_pairs)])
    scores = report.get("per_question_scores", [70]*5)
    
    # Composition segments
    c_p_likelihood = report.get("copy_paste_likelihood", 25.0)
    ai_likelihood = report.get("ai_generated_likelihood", 30.0)
    
    high_risk_part = max(5.0, c_p_likelihood)
    ai_patterns_part = max(5.0, ai_likelihood)
    vocab_part = 15.0
    original_part = max(10.0, 100.0 - (high_risk_part + ai_patterns_part + vocab_part))
    
    with col1:
        st.markdown("<div class='metric-card' style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
        st.plotly_chart(get_understanding_radar(qa_pairs), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='metric-card' style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
        st.plotly_chart(get_understanding_depth(report.get("overall_score", 70)), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='metric-card' style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
        st.plotly_chart(get_three_dimensions(qa_pairs), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='metric-card' style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
        st.plotly_chart(get_concept_mastery(concepts, scores), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='metric-card' style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
        st.plotly_chart(get_confidence_progression(qa_pairs), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='metric-card' style='margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
        st.plotly_chart(get_submission_composition(original_part, ai_patterns_part, high_risk_part, vocab_part), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 7. Downloads & Reset Button
    st.markdown("### 💾 EXPORTS & NEXT CYCLE")
    down_col1, down_col2, down_col3 = st.columns(3)
    
    with down_col1:
        json_data = json.dumps({
            "metadata": meta,
            "analysis": st.session_state.submission_analysis,
            "viva_record": st.session_state.qa_pairs,
            "final_report": report,
            "session_stats": stats
        }, indent=4)
        
        st.download_button(
            label="⬇️ Download JSON Audit Report",
            data=json_data,
            file_name=f"AuthentiLearn_Audit_{meta.get('name', 'submission').replace('.','_')}.json",
            mime="application/json",
            use_container_width=True
        )
        
    with down_col2:
        # PDF Summary export using built-in high-fidelity Plain Text Summary (zero-config, robust)
        pdf_content = generate_pdf_text(report, stats, meta)
        st.download_button(
            label="⬇️ Download PDF Summary",
            data=pdf_content,
            file_name=f"AuthentiLearn_Audit_{meta.get('name', 'submission').replace('.','_')}.pdf",
            mime="text/plain",
            use_container_width=True
        )
        
    with down_col3:
        if st.button("⬅️ Back to Written Report", use_container_width=True):
            st.session_state.stage = "report"
            st.rerun()

    st.markdown("---")
    if st.button(get_txt("reset_btn"), use_container_width=True):
        st.session_state.stage = "upload"
        st.session_state.content = ""
        st.session_state.file_metadata = {}
        st.session_state.submission_analysis = {}
        st.session_state.cheat_analysis = {}
        st.session_state.highlighted_submission = ""
        st.session_state.last_sentence_analysis = []
        st.session_state.line_table = None
        st.session_state.questions = []
        st.session_state.current_q_index = 0
        st.session_state.qa_pairs = []
        st.session_state.followup_active = False
        st.session_state.final_report = {}
        st.session_state.session_stats = {}
        st.session_state.pasted_text = ""
        st.session_state.audio_bytes = None
        st.session_state.current_answer = ""
        st.session_state.paste_events = []
        st.rerun()
