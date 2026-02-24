import streamlit as st
from bytez import Bytez 
import wave
import io

# Initialize the SDK with your secret key
sdk = Bytez(st.secrets["BYTEZ_KEY"])

def frames_to_wav(audio_frames):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(16000) # 16kHz
        for frame in audio_frames:
            wf.writeframes(frame.to_ndarray().tobytes())
    buffer.seek(0)
    return buffer

def transcribe_audio(audio_frames):
    if not audio_frames:
        return None
        
    try:
        # Convert frames to WAV format
        wav_file = frames_to_wav(audio_frames)
        
        # ✅ Using the high-accuracy model from your screenshots
        model = sdk.model("openai/whisper-large-v3")
        
        # Run the model on the audio binary data
        result = model.run(wav_file.read())
        
        # ✅ PROPER HANDLING: Check for dictionary keys or output attributes
        if isinstance(result, dict):
            return result.get("text") or result.get("output")
        elif hasattr(result, "output") and result.output:
            return result.output
        elif hasattr(result, "text"):
            return result.text
            
        return None
        
    except Exception as e:
        st.error(f"Bytez STT Error: {e}")
        return None