# 2. Tool Usage and Integration for Agentic Flows

from typing import Callable, Dict, Any, List, Optional
import random

# --- What is Tool Usage for Agents? ---
# Agents often need to perform actions or gather information beyond their internal logic.
# "Tools" are functions, API calls, or other services that an agent can utilize.
# Effective tool usage involves:
# - Defining a clear interface for each tool.
# - A mechanism for the agent to select the appropriate tool based on its current goal or state.
# - Executing the tool with the necessary inputs.
# - Handling the tool's output (success or error) to inform the agent's next steps.

# --- Example: Simple Tools for an Agent ---

def get_weather(location: str) -> Dict[str, Any]:
    """Simulates fetching the weather for a given location."""
    print(f"TOOL: Calling get_weather for {location}")
    if not isinstance(location, str) or not location.strip():
        return {"error": "Invalid location provided. Location must be a non-empty string."}
    
    # Simulate different weather conditions
    conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
    temp = random.randint(-10, 35) # Celsius
    humidity = random.randint(30, 90) # Percent
    
    if location.lower() == "unknown":
        return {"error": f"Could not find weather for an unknown location."}

    return {
        "location": location,
        "temperature_celsius": temp,
        "condition": random.choice(conditions),
        "humidity_percent": humidity,
        "forecast": f"It will be {random.choice(conditions)} tomorrow as well."
    }

def search_information(query: str, search_engine: str = "Google") -> Dict[str, Any]:
    """Simulates searching for information using a specified search engine."""
    print(f"TOOL: Calling search_information for '{query}' using {search_engine}")
    if not isinstance(query, str) or not query.strip():
        return {"error": "Invalid query provided. Query must be a non-empty string."}

    # Simulate search results
    results = [
        f"Result 1 about '{query}' from {search_engine}",
        f"Another interesting fact about '{query}'",
        f"More details on '{query}' can be found at example.com/{query.replace(' ', '_')}"
    ]
    if random.random() < 0.1: # 10% chance of finding nothing
        return {"query": query, "results_count": 0, "summary": "No relevant information found."}
        
    return {
        "query": query,
        "search_engine": search_engine,
        "results_count": len(results),
        "summary": random.choice(results) # Return a random summary for brevity
    }

def perform_calculation(expression: str) -> Dict[str, Any]:
    """Simulates performing a calculation. For safety, uses eval carefully (not recommended for prod without sanitization)."""
    print(f"TOOL: Calling perform_calculation for '{expression}'")
    try:
        # WARNING: eval() is dangerous with arbitrary user input.
        # In a real agent, use a safer math expression parser/evaluator.
        allowed_chars = set("0123456789.+-*/() ")
        if not all(char in allowed_chars for char in expression):
            raise ValueError("Expression contains invalid characters.")
        if not expression.strip():
             raise ValueError("Expression cannot be empty.")

        result = eval(expression) # Be very cautious with eval!
        return {"expression": expression, "result": result}
    except (SyntaxError, NameError, TypeError, ValueError, ZeroDivisionError) as e:
        return {"expression": expression, "error": f"Calculation error: {str(e)}"}
    except Exception as e:
        return {"expression": expression, "error": f"An unexpected error occurred during calculation: {str(e)}"}

# --- Agent with Tool Usage Capability ---

