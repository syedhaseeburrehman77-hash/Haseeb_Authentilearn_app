# File: authentilearn/modules/auth_engine.py
import time
from modules.voice_auth import enroll_voice_profile, verify_voice_profile
from modules.face_auth import enroll_face_profile, verify_face_profile

# Default Demo Profile Credentials for Judgement Bypasses
MOCK_AUTH_RESULT = {
    "voice_score": 0.87,
    "face_score": 0.79,
    "combined_score": 0.84,
    "status": "AUTHENTICATED",
    "student_name": "Ahmed Hassan",
    "student_id": "CS-2024-047"
}

def enroll_student_identity(name: str, student_id: str) -> dict:
    """
    Registers a student's biometrics by capturing initial voice and face footprints.
    Returns the enrolled profile dict.
    """
    # Capture face template
    face_profile = enroll_face_profile()
    
    # Capture 3-second voice template saying standard honesty statement
    voice_profile = enroll_voice_profile(name, duration=3.0)
    
    return {
        "student_name": name,
        "student_id": student_id,
        "face_template": face_profile["histogram"],
        "face_image_b64": face_profile["image_b64"],
        "voice_template": voice_profile["mfcc"],
        "is_simulated": face_profile["is_simulated"] or voice_profile["is_simulated"],
        "enrolled_timestamp": time.time()
    }

def verify_student_identity(enrolled_profile: dict, demo_mode: bool = False) -> dict:
    """
    Verifies a returning student by checking voice and face inputs against templates.
    """
    if demo_mode:
        # Simulate slight random fluctuations in verification scores for demo dynamics
        v_score = 0.87 + 0.05 * (hash(time.time()) % 3 - 1)
        f_score = 0.79 + 0.04 * (hash(time.time() + 1) % 3 - 1)
        c_score = (v_score * 0.6) + (f_score * 0.4)
        
        return {
            "voice_score": round(v_score, 3),
            "face_score": round(f_score, 3),
            "combined_score": round(c_score, 3),
            "match_percentage": round(c_score * 100, 1),
            "status": "AUTHENTICATED" if c_score >= 0.70 else "FAILED",
            "student_name": enrolled_profile.get("student_name", "Ahmed Hassan"),
            "student_id": enrolled_profile.get("student_id", "CS-2024-047"),
            "is_simulated": True,
            "captured_image_b64": enrolled_profile.get("face_image_b64", "")
        }
        
    # Real biometrics capturing
    # Capture and verify Face
    face_res = verify_face_profile(enrolled_profile["face_template"])
    face_score = face_res["similarity_score"]
    
    # Capture and verify Voice (using same standard duration)
    voice_res = verify_voice_profile(enrolled_profile["voice_template"], duration=3.0)
    voice_score = voice_res["similarity_score"]
    
    # Combined weighted score: 60% Voice match, 40% Face match
    combined_score = (voice_score * 0.6) + (face_score * 0.4)
    
    status = "AUTHENTICATED" if combined_score >= 0.70 else "FAILED"
    
    return {
        "voice_score": round(voice_score, 3),
        "face_score": round(face_score, 3),
        "combined_score": round(combined_score, 3),
        "match_percentage": round(combined_score * 100, 1),
        "status": status,
        "student_name": enrolled_profile["student_name"],
        "student_id": enrolled_profile["student_id"],
        "is_simulated": face_res["is_simulated"] or voice_res["is_simulated"],
        "captured_image_b64": face_res["image_b64"]
    }
