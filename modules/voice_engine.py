# File: authentilearn/modules/voice_engine.py
import io
from gtts import gTTS

def text_to_speech(text: str) -> bytes:
    """
    Converts a given string of text into MP3 voice bytes using gTTS.
    """
    if not text:
        return b""
        
    try:
        # Generate speech
        tts = gTTS(text=text, lang="en", slow=False)
        
        # Save to a bytes buffer
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        return fp.read()
    except Exception as e:
        print(f"Error in text_to_speech: {str(e)}")
        return b""
