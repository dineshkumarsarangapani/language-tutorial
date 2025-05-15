# 6. Structured Data Parsing & Generation (with Pydantic) for Agentic Flows

from pydantic import BaseModel, Field, ValidationError
from typing import Callable, Dict, Any, List, Optional, Union
import random
import json # For pretty printing Pydantic model errors

# --- Why Pydantic for Agentic Flows? ---
# - **Data Validation:** Ensure inputs to tools and agent logic are correct.
# - **Clear Schemas:** Define unambiguous structures for tool inputs/outputs, agent plans, and memory.
# - **Serialization/Deserialization:** Easily convert between Python objects and JSON (e.g., for API calls, storing state).
# - **Improved Tool Handling:** Makes calling tools and processing their results more robust and predictable.
# - **IDE Support:** Better autocompletion and type checking when working with structured data.

# --- Pydantic Models for Tool Inputs & Outputs ---

# Tool: Get Weather
class GetWeatherInput(BaseModel):
    location: str = Field(..., description="The city and state, e.g., San Francisco, CA")

class WeatherOutput(BaseModel):
    location: str
    temperature_celsius: float
    condition: str
    humidity_percent: int
    forecast: str

class ToolErrorOutput(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None

# Tool: Search Information
class SearchInformationInput(BaseModel):
    query: str = Field(..., min_length=3, description="The search query.")
    search_engine: Optional[str] = Field("Google", description="The search engine to use.")

class SearchResultItem(BaseModel):
    title: str
    snippet: str
    source: Optional[str] = None

class SearchInformationOutput(BaseModel):
    query: str
    search_engine: str
    results_count: int
    results: List[SearchResultItem]
    summary: Optional[str] = None

# Tool: Perform Calculation
class PerformCalculationInput(BaseModel):
    expression: str = Field(..., description="The mathematical expression to evaluate, e.g., '2 * (3 + 5)'")

class PerformCalculationOutput(BaseModel):
    expression: str
    result: float # Assuming float result for broader compatibility

# --- Updated Tool Definitions (using Pydantic models) ---

def get_weather_pydantic(inputs: GetWeatherInput) -> Union[WeatherOutput, ToolErrorOutput]:
    print(f"PYDANTIC_TOOL: Calling get_weather for {inputs.location}")
    # Input validation already handled by Pydantic if called correctly
    conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
    if inputs.location.lower() == "unknown_city":
        return ToolErrorOutput(error=f"Could not find weather for an unknown city: {inputs.location}")
    return WeatherOutput(
        location=inputs.location,
        temperature_celsius=random.uniform(-10, 35.5),
        condition=random.choice(conditions),
        humidity_percent=random.randint(30, 90),
        forecast=f"It will be {random.choice(conditions)} tomorrow as well."
    )

def search_information_pydantic(inputs: SearchInformationInput) -> Union[SearchInformationOutput, ToolErrorOutput]:
    print(f"PYDANTIC_TOOL: Calling search_information for '{inputs.query}' using {inputs.search_engine}")
    sim_results = [
        SearchResultItem(title=f"Understanding {inputs.query}", snippet=f"Detailed explanation of {inputs.query}..."),
        SearchResultItem(title=f"Applications of {inputs.query}", snippet="Practical uses and examples.")
    ]
    if random.random() < 0.1: # Simulate no results
        return SearchInformationOutput(query=inputs.query, search_engine=inputs.search_engine, results_count=0, results=[], summary="No relevant information found.")
    return SearchInformationOutput(
        query=inputs.query,
        search_engine=inputs.search_engine,
        results_count=len(sim_results),
        results=sim_results,
        summary=f"Found {len(sim_results)} promising results for '{inputs.query}'."
    )

def perform_calculation_pydantic(inputs: PerformCalculationInput) -> Union[PerformCalculationOutput, ToolErrorOutput]:
    print(f"PYDANTIC_TOOL: Calling perform_calculation for '{inputs.expression}'")
    try:
        allowed_chars = set("0123456789.+-*/() ")
        if not all(char in allowed_chars for char in inputs.expression):
            raise ValueError("Expression contains invalid characters.")
        if not inputs.expression.strip():
            raise ValueError("Expression cannot be empty.")
        
        # WARNING: eval is dangerous. Use a safer math parser in production.
        result_val = float(eval(inputs.expression))
        return PerformCalculationOutput(expression=inputs.expression, result=result_val)
    except Exception as e:
        return ToolErrorOutput(error=f"Calculation error: {str(e)}", details={"expression": inputs.expression})


# --- Agent with Pydantic-aware Tool Usage ---

class PydanticToolAgent:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {
            "get_weather": {
                "function": get_weather_pydantic,
                "input_model": GetWeatherInput,
                "output_model": WeatherOutput # Could also be Union[WeatherOutput, ToolErrorOutput]
            },
            "search_information": {
                "function": search_information_pydantic,
                "input_model": SearchInformationInput,
                "output_model": SearchInformationOutput
            },
            "perform_calculation": {
                "function": perform_calculation_pydantic,
                "input_model": PerformCalculationInput,
                "output_model": PerformCalculationOutput
            }
        }
        print("PydanticToolAgent initialized.")

    def _parse_and_validate_inputs(self, tool_name: str, raw_args: Dict[str, Any]) -> Optional[BaseModel]:
        tool_info = self.tools.get(tool_name)
        if not tool_info:
            return None
        try:
            validated_inputs = tool_info["input_model"](**raw_args)
            return validated_inputs
        except ValidationError as e:
            print(f"AGENT_ERROR: Input validation failed for tool '{tool_name}'. Errors:\n{e.errors()}")
            # For pretty print: print(f"AGENT_ERROR: ... Errors:\n{json.dumps(e.errors(), indent=2)}")
            return None

    def use_tool(self, tool_name: str, raw_args: Dict[str, Any]) -> Union[BaseModel, ToolErrorOutput, Dict[str, Any]]:
        if tool_name not in self.tools:
            return ToolErrorOutput(error=f"Tool '{tool_name}' not found.")

        validated_inputs = self._parse_and_validate_inputs(tool_name, raw_args)
        if not validated_inputs:
            return ToolErrorOutput(error=f"Invalid inputs for tool '{tool_name}'.", details=raw_args)

        tool_function = self.tools[tool_name]["function"]
        print(f"AGENT: Attempting to use Pydantic tool '{tool_name}' with validated inputs: {validated_inputs.model_dump_json(indent=2)}")
        try:
            result = tool_function(validated_inputs) # Pass the Pydantic model instance
            print(f"AGENT: Tool '{tool_name}' executed. Raw Result: {result}")
            
            # Optionally, validate output (though tools should return valid models)
            # output_model = self.tools[tool_name]["output_model"]
            # if isinstance(result, output_model) or (isinstance(result, ToolErrorOutput)):
            #    return result
            # else: 
            #    print(f"AGENT_WARNING: Tool '{tool_name}' output type mismatch!")
            #    return ToolErrorOutput(error=f"Tool '{tool_name}' produced unexpected output type.")
            return result

        except Exception as e:
            return ToolErrorOutput(error=f"Unexpected error executing tool '{tool_name}': {str(e)}")

    # Simplified process_request for demonstration
    def process_request_with_tool(self, tool_name: str, args: Dict[str, Any]):
        print(f"\nAGENT: Processing request to use tool '{tool_name}' with args: {args}")
        tool_output = self.use_tool(tool_name, args)

        if isinstance(tool_output, ToolErrorOutput):
            print(f"AGENT_RESPONSE: Error from tool: {tool_output.model_dump_json(indent=2)}")
        elif isinstance(tool_output, BaseModel):
            print(f"AGENT_RESPONSE: Success! Output: {tool_output.model_dump_json(indent=2)}")
        else: # Should not happen if tools return Pydantic models or ToolErrorOutput
            print(f"AGENT_RESPONSE: Unexpected output format: {tool_output}")
        return tool_output

# --- Example Usage ---
if __name__ == "__main__":
    pydantic_agent = PydanticToolAgent()

    # Weather tool examples
    pydantic_agent.process_request_with_tool("get_weather", {"location": "London, UK"})
    pydantic_agent.process_request_with_tool("get_weather", {"location": ""}) # Invalid input
    pydantic_agent.process_request_with_tool("get_weather", {"city": "Paris"}) # Missing 'location' field
    pydantic_agent.process_request_with_tool("get_weather", {"location": "unknown_city"}) # Tool specific error

    # Search tool examples
    pydantic_agent.process_request_with_tool("search_information", {"query": "FastAPI Pydantic integration"})
    pydantic_agent.process_request_with_tool("search_information", {"query": "AI"}) # Too short if min_length was enforced more strictly by agent
    pydantic_agent.process_request_with_tool("search_information", {})

    # Calculation tool examples
    pydantic_agent.process_request_with_tool("perform_calculation", {"expression": "(100 / 5) + 22"})
    pydantic_agent.process_request_with_tool("perform_calculation", {"expression": "100 / 0"})
    pydantic_agent.process_request_with_tool("perform_calculation", {"expression": "abc + 1"}) # Invalid expression
    pydantic_agent.process_request_with_tool("non_existent_tool", {"arg": "value"})


# --- Key Takeaways for Pydantic in Agentic Flows ---
# - Schema Definition: Use Pydantic models to rigorously define the expected structure of data for tool inputs and outputs.
# - Input Validation: Pydantic automatically validates incoming data against your models, catching errors early.
#   The agent can catch `ValidationError` or check if parsing to the Pydantic model fails.
# - Output Parsing: When a tool returns data (e.g., JSON from an API), parse it into a Pydantic model to ensure it conforms to expectations.
# - Structured Agent Memory/State: Pydantic can also structure an agent's internal thoughts, plans, or memory elements.
# - Tool Discovery and Description: Pydantic model schemas can be used to automatically generate descriptions of tools
#   and their parameters, which can be useful for LLMs or other systems to understand how to use them. 