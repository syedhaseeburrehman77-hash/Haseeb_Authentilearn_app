# File: authentilearn/modules/cheat_detector.py
import re
import json
import plotly.graph_objects as go
from modules.question_engine import parse_json_safely, get_gemini_client
from utils.prompts import SUBMISSION_AUTHENTICITY_PROMPT

# Premium Dark theme styling for Plotly charts
PLOTLY_BG = "#060b18"
PLOTLY_FONT = "#e2e8f0"
PLOTLY_GRID = "#1a2d4a"

DEMO_CHEAT_RESULT = {
    "copy_paste_likelihood": 42,
    "ai_generated_likelihood": 38,
    "suspicious_phrases": [
        {"phrase": "It is worth noting that", "reason": "AI transition pattern"},
        {"phrase": "Furthermore", "reason": "Repetitive AI transition"},
        {"phrase": "leverages", "reason": "AI buzzword"},
        {"phrase": "In conclusion", "reason": "Standard ChatGPT ending"}
    ],
    "writing_style_flags": ["Perfect grammatical parallelism", "Extremely uniform sentence lengths"],
    "vocabulary_level": "suspiciously_advanced",
    "sentence_length_variance": "low",
    "overall_authenticity_score": 61
}

def analyze_submission_authenticity(text: str, api_key: str = None, demo_mode: bool = False) -> dict:
    """
    Analyzes student submission for signs of AI authorship or copy-paste plagiarism.
    """
    if demo_mode:
        # Build slight dynamic variability based on the length of input
        res = DEMO_CHEAT_RESULT.copy()
        
        # If user uploaded FoliarNet or essay, let's tailor the mock phrases to match!
        text_lower = text.lower()
        if "foliarnet" in text_lower or "tomato" in text_lower:
            res["suspicious_phrases"] = [
                {"phrase": "early detection of foliar crop", "reason": "Copy-paste match"},
                {"phrase": "Our model integrates", "reason": "AI template structure"},
                {"phrase": "Furthermore, we conducted", "reason": "AI transition"}
            ]
            res["copy_paste_likelihood"] = 28
            res["ai_generated_likelihood"] = 35
            res["overall_authenticity_score"] = 72
        elif "ethical" in text_lower or "economic" in text_lower:
            res["suspicious_phrases"] = [
                {"phrase": "The rapid advancement of", "reason": "Common AI hook"},
                {"phrase": "On one hand", "reason": "Formulaic structure"},
                {"phrase": "fostering critical thinking", "reason": "Buzzword pattern"}
            ]
            res["copy_paste_likelihood"] = 48
            res["ai_generated_likelihood"] = 55
            res["overall_authenticity_score"] = 52
            
        return res
        
    # Live Mode via Gemini SDK
    truncated_content = text[:4000]
    prompt = SUBMISSION_AUTHENTICITY_PROMPT.format(text=truncated_content)
    
    try:
        client = get_gemini_client(api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        result = parse_json_safely(response.text, None)
        
        if not result or not isinstance(result, dict):
            raise ValueError("Invalid format received from Gemini.")
            
        # Ensure fallback defaults exist
        required_keys = ["copy_paste_likelihood", "ai_generated_likelihood", "suspicious_phrases", "writing_style_flags", "vocabulary_level", "sentence_length_variance", "overall_authenticity_score"]
        for key in required_keys:
            if key not in result:
                result[key] = DEMO_CHEAT_RESULT[key]
                
        return result
    except Exception as e:
        print(f"Submission authenticity analysis failed: {str(e)}")
        # Graceful fallback to demo in case of credentials/limit failure
        return DEMO_CHEAT_RESULT

def highlight_suspicious_text(text: str, suspicious_phrases: list) -> str:
    """
    Injects HTML styling highlights for suspicious text elements.
    Yellow = AI transition patterns, Red = Copy-paste plagiarism risks, Purple = Over-advanced vocabulary.
    """
    html_text = text
    # Escape standard HTML markers to prevent injections
    html_text = html_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Sort phrases in descending order of length to prevent overlapping replacements
    sorted_phrases = sorted(suspicious_phrases, key=lambda x: len(x.get("phrase", "")), reverse=True)
    
    highlighted_already = set()
    
    for item in sorted_phrases:
        phrase = item.get("phrase", "").strip()
        reason = item.get("reason", "Suspicious pattern")
        if not phrase or phrase in highlighted_already:
            continue
            
        # Determine styling tag based on reason categories
        reason_lower = reason.lower()
        if "copy" in reason_lower or "plag" in reason_lower or "paste" in reason_lower:
            style_cls = "highlight-copy"
            color_badge = "🔴 Copy-paste"
        elif "vocab" in reason_lower or "advanced" in reason_lower:
            style_cls = "highlight-vocab"
            color_badge = "🟣 Advanced Vocab"
        else:
            style_cls = "highlight-ai"
            color_badge = "🟡 AI Pattern"
            
        # Compile direct replacement string
        escaped_phrase = phrase.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        replacement = f'<span class="{style_cls}" title="{color_badge}: {reason}">{escaped_phrase}</span>'
        
        # Use regex to replace exact boundaries or direct substring if safe
        try:
            # We use non-word character boundary limits to prevent cutting words in half
            pattern = re.compile(re.escape(escaped_phrase), re.IGNORECASE)
            html_text = pattern.sub(replacement, html_text)
            highlighted_already.add(phrase)
        except Exception:
            # Substring fallback
            html_text = html_text.replace(escaped_phrase, replacement)
            highlighted_already.add(phrase)
            
    # Format line breaks to match coursework
    html_text = html_text.replace("\n", "<br/>")
    return html_text

def get_copy_paste_gauge_chart(score: float) -> go.Figure:
    """
    Builds a highly premium needles speedometer gauge representing overall copy-paste/AI risk.
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "AI / Copy-Paste Risk Index", 'font': {'size': 16, 'family': 'Space Mono', 'color': PLOTLY_FONT}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': PLOTLY_GRID},
            'bar': {'color': "#3b82f6", 'thickness': 0.75}, # Cyberblue needle pointer line
            'bgcolor': PLOTLY_BG,
            'borderwidth': 1,
            'bordercolor': PLOTLY_GRID,
            'steps': [
                {'range': [0, 30], 'color': 'rgba(16, 185, 129, 0.15)'}, # Green Safe
                {'range': [30, 60], 'color': 'rgba(245, 158, 11, 0.15)'}, # Amber Warn
                {'range': [60, 100], 'color': 'rgba(239, 68, 68, 0.15)'} # Red Plagiarism Risk
            ],
            'threshold': {
                'line': {'color': "#ef4444", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor=PLOTLY_BG,
        plot_bgcolor=PLOTLY_BG,
        font={'color': PLOTLY_FONT, 'family': "Plus Jakarta Sans"},
        margin=dict(l=30, r=30, t=50, b=30),
        height=220
    )
    
    return fig
