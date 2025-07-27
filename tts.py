# tts.py
from gtts import gTTS
import os
def generate_tts(text, voice, out_file, api_key=None):
    try:
        print("🎙️ Generating TTS using gTTS...")
        tts = gTTS(text=text, lang='en')
        tts.save(out_file)
        print(f"✅ Audio saved to: {out_file}")
    except Exception as e:
        raise Exception(f"gTTS generation failed: {str(e)}")
