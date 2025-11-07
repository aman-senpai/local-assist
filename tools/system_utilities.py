import os
import subprocess
import urllib.parse
from typing import Dict, Any, List, Callable
import re # Added for potential future use, though not strictly needed here

# Tool Definitions

def run_shell_command(command: str) -> str:
    """
    Executes an arbitrary shell command on macOS.
    NOTE: Use this tool ONLY for actions not covered by other specific functions.
    """
    try:
        # Use subprocess.run for safer and more robust execution and error handling
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False # Do not raise exception on non-zero exit code
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            return f"Command executed successfully. Output: {output if output else 'No output.'}"
        else:
            return f"Command failed (Exit Code {result.returncode}). Error: {error}"

    except Exception as e:
        return f"Error executing shell command '{command}': {e}"


# --- Volume Control Functions ---

def get_current_volume() -> int:
    """Reads the current system volume level (0-100) using AppleScript."""
    try:
        applescript = 'output volume of (get volume settings)'
        command = f"osascript -e '{applescript}'"
        result = subprocess.check_output(command, shell=True, text=True).strip()
        return int(result)
    except Exception:
        return 50 


def adjust_system_volume(change: int = None, absolute_level: int = None) -> str:
    """
    Adjusts the macOS master output volume by a relative change (+/-) 
    or sets it to an absolute level (0-100).
    """
    if absolute_level is not None:
        if not 0 <= absolute_level <= 100:
            return "Error: Absolute volume level must be between 0 and 100."
        new_level = absolute_level
        action_type = "set to"
        
    elif change is not None:
        current_level = get_current_volume()
        new_level = current_level + change
        action_type = "adjusted by"
        
    else:
        return "Error: Must provide either 'change' (relative) or 'absolute_level'."

    new_level = max(0, min(100, new_level))

    try:
        applescript = f'set volume output volume {new_level}'
        command = f"osascript -e '{applescript}'"
        os.system(command)
        
        if action_type == "set to":
            return f"System volume successfully set to **{new_level}%**."
        else:
            return f"System volume {action_type} {change}%. New level is **{new_level}%**."
            
    except Exception as e:
        return f"An error occurred while setting the volume: {e}"


# --- Brightness Control Functions (NEW) ---

def get_current_brightness() -> int:
    """Reads the current display brightness level (0-100) using AppleScript."""
    try:
        # AppleScript to get the brightness (0.0 to 1.0)
        applescript = 'tell application "System Events" to get value of slider "display brightness" of group 1 of (first process whose name is "ControlCenter")'
        command = f"osascript -e '{applescript}'"
        
        # Execute the command and capture output (e.g., "0.5")
        result = subprocess.check_output(command, shell=True, text=True).strip()
        
        # Convert float (0.0-1.0) to integer percentage (0-100)
        brightness_float = float(result)
        return int(brightness_float * 100)
        
    except Exception:
        # Fallback to a mid-point if reading fails
        # Note: Reading brightness via AppleScript can be brittle depending on macOS version/setup.
        return 50


def adjust_system_brightness(change: int = None, absolute_level: int = None) -> str:
    """
    Adjusts the macOS display brightness by a relative change (+/-) 
    or sets it to an absolute level (0-100).
    """
    
    if absolute_level is not None:
        # Absolute Brightness Setting
        if not 0 <= absolute_level <= 100:
            return "Error: Absolute brightness level must be between 0 and 100."
        new_level_int = absolute_level
        action_type = "set to"
        
    elif change is not None:
        # Relative Brightness Change
        current_level = get_current_brightness()
        new_level_int = current_level + change
        action_type = "adjusted by"
        
    else:
        return "Error: Must provide either 'change' (relative) or 'absolute_level' for brightness."

    # Clamp the new level to the 0-100 range
    new_level_int = max(0, min(100, new_level_int))
    
    # Convert integer percentage (0-100) to float (0.0-1.0) for the AppleScript command
    new_level_float = new_level_int / 100.0

    try:
        # AppleScript to set brightness. We use the 'System Events' method for consistency.
        # This approach assumes "System Events" can interact with the Display preferences.
        applescript = (
            'tell application "System Events"\n'
            '    tell process "ControlCenter"\n'
            '        tell slider "display brightness" of group 1\n'
            f'            set value to {new_level_float}\n'
            '        end tell\n'
            '    end tell\n'
            'end tell'
        )
        command = f"osascript -e '{applescript}'"
        
        # Execute the command
        os.system(command)
        
        if action_type == "set to":
            return f"System brightness successfully set to **{new_level_int}%**."
        else:
            return f"System brightness {action_type} {change}%. New level is **{new_level_int}%**."
            
    except Exception as e:
        return f"An error occurred while setting the brightness: {e}"


