import os
import subprocess
from typing import Dict, Any, List, Callable

# Tool Definitions

def open_application(app_name: str) -> str:
    """
    Opens a specified application on macOS using the 'open -a' command.
    Example: open_application("Safari")
    """
    try:
        command = f'open -a "{app_name}"'
        result = os.system(command)

        if result == 0:
            return f"Successfully opened the application: {app_name}."
        else:
            return f"Error: Could not find or open application '{app_name}'. Please ensure the app name is correct and in the Applications folder."
    except Exception as e:
        return f"An unexpected error occurred while trying to open {app_name}: {e}"


def close_frontmost_application() -> str:
    """
    Closes the currently active (frontmost) application on macOS using AppleScript.
    """
    try:
        # AppleScript to quit the frontmost application.
        applescript = 'tell application (path to frontmost application as text) to quit'

        command = f"osascript -e '{applescript}'"
        result = os.system(command)

        if result == 0:
            return "Successfully sent the quit command to the frontmost application. Note: The application might ask to save documents."
        else:
            return "Error: Could not send the quit command to the frontmost application. It might be a protected system process."
    except Exception as e:
        return f"An unexpected error occurred while trying to close the frontmost application: {e}"


def minimize_frontmost_window() -> str:
    """
    Minimizes the currently active (frontmost) application's window using AppleScript.
    """
    try:
        # AppleScript to minimize the window of the frontmost application.
        applescript = (
            'tell application "System Events"\n'
            '    tell process (name of first process whose frontmost is true)\n'
            '        try\n'
            '            click menu item "Minimize" of menu "Window" of menu bar 1\n'
            '            return "Successfully minimized the frontmost window."\n'
            '        on error\n'
            '            return "Error: Could not find a window to minimize or the application does not support it."\n'
            '        end try\n'
            '    end tell\n'
            'end tell'
        )

        command = f"osascript -e '{applescript}'"
        # We use check_output to capture any output from the script (including error messages)
        result = subprocess.check_output(command, shell=True, text=True).strip()

        # Check if the result indicates a successful minimize action
        if "Successfully minimized" in result:
            return result
        else:
            return "Could not minimize the frontmost window. It might be a full-screen app or a system utility."

    except subprocess.CalledProcessError as e:
        # The AppleScript failed to execute or returned an error code
        return f"AppleScript execution failed: {e.output.strip()}"
    except Exception as e:
        return f"An unexpected error occurred while trying to minimize the window: {e}"


# Tool Schema and Mapping Aggregation
APP_CONTROL_TOOLS: Dict[str, Callable] = {
    open_application.__name__: open_application,
    close_frontmost_application.__name__: close_frontmost_application,
    minimize_frontmost_window.__name__: minimize_frontmost_window,
}

APP_CONTROL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": open_application.__name__,
            "description": "Opens a specified application (e.g., 'open Mail', 'launch Terminal'). Takes the exact application name as input.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "The exact name of the macOS application to open, like 'Safari' or 'Finder'."
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": close_frontmost_application.__name__,
            "description": "Closes or quits the application that is currently active on the user's screen.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": minimize_frontmost_window.__name__,
            "description": "Minimizes the window of the application that is currently active on the screen.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
]