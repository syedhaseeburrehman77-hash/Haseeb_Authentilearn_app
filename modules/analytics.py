# File: authentilearn/modules/analytics.py

def calculate_session_stats(qa_pairs: list[dict]) -> dict:
    """
    Computes session analytics including average answer length, total duration,
    skip rates, score progression, strongest/weakest areas, and confidence metrics.
    """
    if not qa_pairs:
        return {
            "avg_answer_length": 0,
            "total_time_seconds": 0,
            "skip_rate": 0.0,
            "score_progression": [],
            "strongest_area": "N/A",
            "weakest_area": "N/A",
            "confidence_signals": []
        }
        
    total_words = 0
    answered_count = 0
    total_time = 0.0
    score_progression = []
    
    concepts_scores = {}
    confidence_signals = []
    
    for i, qa in enumerate(qa_pairs):
        ans = qa.get("answer", "").strip()
        time_taken = qa.get("time_taken", 0.0)
        total_time += time_taken
        
        concept = qa.get("concept_tested", f"Topic {i+1}")
        
        # Check if skipped
        is_skipped = qa.get("skipped", False) or ans.lower() == "skipped" or not ans
        
        if is_skipped:
            score_progression.append(0)
            confidence_signals.append(f"Q{i+1} ({concept}): Skipped (No Confidence)")
            concepts_scores[concept] = 0.0
            continue
            
        answered_count += 1
        words = len(ans.split())
        total_words += words
        
        eval_data = qa.get("evaluation", {})
        # Score out of 100
        score = eval_data.get("overall_score", 5.0) * 10
        score_progression.append(int(score))
        
        concepts_scores[concept] = score
        
        # Confidence logic based on answer time
        if time_taken < 15.0:
            speed = "Rapid response (High Confidence)"
        elif time_taken <= 45.0:
            speed = "Steady response (Medium Confidence)"
        else:
            speed = "Deliberate response (Uncertain / Pondering)"
            
        confidence_signals.append(f"Q{i+1} ({concept}): {speed} in {round(time_taken, 1)}s")

    avg_len = round(total_words / answered_count) if answered_count > 0 else 0
    skip_rate = round((len(qa_pairs) - answered_count) / len(qa_pairs) * 100, 1) if qa_pairs else 0.0
    
    # Identify strongest and weakest areas
    strongest_area = "N/A"
    weakest_area = "N/A"
    if concepts_scores:
        strongest_area = max(concepts_scores, key=concepts_scores.get)
        weakest_area = min(concepts_scores, key=concepts_scores.get)
        
    return {
        "avg_answer_length": avg_len,
        "total_time_seconds": round(total_time, 1),
        "skip_rate": skip_rate,
        "score_progression": score_progression,
        "strongest_area": strongest_area,
        "weakest_area": weakest_area,
        "confidence_signals": confidence_signals
    }
