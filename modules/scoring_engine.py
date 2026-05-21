# File: authentilearn/modules/scoring_engine.py
import os
import json
from google import genai
from utils.prompts import FINAL_SCORE_PROMPT
from modules.question_engine import parse_json_safely, get_gemini_client

def get_dynamic_demo_report(qa_pairs) -> dict:
    """
    Dynamically generates a realistic evaluation report in Demo Mode
    based on the student's actual performance.
    """
    scores = []
    red_flags = []
    strengths = []
    gaps = []
    
    for qa in qa_pairs:
        eval_data = qa.get("evaluation", {})
        score = eval_data.get("overall_score", 5.0) * 10
        scores.append(int(score))
        red_flags.extend(eval_data.get("red_flags", []))
        
        # Categorize strengths vs gaps per question
        concept = qa.get("concept_tested", "Submission Topics")
        difficulty = qa.get("difficulty", "medium")
        if score >= 70:
            strengths.append(f"Demonstrated solid understanding of {concept} ({difficulty} level) with {int(score)}% score.")
        else:
            gaps.append(f"Showed difficulty or lack of depth in {concept} ({difficulty} level) with {int(score)}% score.")

    overall_score = int(sum(scores) / len(scores)) if scores else 70
    
    # Ensure there's always default data
    if not strengths:
        strengths = [
            "Correctly explained train_test_split purpose and split ratios",
            "Understood Random Forest ensemble advantage over a single decision tree"
        ]
    if not gaps:
        gaps = [
            "Could not explain imbalanced dataset implications and accuracy paradox",
            "Vague on advanced explainability frameworks like SHAP or LIME"
        ]
        
    # Verdict assignment
    if overall_score >= 75:
        verdict = "Highly Likely Author"
        confidence_level = "High"
        recommendation = f"The student shows excellent command of their submission (Authenticity Score: {overall_score}%). They explained core architectural decisions, preprocessing models, and edge cases clearly. High integrity validation."
    elif overall_score >= 55:
        verdict = "Mostly Understands"
        confidence_level = "Medium"
        recommendation = f"The student demonstrated decent working knowledge (Authenticity Score: {overall_score}%) but displayed minor depth gaps. They likely collaborated or used AI assistance for advanced sections but understand the core concepts."
    elif overall_score >= 35:
        verdict = "Partial Understanding"
        confidence_level = "Medium"
        recommendation = f"The student failed to explain several key aspects of the submission (Authenticity Score: {overall_score}%). They relied on generic responses and struggled with application or edge case questions. Suggestive of outsourced work or copying."
    else:
        verdict = "Likely Not Author"
        confidence_level = "Low"
        recommendation = f"The student showed severe conceptual deficits and was unable to answer or explain basic details (Authenticity Score: {overall_score}%). Multiple red flags and severe mismatch suggest they did not write the submitted work."
        
    suggested_actions = [
        "Schedule a brief face-to-face follow-up specifically on model explainability and SHAP values.",
        "Assign an in-class task to adapt the preprocessing pipeline for a different column type.",
        "Request the student run their code in a sandboxed terminal and explain live runtime modifications."
    ]
    
    return {
        "overall_score": overall_score,
        "verdict": verdict,
        "confidence_level": confidence_level,
        "strengths": strengths[:4],
        "knowledge_gaps": gaps[:4],
        "suspicious_patterns": list(set(red_flags)) if red_flags else ["Generic hedging or lack of detail"],
        "per_question_scores": scores if len(scores) == 5 else (scores + [70]*(5-len(scores))),
        "recommendation": recommendation,
        "suggested_actions": suggested_actions
    }

def calculate_final_score(content: str, qa_pairs: list[dict], api_key: str = None, demo_mode: bool = False) -> dict:
    """
    Consolidates the complete viva record to generate the final educator authenticity report.
    """
    if demo_mode:
        return get_dynamic_demo_report(qa_pairs)
        
    # Format the viva record as text for Gemini
    viva_record_list = []
    for i, qa in enumerate(qa_pairs):
        eval_data = qa.get("evaluation", {})
        viva_record_list.append(
            f"Question {i+1}: {qa['question']}\n"
            f"Concept Tested: {qa.get('concept_tested', 'N/A')} | Difficulty: {qa.get('difficulty', 'N/A')}\n"
            f"Student Answer: {qa['answer']}\n"
            f"Evaluation Score: {eval_data.get('overall_score', 0.0)}/10\n"
            f"Feedback: {eval_data.get('feedback', '')}\n"
            f"Red Flags: {', '.join(eval_data.get('red_flags', [])) or 'None'}\n"
            f"----------------------------------------"
        )
    viva_record_str = "\n".join(viva_record_list)
    
    truncated_content = content[:3000] # Safe sizing for tokens
    summary_info = f"Length: {len(content)} characters. Content Sample: {truncated_content[:500]}..."
    
    prompt = FINAL_SCORE_PROMPT.format(
        summary=summary_info,
        viva_record=viva_record_str
    )
    
    client = get_gemini_client(api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    report = parse_json_safely(response.text, None)
    
    if not report or not isinstance(report, dict):
        raise ValueError("Gemini returned an invalid final score report format. Please retry compiling.")
        
    # Ensure all required keys exist and are in appropriate ranges
    required_keys = ["overall_score", "verdict", "confidence_level", "strengths", "knowledge_gaps", "suspicious_patterns", "per_question_scores", "recommendation", "suggested_actions"]
    for key in required_keys:
        if key not in report:
            raise ValueError(f"Missing required report field: '{key}' in Gemini response.")
            
    # Validate verdict types
    valid_verdicts = ["Highly Likely Author", "Mostly Understands", "Partial Understanding", "Likely Not Author"]
    if report["verdict"] not in valid_verdicts:
        # Match by score ranges
        score = report["overall_score"]
        if score >= 75:
            report["verdict"] = "Highly Likely Author"
        elif score >= 55:
            report["verdict"] = "Mostly Understands"
        elif score >= 35:
            report["verdict"] = "Partial Understanding"
        else:
            report["verdict"] = "Likely Not Author"
            
    return report
