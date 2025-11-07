import os
import sys

# --- AI Configuration ---
MODEL_NAME = "gpt-4o-mini"
# The system prompt guides the AI's persona and capability.
# Crucially, it informs the model about the available tools.
SYSTEM_PROMPT = """
You are 'Aether', an expert voice-activated AI assistant for macOS. 
Your primary goal is to be helpful, concise, and conversational.
You have the capability to interact directly with the user's operating system using the tools provided.

RULES:
1. When a user asks you to perform an action (e.g., "Open Safari," "Close Messages"), ALWAYS use the appropriate tool function instead of just saying you will do it.
2. After calling a tool, report the result of the action (success or error) back to the user naturally.
3. For general questions, provide a concise, friendly, and direct answer.
4. Keep your responses short and effective for a voice interface.
"""

# --- Local TTS Function ---
def local_tts(speech: str):
    """
    Uses the local macOS 'say' command for Text-to-Speech.
    The -v (voice) and -r (rate) flags are optional but improve quality.
    Note: The original 'Isha' voice is used here.
    """
    try:
        # Escape single quotes properly for shell execution
        safe_speech = speech.replace("'", r"'\''")
        # Use a higher quality, standard voice like 'Samantha' or 'Alex'
        # 'Isha' is not a standard macOS voice. Using 'Alex' as a safe default.
        command = f"say -v 'Alex' -r 200 '{safe_speech}'"
        os.system(command)
    except Exception as e:
        print(f"❌ Error during local TTS: {e}")
        
    sys.stdout.flush()

# --- Placeholder for environment check (optional but good practice) ---
def check_env():
    """Checks for necessary environment variables."""
    if not os.getenv("OPENAI_API_KEY"):
        print("FATAL ERROR: OPENAI_API_KEY environment variable not found.")
        print("Please create a .env file or set the variable.")
        sys.exit(1)

if __name__ == "__main__":
    # Test TTS function directly
    local_tts("The configuration and utilities file is working successfully.")
    print("TTS test complete.")
