from openai import OpenAI
from typing import List, Dict, Any, Tuple
import json

from config import MODEL_NAME, SYSTEM_PROMPT
from tools.manager import AVAILABLE_TOOLS, TOOL_SCHEMAS

class VoiceAgent:
    """
    Manages the conversation history and interaction with the OpenAI API, 
    including the logic for detecting and executing tool calls.
    """
    def __init__(self, client: OpenAI):
        self.client = client
        self.messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    def get_response(self, user_text: str) -> Tuple[str, bool]:
        """
        Processes user input, calls the OpenAI model, handles tool calls, 
        and returns the final AI response text.
        
        Returns: A tuple (response_text, is_tool_call_successful)
        """
        # 1. Add user message to history
        self.messages.append({"role": "user", "content": user_text})
        
        # Flag to track if a tool was executed
        tool_executed = False

        # Loop for potential multi-step tool calls
        while True:
            try:
                # 2. Call the model with tools enabled
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=self.messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto"  # Allow the model to decide whether to call a tool
                )

                response_message = response.choices[0].message
                
                # 3. Check if the model wants to call a function/tool
                if response_message.tool_calls:
                    tool_executed = True
                    self.messages.append(response_message)  # Extend conversation with the tool call
                    
                    tool_outputs = []
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # 4. Execute the tool locally
                        if function_name in AVAILABLE_TOOLS:
                            print(f"\n⚙️ Executing tool: {function_name} with args: {function_args}", flush=True)
                            
                            # Execute the Python function
                            function_to_call = AVAILABLE_TOOLS[function_name]
                            function_response = function_to_call(**function_args)
                            
                            # 5. Add tool response back to messages
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": function_response,
                            })
                        else:
                            # Handle case where model asks for an unknown tool
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": f"Error: Tool '{function_name}' is not defined.",
                            })

                    self.messages.extend(tool_outputs)
                    
                    # Continue the loop to get the final, human-readable response
                    # (The model now summarizes the tool execution result)
                    continue 

                # 6. If no tool call, this is the final AI response
                ai_response = response_message.content
                self.messages.append(response_message) # Store the text response
                
                # Keep history concise (optional: remove older messages if it gets too long)
                # For simplicity, we keep all messages for now.
                
                return ai_response, tool_executed

            except Exception as e:
                # Remove the last user message to prevent loop on failure
                if self.messages[-1]["role"] == "user":
                    self.messages.pop() 
                return f"❌ A core error occurred while communicating with the AI: {e}", False
