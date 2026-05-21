# File: authentilearn/utils/prompts.py

QUESTION_GEN_PROMPT = """You are an elite academic examiner conducting an oral viva (verbal examination) to assess if a student truly understands their submitted assignment.
Your task is to analyze the student's submission below and generate exactly 5 deep, highly specific viva-style questions.

SUBMISSION CONTENT:
---
{content}
---

RULES FOR QUESTION GENERATION:
1. SPECIFICITY: The questions must be deeply customized to the provided text. Refrain from general or boilerplate questions. A student who has just read a generic tutorial or Googled the topic should NOT be able to answer these. They must have understood THIS specific implementation or thesis.
2. COMPOSITION MIX:
   - 2 Conceptual questions: Focused on "why" or "how" specific decisions, arguments, or lines of code were executed.
   - 2 Application questions: Focused on "what if" scenarios, hypothetical modifications, or what happens if we change parameter X or section Y.
   - 1 Edge Case / Gotcha question: Focused on constraints, limitations, failure points, or specific edge behaviors in the submission.
3. DIFFICULTY GRADIENT:
   - Q1: Easy (Conceptual)
   - Q2: Easy (Conceptual/Application)
   - Q3: Medium (Application)
   - Q4: Medium (Application/Edge Case)
   - Q5: Hard (Gotcha/Advanced Conceptual)
4. STRUCTURE: Each question MUST be represented as a JSON object containing:
   - "id": integer (1 to 5)
   - "question": string (the exact text of the question)
   - "difficulty": string ("easy", "medium", or "hard")
   - "concept_tested": string (the core concept, e.g., "Ensemble Methods", "Data Preprocessing", "Ethical Implications")
   - "hint_topic": string (a short hint or keywords indicating what the student should focus on to answer)

OUTPUT FORMAT:
Return ONLY a valid JSON array of these 5 question objects. Do not wrap the JSON in markdown code blocks (like ```json), do not include any preamble, introduction, or postscript. Begin your response with "[" and end with "]".
"""

EVALUATE_ANSWER_PROMPT = """You are an expert examiner. Evaluate the student's answer to a viva question based on the provided submission.

SUBMISSION CONTENT:
---
{content}
---

QUESTION ASKED:
{question}

STUDENT'S ANSWER:
{answer}

Your task is to analyze the student's answer and produce a detailed evaluation JSON object. 

EVALUATION CRITERIA (0 to 10 points each):
1. "correctness": Is the answer factually and logically accurate relative to the submission and domain?
2. "depth": Does the answer show genuine, conceptual understanding of the underlying principles, or is it a surface-level repetition of definitions?
3. "specificity": Does the student refer to concrete details and specific decisions in their submission, or are they using vague, generic hedging?

REQUIRED JSON OUTPUT KEYS:
- "correctness": number (0-10)
- "depth": number (0-10)
- "specificity": number (0-10)
- "overall_score": number (0-10, weighted average based on depth and correctness)
- "feedback": string (2-3 sentences of direct, constructive, and highly specific feedback)
- "red_flags": list of strings (suspicious patterns. e.g. "uses advanced jargon not found in submission", "contradicts their own written submission", "avoids addressing the specific question", "vague AI-style conversational filler"). If none, return an empty list [].
- "needs_followup": boolean (true if the answer was incomplete, raised a new red flag, or was highly vague, indicating that a follow-up question is necessary to confirm understanding. Otherwise false.)
- "followup_question": string (if needs_followup is true, provide an adaptive, pointed follow-up question digging deeper into their response. If false, return empty string "").

OUTPUT FORMAT:
Return ONLY a valid JSON object. Do not wrap the JSON in markdown code blocks (like ```json), do not include any preamble, introduction, or postscript. Begin your response with "{{" and end with "}}".
"""

SUMMARY_ANALYSIS_PROMPT = """Analyze the following student submission and extract high-level metadata and diagnostic summaries.

SUBMISSION TEXT:
---
{content}
---

REQUIRED JSON OUTPUT KEYS:
- "subject_area": string (e.g. "Machine Learning", "Web Development", "Microeconomics", "Modern Poetry Analysis")
- "complexity_level": string (strictly one of: "beginner", "intermediate", "advanced")
- "key_concepts": list of exactly 5 strings (the core topics or technologies demonstrated, e.g. ["Random Forest", "Feature Engineering", "Overfitting", "K-Fold Cross-Validation", "Imbalanced Data"])
- "word_count": integer (approximate word count)
- "estimated_read_time": string (estimated reading time, e.g., "3 mins")
- "ai_written_likelihood": string (strictly one of: "Low", "Medium", "High")
- "ai_written_reasoning": string (1-2 sentences of explanation for the AI-likelihood estimate, citing patterns like highly repetitive sentence structures, uniform complexity, lack of personal narrative, or generic phrasing).

OUTPUT FORMAT:
Return ONLY a valid JSON object. Do not wrap the JSON in markdown code blocks (like ```json), do not include any preamble, introduction, or postscript. Begin your response with "{{" and end with "}}".
"""

