# File: authentilearn/modules/question_engine.py
import os
import json
import re
from google import genai
from utils.prompts import QUESTION_GEN_PROMPT, SUMMARY_ANALYSIS_PROMPT

# Realistic fallback/demo data for a Python ML assignment
DEMO_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the purpose of train_test_split in your code and what parameters did you use?",
        "difficulty": "easy",
        "concept_tested": "Data Splitting",
        "hint_topic": "Train-test partition ratios, random state consistency"
    },
    {
        "id": 2,
        "question": "Why did you choose a Random Forest over a simple Decision Tree for this classification task?",
        "difficulty": "easy",
        "concept_tested": "Ensemble Methods",
        "hint_topic": "Overfitting mitigation, variance reduction, voting classifiers"
    },
    {
        "id": 3,
        "question": "Your accuracy is 94%. What does this mean if the dataset is imbalanced with 94% class A?",
        "difficulty": "medium",
        "concept_tested": "Imbalanced Data & Evaluation Metrics",
        "hint_topic": "Accuracy paradox, precision, recall, confusion matrix"
    },
    {
        "id": 4,
        "question": "How would your preprocessing pipeline change if you received new data with missing values in the 'age' column?",
        "difficulty": "medium",
        "concept_tested": "Data Imputation & Preprocessing",
        "hint_topic": "Mean/median imputation, KNN imputer, pipeline integration"
    },
    {
        "id": 5,
        "question": "If you had to explain why your model predicted class B for a specific input, what technique would you use and why?",
        "difficulty": "hard",
        "concept_tested": "Model Explainability (XAI)",
        "hint_topic": "SHAP (Shapley Additive exPlanations), LIME, feature importance plots"
    }
]

DEMO_ANALYSIS = {
    "subject_area": "Machine Learning (Supervised Classification)",
    "complexity_level": "advanced",
    "key_concepts": ["Random Forest Classifier", "Feature Engineering", "Imbalanced Classes", "Pipeline Imputation", "Model Interpretability (SHAP/LIME)"],
    "word_count": 850,
    "estimated_read_time": "4 mins",
    "ai_written_likelihood": "High",
    "ai_written_reasoning": "The pipeline structure displays extremely uniform scikit-learn syntax, optimal preprocessors, and near-perfect comments, suggesting AI generation (e.g. ChatGPT)."
}

def clean_json_response(text: str) -> str:
    """
    Cleans raw LLM response by stripping markdown blocks, whitespace,
    and returns a clean JSON string.
    """
    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    # Find first '[' or '{' and last ']' or '}' to isolate JSON
    match = re.search(r'([\[{].*[\]}])', cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)
    return cleaned

def parse_json_safely(text: str, fallback_obj):
    """
    Safely parses JSON with a robust fallback.
    """
    cleaned = clean_json_response(text)
    try:
        return json.loads(cleaned)
    except Exception as e:
        print(f"JSON Parsing Error: {str(e)} for cleaned text: {cleaned}")
        return fallback_obj

def get_gemini_client(api_key: str = None) -> genai.Client:
    """
    Initializes and returns a Google GenAI Client.
    """
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError("Google API Key not found. Please provide an API key in the sidebar or toggle Demo Mode.")
    return genai.Client(api_key=key)