# --- Other Utility Functions (Unchanged) ---

def copy_to_clipboard(text: str) -> str:
    # ... (Implementation remains the same)
    try:
        process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE, text=True)
        process.communicate(text)
        if process.returncode == 0:
            return "Text successfully copied to the clipboard."
        else:
            return "Error copying text to clipboard."
    except Exception as e:
        return f"An error occurred while using the clipboard: {e}"


def create_file_with_content(file_path: str, content: str) -> str:
    # ... (Implementation remains the same)
    full_path = os.path.expanduser(file_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return f"Successfully created file at {full_path} with the specified content."
    except Exception as e:
        return f"Error creating file at {full_path}: {e}"


def search_youtube(query: str) -> str:
    # ... (Implementation remains the same)
    safe_query = urllib.parse.quote_plus(query)
    youtube_url = f"https://www.youtube.com/results?search_query={safe_query}"
    try:
        command = f'open "{youtube_url}"'
        result = os.system(command)
        if result == 0:
            return f"Successfully opened the default web browser to search YouTube for: '{query}'."
        else:
            return f"Error: Could not open the URL for YouTube search. Shell command failed."
    except Exception as e:
        return f"An unexpected error occurred while trying to search YouTube: {e}"


# --- Tool Schema and Mapping Aggregation ---

SYSTEM_UTILITY_TOOLS: Dict[str, Callable] = {
    run_shell_command.__name__: run_shell_command,
    adjust_system_volume.__name__: adjust_system_volume,
    adjust_system_brightness.__name__: adjust_system_brightness, # NEW
    copy_to_clipboard.__name__: copy_to_clipboard,
    create_file_with_content.__name__: create_file_with_content,
    search_youtube.__name__: search_youtube,
}

SYSTEM_UTILITY_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": run_shell_command.__name__,
            "description": "Executes a general, arbitrary command in the macOS shell. Use this sparingly and only for advanced tasks like checking system status or running scripts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The exact shell command to execute, e.g., 'date' or 'pwd'."
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": adjust_system_volume.__name__,
            "description": "Adjusts the macOS master output volume. Can set it to an 'absolute_level' (0-100) or increase/decrease it by a 'change' amount (e.g., +10 or -5).",
            "parameters": {
                "type": "object",
                "properties": {
                    "change": {
                        "type": "integer",
                        "description": "The relative amount to change the volume by (e.g., 10 to increase, -10 to decrease). Use only one of 'change' or 'absolute_level'."
                    },
                    "absolute_level": {
                        "type": "integer",
                        "description": "The specific volume level to set (0 to 100). Use only one of 'change' or 'absolute_level'."
                    }
                },
                "oneOf": [
                    {"required": ["change"]},
                    {"required": ["absolute_level"]}
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": adjust_system_brightness.__name__, # NEW
            "description": "Adjusts the macOS display brightness. Can set it to an 'absolute_level' (0-100) or increase/decrease it by a 'change' amount (e.g., +10 or -5).",
            "parameters": {
                "type": "object",
                "properties": {
                    "change": {
                        "type": "integer",
                        "description": "The relative amount to change the brightness by (e.g., 10 to increase, -10 to decrease). Use only one of 'change' or 'absolute_level'."
                    },
                    "absolute_level": {
                        "type": "integer",
                        "description": "The specific brightness level to set (0 to 100). Use only one of 'change' or 'absolute_level'."
                    }
                },
                "oneOf": [
                    {"required": ["change"]},
                    {"required": ["absolute_level"]}
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": copy_to_clipboard.__name__,
            "description": "Copies a given text string to the macOS clipboard. Use this for quick copy tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content to be copied to the clipboard."
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": create_file_with_content.__name__,
            "description": "Creates a new text file at a specified path (e.g., '~/Documents/report.txt') with the provided content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file, relative to the user's home directory (e.g., '~/Desktop/notes.md')."
                    },
                    "content": {
                        "type": "string",
                        "description": "The text content to be written into the new file."
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": search_youtube.__name__,
            "description": "Opens the default web browser and searches YouTube for a specified video topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The video topic or search phrase to look for on YouTube (e.g., 'latest AI news')."
                    }
                },
                "required": ["query"]
            }
        }
    },
]