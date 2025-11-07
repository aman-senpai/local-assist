import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv
import os
import sys

from config import local_tts, check_env
from agent import VoiceAgent

# Load environment variables (like OPENAI_API_KEY) from .env file
load_dotenv()
check_env()

def main():
    """
    Initializes the voice assistant components and runs the main listening loop.
    """
    # 1. Initialization
    try:
        client = OpenAI()
        agent = VoiceAgent(client=client)
    except Exception as e:
        print(f"FATAL ERROR: Could not initialize OpenAI client. Check API key. Details: {e}")
        sys.exit(1)
        
    r = sr.Recognizer()
    
    # Configure Recognizer
    r.pause_threshold = 0.8  # Wait for 0.8 seconds of silence before finishing a phrase
    r.non_speaking_duration = 0.5 # Min non-speaking duration before a phrase is considered complete

    # 2. Microphone Calibration
    with sr.Microphone() as source:
        print("🔊 Calibrating microphone for ambient noise...")
        # Reduce to a shorter duration for faster startup
        r.adjust_for_ambient_noise(source, duration=1.0) 
        print("✅ Calibration complete. Ready! I'm Aether, your macOS assistant. Say 'Open Safari' or ask a question.")
        sys.stdout.flush()

    # 3. Main Loop
    while True:
        with sr.Microphone() as source:
            
            print("\n🎤 Listening... (Say something): ", end="", flush=True)

            try:
                # Listen for up to 5 seconds, max phrase length 10 seconds
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                print("\r🧠 Thinking...               ", end="", flush=True) 

            except sr.WaitTimeoutError:
                # Only print if we are still at the listening prompt
                print("\rTimeout: No speech detected.          ", flush=True)
                continue

            # Speech to Text (STT)
            try:
                # Using Google Speech Recognition (requires internet connection)
                stt = r.recognize_google(audio)
                print(f"\r👤 You said: {stt}", flush=True) 
            except sr.UnknownValueError:
                print("\rCould not understand audio.          ", flush=True)
                local_tts("I'm sorry, I couldn't understand what you said. Could you repeat that?")
                continue
            except sr.RequestError as e:
                print(f"\rGoogle Speech Recognition service error: {e}", flush=True)
                local_tts("There was an issue with the speech recognition service. Please check your internet connection.")
                continue

            # AI Response Generation (Tool Calling is handled inside)
            ai_response, _ = agent.get_response(user_text=stt)
            
            # Text to Speech (TTS)
            if ai_response:
                print(f"🤖 AI says: {ai_response}", flush=True)
                local_tts(speech=ai_response)
            
if __name__ == "__main__":
    # Ensure all required packages are installed: 
    # pip install openai SpeechRecognition PyAudio python-dotenv
    # (PyAudio often needs: brew install portaudio)
    main()