FINAL_SCORE_PROMPT = """You are the Lead Auditor of Academic Integrity. Review the summary of the submission and the detailed history of the student's oral viva (questions, answers, and evaluations) to compile a definitive Authenticity Evaluation & Educator Report.

SUBMISSION SUMMARY:
{summary}

ORAL VIVA RECORD:
{viva_record}

Your task is to analyze this performance and compute a comprehensive final authenticity report.

VERDICT RULES:
- "Highly Likely Author" (Overall Score: 75-100): The student answered almost all questions correctly, provided excellent depth and specific details, and showed high alignment with the submission contents. No major red flags.
- "Mostly Understands" (Overall Score: 55-74): The student understands the general framework, but struggled with medium/hard questions, had minor depth deficiencies, or minor specific knowledge gaps.
- "Partial Understanding" (Overall Score: 35-54): The student showed serious gaps in conceptual understanding, failed multiple medium/hard questions, or answered with generic hedging. Several red flags.
- "Likely Not Author" (Overall Score: 0-34): The student was unable to explain basic decisions in the code/text, showed extreme mismatch with the text, had persistent red flags, or was unable to answer. Highly likely they did not write/author the work.

REQUIRED JSON OUTPUT KEYS:
- "overall_score": number (0 to 100 representing the consolidated authenticity/understanding score)
- "verdict": string (must be exactly one of: "Highly Likely Author", "Mostly Understands", "Partial Understanding", "Likely Not Author")
- "confidence_level": string (strictly one of: "High", "Medium", "Low")
- "strengths": list of 3 to 5 strings (concrete positive elements shown in the viva)
- "knowledge_gaps": list of 3 to 5 strings (areas where the student showed lack of understanding)
- "suspicious_patterns": list of strings (consolidated list of suspicious patterns or red flags across all questions, if any)
- "per_question_scores": list of numbers (exactly 5 integers, one per question index, matching the overall score awarded out of 100 for each of the 5 questions, e.g. [90, 85, 70, 50, 40] to be used in a Plotly radar chart)
- "recommendation": string (2-3 sentences of educator recommendation explaining what this viva profile means for the student's grade and how the educator should proceed)
- "suggested_actions": list of exactly 3 strings (concrete, actionable next steps for the educator, e.g., "Schedule a brief face-to-face follow-up", "Assign an alternative in-class writing exercise", "Validate code execution in a sandbox environment").

OUTPUT FORMAT:
Return ONLY a valid JSON object. Do not wrap the JSON in markdown code blocks (like ```json), do not include any preamble, introduction, or postscript. Begin your response with "{{" and end with "}}".
"""

SUBMISSION_AUTHENTICITY_PROMPT = """You are an elite AI forensics and academic integrity analyst.
Analyze the following student submission text and identify signs of AI authorship (burstiness, perplexity, formulaic structures) or copy-paste plagiarism (density of phrasing, transition words, advanced vocab).

SUBMISSION TEXT:
---
{text}
---

Your task is to produce a detailed analysis JSON object with these EXACT keys:
- "copy_paste_likelihood": number (0 to 100 representing copy-paste plagiarism probability)
- "ai_generated_likelihood": number (0 to 100 representing AI generation probability)
- "suspicious_phrases": a list of objects where each object has:
  - "phrase": string (the exact sequence of words from the submission that looks suspicious, e.g. a copy-pasted sentence or a formulaic AI transition phrase)
  - "reason": string (explanation of why it is flagged, e.g. "AI template phrase", "suspiciously advanced vocabulary", "plagiarized source match")
- "writing_style_flags": list of strings (style markers, e.g., "Extremely uniform sentence lengths", "Lack of spelling errors", "Over-balanced paragraphs")
- "vocabulary_level": string (strictly one of: "standard", "slightly_advanced", "suspiciously_advanced")
- "sentence_length_variance": string (strictly one of: "low", "medium", "high")
- "overall_authenticity_score": number (0 to 100, where higher means more authentic/student-written, lower means suspicious)

OUTPUT FORMAT:
Return ONLY a valid JSON object. Do not wrap the JSON in markdown code blocks (like ```json), do not include any preamble, introduction, or postscript. Begin your response with "{{" and end with "}}".
"""

LINE_BY_LINE_PROMPT = """You are a meticulous line-by-line coursework evaluator.
Analyze each sentence in the following numbered list of sentences extracted from a student submission. Evaluate each sentence on its authenticity and formulate a highly specific, targeted viva-style question testing the student's understanding of that line.

NUMBERED SENTENCES TO ANALYZE:
{lines}

Your task is to return a JSON array containing an evaluation object for each line in order. Each object must have these EXACT keys:
- "line_number": integer (matching the input line number)
- "authenticity_score": number (0 to 100 representing the authenticity score for this specific sentence)
- "flag": string (strictly one of: "clean", "suspicious", "likely_ai")
- "reason": string (explanation of why it received that score or flag)
- "suggested_viva_question": string (a deeply targeted, custom viva question that asks the student to explain, modify, or defend the technical/conceptual choice made in this specific sentence)

OUTPUT FORMAT:
Return ONLY a valid JSON array of these objects. Do not wrap the JSON in markdown code blocks (like ```json), do not include any preamble, introduction, or postscript. Begin your response with "[" and end with "]".
"""

REALTIME_ANSWER_CHEAT_PROMPT = """You are an expert oral examiner assessing a student's live verbal response.
Analyze the student's answer to the viva question and detect signs of pre-prepared copy-pasted scripts, googling, or AI assistance (highly formal passive jargon, lack of normal human speech disfluencies, direct pasting, etc.).

VIVA QUESTION:
{question}

STUDENT'S ANSWER:
{answer}

Your task is to return a JSON object with these EXACT keys:
- "live_answer_score": number (0 to 100 representing answer authenticity and naturalness)
- "cheating_indicators": list of strings (flagged cues, e.g. "sudden tone shift", "highly formal pre-written structure")
- "suspicious_phrases_in_answer": list of strings (exact phrases in their answer that look copied or AI-generated)
- "verdict": string (strictly one of: "clean", "prepared_answer", "likely_googled")
- "confidence": string (strictly one of: "high", "medium", "low")

OUTPUT FORMAT:
Return ONLY a valid JSON object. Do not wrap the JSON in markdown code blocks (like ```json), do not include any preamble, introduction, or postscript. Begin your response with "{{" and end with "}}".
"""