class ToolUsingAgent:
    def __init__(self):
        self.tools: Dict[str, Callable[..., Dict[str, Any]]] = {
            "get_weather": get_weather,
            "search_information": search_information,
            "perform_calculation": perform_calculation
        }
        print("ToolUsingAgent initialized with tools:", list(self.tools.keys()))

    def list_available_tools(self) -> List[str]:
        return list(self.tools.keys())

    def select_tool(self, task_description: str) -> Optional[str]:
        """Very simple tool selection logic based on keywords."""
        task_description = task_description.lower()
        if "weather" in task_description or "forecast" in task_description:
            return "get_weather"
        elif "search" in task_description or "find information" in task_description or "look up" in task_description:
            return "search_information"
        elif "calculate" in task_description or "compute" in task_description or "math" in task_description:
            return "perform_calculation"
        return None # No suitable tool found

    def use_tool(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found."}
        
        tool_function = self.tools[tool_name]
        print(f"AGENT: Attempting to use tool '{tool_name}' with arguments {kwargs}")
        try:
            # In a real scenario, argument validation against tool schema would be important here.
            result = tool_function(**kwargs)
            print(f"AGENT: Tool '{tool_name}' executed. Result: {result}")
            return result
        except TypeError as e: # Mismatch in arguments provided vs. tool expectations
            error_msg = f"Argument mismatch for tool '{tool_name}'. Expected: {tool_function.__code__.co_varnames[:tool_function.__code__.co_argcount]}. Error: {e}"
            print(f"AGENT: Error - {error_msg}")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error while executing tool '{tool_name}': {e}"
            print(f"AGENT: Error - {error_msg}")
            return {"error": error_msg}

    def process_request(self, request_text: str):
        """Simulates an agent processing a request that might involve a tool."""
        print(f"\nAGENT: Received request: '{request_text}'")
        
        # Simplified: Extracting tool and arguments (very basic parsing)
        # In a real agent, this would involve more sophisticated NLP/intent recognition.
        tool_name = self.select_tool(request_text)
        
        if not tool_name:
            print("AGENT: I don't have a tool for that. Can you rephrase or ask something else?")
            return {"response": "Sorry, I can't help with that specific request.", "tool_used": None}

        # Extremely simplified argument extraction for demonstration
        args = {}
        if tool_name == "get_weather":
            # Try to find a location (e.g., "weather in London")
            if " in " in request_text:
                args["location"] = request_text.split(" in ")[-1].split("?")[0].strip()
            elif " for " in request_text:
                args["location"] = request_text.split(" for ")[-1].split("?")[0].strip()
            else:
                args["location"] = "unknown" # Default if not found
        elif tool_name == "search_information":
            # Assume the part after "search for" or "look up" is the query
            if "search for " in request_text:
                args["query"] = request_text.split("search for ")[-1].strip()
            elif "look up " in request_text:
                args["query"] = request_text.split("look up ")[-1].strip()
            else:
                args["query"] = request_text # Fallback to whole request
        elif tool_name == "perform_calculation":
            # Assume the part after "calculate" is the expression
            if "calculate " in request_text:
                args["expression"] = request_text.split("calculate ")[-1].strip()
            else:
                 return {"response": "Please provide the expression to calculate.", "tool_used": tool_name, "error": "Missing expression"}

        tool_result = self.use_tool(tool_name, **args)
        
        # Agent formulates a response based on tool output
        if "error" in tool_result:
            response_text = f"I tried to use the '{tool_name}' tool, but there was an error: {tool_result['error']}"
        else:
            response_text = f"Using the '{tool_name}' tool, I found: {tool_result}"
        
        print(f"AGENT: Formulated response: '{response_text}'")
        return {"response": response_text, "tool_used": tool_name, "tool_output": tool_result}

# --- Example Usage ---
if __name__ == "__main__":
    agent = ToolUsingAgent()

    print("\nAvailable tools:", agent.list_available_tools())

    agent.process_request("What's the weather like in Paris?")
    agent.process_request("search for information on Python decorators")
    agent.process_request("calculate 25 * (4 + 1)")
    agent.process_request("calculate 100 / 0") # Error in tool
    agent.process_request("get_weather for London") # Using tool name directly
    agent.process_request("What is the capital of France?") # Tool selection might fail or use search
    agent.process_request("search for pizza recipes")
    agent.process_request("Tell me a joke.") # No tool for this
    agent.process_request("calculate") # Missing argument for tool
    agent.process_request("weather in") # Missing argument for tool, leads to "unknown"

# --- Key Takeaways for Tool Usage ---
# - Tool Definition: Each tool should have a clear purpose and well-defined inputs/outputs (Pydantic models are great for this in real apps).
# - Tool Registration: The agent needs a way to know which tools are available.
# - Tool Selection (Reasoning): This is a critical part. It can range from simple keyword matching (as above) 
#   to complex NLP, or even another LLM call to decide which tool and parameters to use.
# - Argument Mapping: Ensuring the agent can extract or determine the correct arguments for the selected tool.
# - Robust Error Handling: Tools can fail. The agent needs to handle these errors gracefully.
# - Security: Be extremely careful if tools involve executing code (like `eval`) or interacting with sensitive systems.
#   Always sanitize inputs and limit permissions. 