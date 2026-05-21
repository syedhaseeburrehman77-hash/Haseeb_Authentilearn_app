# File: authentilearn/modules/viva_engine.py
import os
import json
from google import genai
from utils.prompts import EVALUATE_ANSWER_PROMPT
from modules.question_engine import parse_json_safely, get_gemini_client

DEMO_EVALUATIONS = {
    1: {
        "correctness": 9,
        "depth": 8,
        "specificity": 9,
        "overall_score": 8.7,
        "feedback": "Superb explanation of the train_test_split partitioning. You correctly highlighted how the 80/20 split behaves and why a random_state is critical for reproducibility.",
        "red_flags": [],
        "needs_followup": False,
        "followup_question": ""
    },
    2: {
        "correctness": 8,
        "depth": 8,
        "specificity": 7,
        "overall_score": 7.8,
        "feedback": "Good comparison between decision tree bagging vs a single tree's high variance. However, you could have mentioned out-of-bag error estimation as an additional benefit.",
        "red_flags": [],
        "needs_followup": True,
        "followup_question": "That makes sense. Can you explain what 'bagging' actually does to the features selected at each node split?"
    },
    3: {
        "correctness": 5,
        "depth": 4,
        "specificity": 4,
        "overall_score": 4.5,
        "feedback": "You correctly identified that 94% accuracy could be misleading on an imbalanced dataset, but failed to explain how that accuracy relates to the minority class. Your response lacked mention of precision or recall metrics.",
        "red_flags": ["Confused about baseline classification rates", "Relies heavily on vague terminology"],
        "needs_followup": False,
        "followup_question": ""
    },
    4: {
        "correctness": 8,
        "depth": 7,
        "specificity": 8,
        "overall_score": 7.7,
        "feedback": "Good application logic. You correctly selected median imputation for numeric attributes to mitigate outliers and integrated it well within a scikit-learn Pipeline.",
        "red_flags": [],
        "needs_followup": False,
        "followup_question": ""
    },
    5: {
        "correctness": 4,
        "depth": 3,
        "specificity": 3,
        "overall_score": 3.4,
        "feedback": "Very generic answer. You mentioned 'looking at the graphs' but showed zero awareness of modern explainability toolkits like SHAP or LIME, which were crucial for class-level breakdowns in this codebase.",
        "red_flags": ["Unfamiliar with explainability frameworks used in submission", "Evasive and non-technical phrasing"],
        "needs_followup": False,
        "followup_question": ""
    }
}

def evaluate_answer(content: str, question: str, answer: str, api_key: str = None, demo_mode: bool = False, q_id: int = 1, is_followup: bool = False) -> dict:
    """
    Evaluates a student's answer to a given question relative to their submission.
    """
    if demo_mode:
        ans_len = len(answer.strip())
        if ans_len < 15:
            return {
                "correctness": 2,
                "depth": 1,
                "specificity": 1,
                "overall_score": 1.3,
                "feedback": "The answer was extremely short or evasive, providing no technical or conceptual substance to demonstrate actual understanding.",
                "red_flags": ["Answer is too brief to evaluate", "Avoids discussing specific details"],
                "needs_followup": False,
                "followup_question": ""
            }
            
        demo_eval = DEMO_EVALUATIONS.get(q_id, {
            "correctness": 7,
            "depth": 7,
            "specificity": 7,
            "overall_score": 7.0,
            "feedback": "Standard demo evaluation. The answer is reasonable and demonstrates a working understanding of the topic.",
            "red_flags": [],
            "needs_followup": False,
            "followup_question": ""
        })
        
        # If it is a follow-up answer, clear out followup flags to prevent nested loops
        if is_followup:
            final_eval = demo_eval.copy()
            final_eval["needs_followup"] = False
            final_eval["followup_question"] = ""
            final_eval["overall_score"] = min(10.0, final_eval["overall_score"] + 1.0)  # minor boost for trying follow-up
            return final_eval
            
        return demo_eval

    # Live Mode via Gemini SDK
    truncated_content = content[:4000]
    prompt = EVALUATE_ANSWER_PROMPT.format(
        content=truncated_content,
        question=question,
        answer=answer
    )
    
    # We do not catch exceptions here so that the app.py handles them explicitly,
    # giving the user immediate visual visibility into Gemini API downtime or token exhausts.
    client = get_gemini_client(api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    evaluation = parse_json_safely(response.text, None)
    
    if not evaluation or not isinstance(evaluation, dict):
        raise ValueError("Gemini returned an invalid answer evaluation format. Please resubmit.")
        
    # Validate keys
    required_keys = ["correctness", "depth", "specificity", "overall_score", "feedback", "red_flags", "needs_followup", "followup_question"]
    for key in required_keys:
        if key not in evaluation:
            raise ValueError(f"Missing required evaluation attribute: '{key}'")
            
    # Ensure red_flags is a list
    if not isinstance(evaluation["red_flags"], list):
        evaluation["red_flags"] = [str(evaluation["red_flags"])] if evaluation["red_flags"] else []
        
    return evaluation
ZOOM = 1.0
