from typing import Dict, Any, List, Callable

# Import tools and schemas from modular files
from .app_control import APP_CONTROL_TOOLS, APP_CONTROL_SCHEMAS
from .system_utilities import SYSTEM_UTILITY_TOOLS, SYSTEM_UTILITY_SCHEMAS

# --- Central Aggregation ---

# Dictionary to map function names to their callable objects
AVAILABLE_TOOLS: Dict[str, Callable] = {}
AVAILABLE_TOOLS.update(APP_CONTROL_TOOLS)
AVAILABLE_TOOLS.update(SYSTEM_UTILITY_TOOLS)

# List to hold the OpenAI API tool schemas
TOOL_SCHEMAS: List[Dict[str, Any]] = []
TOOL_SCHEMAS.extend(APP_CONTROL_SCHEMAS)
TOOL_SCHEMAS.extend(SYSTEM_UTILITY_SCHEMAS)

# You can now import AVAILABLE_TOOLS and TOOL_SCHEMAS from this manager file
# in your main application logic.