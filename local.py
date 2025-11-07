import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv
import os
import sys

load_dotenv()

client = OpenAI()

def local_tts(speech: str):
    """
    Uses the local macOS 'say' command for Text-to-Speech.
    The -v (voice) and -r (rate) flags are optional but improve quality.
    """
    safe_speech = speech.replace("'", r"'\''")
    command = f"say -v 'Isha' -r 200 '{safe_speech}'"
    os.system(command)

def main():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("🔊 Calibrating microphone for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=2.0)
        print("✅ Calibration complete. Ready!")
        sys.stdout.flush()

    r.pause_threshold = 1.0
    r.non_speaking_duration = 1

    SYSTEM_PROMPT = """
    You're an expert voice agent. You are given the transcript of what the user has said using voice.
    You need to output as if you are a voice agent, and whatever you speak will be converted back to audio
    using AI and played back to the user. Keep your responses concise and conversational.
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    while True:
        with sr.Microphone() as source:
            
            print("\n🎤 Say something (Listening...): ", end="", flush=True)

            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                print("\r🧠 Thinking...               ", end="", flush=True) 

            except sr.WaitTimeoutError:
                print("\rTimeout: No speech detected.          ", flush=True)
                continue

            try:
                stt = r.recognize_google(audio)
                print(f"\r👤 You said: {stt}", flush=True) 
            except sr.UnknownValueError:
                print("\rCould not understand audio.          ", flush=True)
                continue
            except sr.RequestError as e:
                print(f"\rGoogle Speech Recognition service error: {e}", flush=True)
                continue

            messages.append({"role": "user", "content": stt})
            
            try:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )

                ai_response = res.choices[0].message.content 
                print(f"🤖 AI says: {ai_response}", flush=True)
            
                local_tts(speech=ai_response)
                
            except Exception as e:
                 print(f"❌ Error getting AI response: {e}", flush=True)


if __name__ == "__main__":
    main()