def generate_questions(content: str, api_key: str = None, demo_mode: bool = False) -> list[dict]:
    """
    Generates exactly 5 specific viva questions using Gemini.
    """
    if demo_mode:
        # Check if the content is one of our default demos to return perfect custom sets
        content_lower = content.lower()
        if "telecom_churn" in content_lower or "randomforestclassifier" in content_lower:
            return DEMO_QUESTIONS
        elif "tomato" in content_lower or "foliarnet" in content_lower:
            return [
                {
                    "id": 1,
                    "question": "What is the architecture of FoliarNet and how does it optimize tomato leaf pathogen classification?",
                    "difficulty": "easy",
                    "concept_tested": "Model Architecture",
                    "hint_topic": "Depthwise separable convolutions, computational efficiency, attention-gated layer"
                },
                {
                    "id": 2,
                    "question": "Why did you choose low-altitude aerial imagery from multi-spectral drone sensors instead of standard RGB cameras?",
                    "difficulty": "easy",
                    "concept_tested": "Data Acquisition",
                    "hint_topic": "Multi-spectral features, chlorotic and necrotic margin differentiation"
                },
                {
                    "id": 3,
                    "question": "Your model achieved 96.8% accuracy. How do you guarantee the model isn't learning background soil noise instead of crop disease?",
                    "difficulty": "medium",
                    "concept_tested": "Model Validation",
                    "hint_topic": "Grad-CAM saliency mapping, saliency visual boundaries, soil bias"
                },
                {
                    "id": 4,
                    "question": "How does depthwise separable convolution compare to standard convolution in terms of parameter size and efficiency?",
                    "difficulty": "medium",
                    "concept_tested": "Convolution Mechanics",
                    "hint_topic": "Spatial convolution, channel convolution, computational load reduction"
                },
                {
                    "id": 5,
                    "question": "If tomato leaf pathogens mutation occurs next season, how would you update FoliarNet to prevent catastrophic forgetting?",
                    "difficulty": "hard",
                    "concept_tested": "Continual Learning",
                    "hint_topic": "Fine-tuning, transfer learning, class incremental training"
                }
            ]
        elif "generative artificial intelligence" in content_lower or "academic institutions" in content_lower:
            return [
                {
                    "id": 1,
                    "question": "In your essay, why do you characterize the detection of AI output as a 'losing battle' for academic institutions?",
                    "difficulty": "easy",
                    "concept_tested": "AI Detection Ethics",
                    "hint_topic": "Detector evasion, LLM style mutations, dynamic AI generation evolution"
                },
                {
                    "id": 2,
                    "question": "You discussed how junior software engineers and copywriters are at risk. How can training programs adapt to prevent labor displacement?",
                    "difficulty": "easy",
                    "concept_tested": "Socio-Economic Implications",
                    "hint_topic": "AI-human co-working, upskilling, creative guidance"
                },
                {
                    "id": 3,
                    "question": "What role do oral vivas and flipped classrooms play in validating a student's actual understanding of GenAI artifacts?",
                    "difficulty": "medium",
                    "concept_tested": "Pedagogical Evolution",
                    "hint_topic": "Authentic assessment, real-time verbal reasoning, critical thinking"
                },
                {
                    "id": 4,
                    "question": "How can society address copyright infringement when large language models are trained on public datasets without explicit creator consent?",
                    "difficulty": "medium",
                    "concept_tested": "Intellectual Property",
                    "hint_topic": "Fair use doctrine, licensing models, opt-out mechanisms"
                },
                {
                    "id": 5,
                    "question": "If white-collar automation increases wealth inequality, what policy interventions (e.g. UBI or automation taxes) would you recommend?",
                    "difficulty": "hard",
                    "concept_tested": "Economic Policy Design",
                    "hint_topic": "Universal Basic Income, taxation of digital capital, structural transitions"
                }
            ]
        
        # Otherwise, dynamically construct highly realistic questions using sentences from their custom document!
        import re
        sentences = re.split(r'(?<=[.!?])\s+|\n+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 35 and not s.strip().startswith("import") and not s.strip().startswith("from") and not s.strip().startswith("print")]
        
        # Fallback to standard demo questions if the custom text is too short or empty
        if len(sentences) < 3:
            return DEMO_QUESTIONS
            
        # Select 5 sentences (or repeat if fewer)
        chosen_sentences = []
        for i in range(5):
            chosen_sentences.append(sentences[i % len(sentences)])
            
        dynamic_qs = []
        difficulties = ["easy", "easy", "medium", "medium", "hard"]
        concepts = ["Core Premise", "Methodology Application", "Structural Limitations", "Detailed Process", "Empirical Defence"]
        hints = [
            "Clarifying central arguments, personal voice, project context",
            "Alternative methods, scaling parameters, framework modifications",
            "Failure states, boundaries, assumptions made in the text",
            "Walkthrough of decisions, structural reasoning, syntax choice",
            "Handling critics, edge behaviors, verifying claims empirically"
        ]
        
        templates = [
            "In your submission, you state: '{sentence}'. Can you explain the core motivation and background behind this specific statement?",
            "Regarding your point about '{sentence}', how would you approach this task differently if you were restricted to a highly limited budget or resource constraint?",
            "You wrote: '{sentence}'. What are the potential vulnerabilities, limitations, or edge cases associated with this approach?",
            "Walk me through the precise logical or technical steps that led you to assert: '{sentence}'. Why is this choice optimal?",
            "If a validator challenged your claim: '{sentence}', how would you defend this assertion using direct empirical evidence or logical proof?"
        ]
        
        for i in range(5):
            s_clean = chosen_sentences[i]
            if len(s_clean) > 85:
                s_clean = s_clean[:82] + "..."
            
            dynamic_qs.append({
                "id": i + 1,
                "question": templates[i].format(sentence=s_clean),
                "difficulty": difficulties[i],
                "concept_tested": concepts[i],
                "hint_topic": hints[i]
            })
            
        return dynamic_qs
        
    # Truncate content to 4000 chars to avoid token limit errors
    truncated_content = content[:4000]
    prompt = QUESTION_GEN_PROMPT.format(content=truncated_content)
    
    # We let the exception bubble up to the app interface in live mode 
    # so the user receives a clear error banner instead of a silent fallback!
    client = get_gemini_client(api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    questions = parse_json_safely(response.text, None)
    
    if not questions or not isinstance(questions, list) or len(questions) != 5:
        raise ValueError("Gemini returned an invalid or incomplete question schema. Please try regenerating.")
        
    return questions

def analyze_submission(content: str, api_key: str = None, demo_mode: bool = False) -> dict:
    """
    Performs high-level metadata analysis on the submission text.
    """
    if demo_mode:
        content_lower = content.lower()
        if "telecom_churn" in content_lower or "randomforestclassifier" in content_lower:
            return DEMO_ANALYSIS
        elif "tomato" in content_lower or "foliarnet" in content_lower:
            return {
                "subject_area": "Computer Vision (Precision Agriculture)",
                "complexity_level": "advanced",
                "key_concepts": ["Convolutional Neural Network", "Attention Gated Layers", "Grad-CAM Saliency Maps", "Multi-spectral Drone Imagery", "Depthwise Separable Convolutions"],
                "word_count": 230,
                "estimated_read_time": "1 min",
                "ai_written_likelihood": "Low",
                "ai_written_reasoning": "The abstract features highly specific botanical nomenclature and custom domain-specific methodologies, indicating high student authorship."
            }
        elif "generative artificial intelligence" in content_lower or "academic institutions" in content_lower:
            return {
                "subject_area": "Sociology of Technology & Education",
                "complexity_level": "intermediate",
                "key_concepts": ["Generative AI Ethics", "Labor Automation", "Pedagogical Evolution", "Oral Viva Examinations", "Socio-economic Wealth Inequality"],
                "word_count": 250,
                "estimated_read_time": "1.5 mins",
                "ai_written_likelihood": "Medium",
                "ai_written_reasoning": "The essay is highly structured and grammatically cohesive, but balances this with personal insights regarding flipped classrooms."
            }
            
        # Otherwise, dynamically extract key concepts!
        words = content.split()
        word_count = len(words)
        
        # Simple extraction of some capitalized terms as key concepts
        concepts = list(set([w.strip(".,()\"';:") for w in words if w.istitle() and len(w) > 4]))[:5]
        while len(concepts) < 5:
            concepts.append(f"Concept {len(concepts)+1}")
            
        return {
            "subject_area": "Custom Submitted Coursework",
            "complexity_level": "intermediate",
            "key_concepts": concepts,
            "word_count": word_count,
            "estimated_read_time": f"{max(1, word_count // 200)} mins",
            "ai_written_likelihood": "Low",
            "ai_written_reasoning": "This custom document features a unique linguistic profile with custom thematic distributions, indicating authentic authorship."
        }
        
    truncated_content = content[:4000]
    prompt = SUMMARY_ANALYSIS_PROMPT.format(content=truncated_content)
    
    client = get_gemini_client(api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    analysis = parse_json_safely(response.text, None)
    
    if not analysis or not isinstance(analysis, dict):
        raise ValueError("Gemini returned an invalid metadata analysis schema. Please try again.")
        
    # Validation checks for schema structure
    required_keys = ["subject_area", "complexity_level", "key_concepts", "word_count", "estimated_read_time", "ai_written_likelihood", "ai_written_reasoning"]
    for key in required_keys:
        if key not in analysis:
            raise ValueError(f"Missing required metadata field: '{key}' in Gemini response.")
            
    return analysis
