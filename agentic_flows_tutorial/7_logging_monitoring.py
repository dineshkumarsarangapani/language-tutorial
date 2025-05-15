# 7. Logging and Monitoring Agentic Flows

import logging
import logging.config
from typing import Dict, Any, Callable, Optional, List, Union
from pydantic import BaseModel, ValidationError # For tool input validation
import uuid # For generating unique flow IDs
import json # For pretty printing
import time # Added time

# --- Why Logging and Monitoring is Crucial for Agents ---
# - **Debugging:** Agentic flows can be complex. Detailed logs help trace behavior and pinpoint issues.
# - **Observability:** Understand what the agent is doing, its decisions, and its interactions.
# - **Performance Analysis:** Identify bottlenecks or frequently failing tools/steps.
# - **Auditing:** Keep a record of agent actions, especially if they interact with critical systems or data.
# - **Error Tracking:** Capture and analyze errors to improve agent robustness.

# --- Setting up Python `logging` for Agentic Flows ---

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "agent_flow_formatter": {
            "format": "%(asctime)s - FLOW_ID:%(flow_id)s - AGENT:%(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "agent_flow_formatter",
            "level": "DEBUG"
        },
        # Optionally, add a file handler:
        # "file_handler": {
        #     "class": "logging.FileHandler",
        #     "formatter": "agent_flow_formatter",
        #     "filename": "agent_flow.log",
        #     "level": "INFO"
        # }
    },
    "loggers": {
        "AgentSystem": { # A root logger for our agent components
            "handlers": ["console_handler"], # Add 'file_handler' here if using
            "level": "DEBUG",
            "propagate": False # Don't pass messages to the root Python logger
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

# --- Helper to get a logger with flow_id ---
# This allows us to pass the flow_id into log messages easily using LogRecord a factory
# A more robust way might involve contextvars for flow_id if dealing with async/threading heavily.

_original_logrecord_factory = logging.getLogRecordFactory()

def agent_log_record_factory(*args, **kwargs):
    record = _original_logrecord_factory(*args, **kwargs)
    record.flow_id = getattr(logging, 'flow_id', 'GLOBAL') # Get flow_id from logging module's namespace
    return record

logging.setLogRecordFactory(agent_log_record_factory)

# --- Simplified Pydantic Models and Tools (from previous examples) ---
class BasicToolInput(BaseModel):
    param: str

class BasicToolOutput(BaseModel):
    result: str
    param_received: str

class ErrorOutput(BaseModel):
    error: str
    details: Optional[Any] = None

def example_tool_1(inputs: BasicToolInput) -> Union[BasicToolOutput, ErrorOutput]:
    logger = logging.getLogger("AgentSystem.Tools.ExampleTool1")
    logger.info(f"Executing with inputs: {inputs.model_dump_json()}", extra={"flow_id": getattr(logging, 'flow_id', 'N/A')})
    if inputs.param == "fail":
        logger.error("Simulated failure in tool.")
        return ErrorOutput(error="Simulated tool failure", details={"input_param": inputs.param})
    time.sleep(0.1) # Simulate work
    return BasicToolOutput(result=f"Tool 1 processed '{inputs.param}' successfully.", param_received=inputs.param)

# --- Agent with Enhanced Logging ---
class LoggingAgent:
    def __init__(self, agent_name: str = "MyLoggingAgent"):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"AgentSystem.{self.agent_name}") # Specific logger for this agent instance
        self.tools: Dict[str, Callable[[BaseModel], Union[BaseModel, ErrorOutput]]] = {
            "example_tool_1": example_tool_1
        }
        self.logger.info("Agent initialized.")

    def _execute_tool(self, tool_name: str, tool_input_model: BaseModel) -> Union[BaseModel, ErrorOutput]:
        if tool_name not in self.tools:
            self.logger.error(f"Tool '{tool_name}' not found.")
            return ErrorOutput(error=f"Tool '{tool_name}' not configured for this agent.")
        
        tool_function = self.tools[tool_name]
        self.logger.info(f"Attempting to execute tool '{tool_name}'.")
        try:
            # Pydantic model is already validated if it reaches here as an instance
            tool_result = tool_function(tool_input_model)
            if isinstance(tool_result, ErrorOutput):
                self.logger.warning(f"Tool '{tool_name}' executed but returned an error: {tool_result.error}")
            else:
                self.logger.info(f"Tool '{tool_name}' executed successfully.")
            return tool_result
        except Exception as e:
            self.logger.exception(f"Unexpected critical error during '{tool_name}' execution.")
            return ErrorOutput(error=f"Critical failure in tool '{tool_name}': {str(e)}")

    def process_task(self, task_description: str, task_data: Dict[str, Any]):
        flow_id = str(uuid.uuid4())[:8] # Generate a unique ID for this flow/task
        setattr(logging, 'flow_id', flow_id) # Make flow_id available to the log record factory

        self.logger.info(f"Starting new task. Description: '{task_description}'. Initial data: {json.dumps(task_data)}")

        # Simplified logic: Assume task_data contains tool name and params
        tool_to_use = task_data.get("tool_name")
        raw_tool_params = task_data.get("parameters")

        if not tool_to_use or raw_tool_params is None:
            self.logger.error("Task definition is missing tool_name or parameters.")
            setattr(logging, 'flow_id', 'GLOBAL') # Reset flow_id
            return {"status": "Error", "message": "Invalid task structure.", "flow_id": flow_id}
        
        # Assume we have an input model for the tool (not shown in this simplified agent for brevity, but good practice)
        # For this example, let's assume example_tool_1 and BasicToolInput
        if tool_to_use == "example_tool_1":
            try:
                tool_input_data = BasicToolInput(**raw_tool_params)
            except ValidationError as ve:
                self.logger.error(f"Input validation failed for tool '{tool_to_use}': {ve.errors()}")
                setattr(logging, 'flow_id', 'GLOBAL')
                return {"status": "Error", "message": "Tool input validation failed.", "details": ve.errors(), "flow_id": flow_id}
        else:
            self.logger.error(f"No input model schema defined for tool '{tool_to_use}'. Cannot proceed.")
            setattr(logging, 'flow_id', 'GLOBAL')
            return {"status": "Error", "message": f"Schema missing for '{tool_to_use}'.", "flow_id": flow_id}

        self.logger.debug(f"Decision: Use tool '{tool_to_use}' with validated params: {tool_input_data.model_dump_json()}")
        
        tool_result = self._execute_tool(tool_to_use, tool_input_data)

        final_status = "Completed"
        final_message = "Task processed."
        result_payload = None

        if isinstance(tool_result, ErrorOutput):
            final_status = "Failed"
            final_message = f"Task failed due to tool error: {tool_result.error}"
            result_payload = tool_result.model_dump()
            self.logger.error(final_message)
        elif isinstance(tool_result, BaseModel):
            final_message = f"Task completed successfully using tool '{tool_to_use}'."
            result_payload = tool_result.model_dump()
            self.logger.info(final_message)
        else:
            final_status = "Error"
            final_message = "Tool returned unexpected data type."
            self.logger.critical(f"{final_message} Type: {type(tool_result)}")

        self.logger.info(f"Task finished. Status: {final_status}.")
        setattr(logging, 'flow_id', 'GLOBAL') # Reset flow_id for the next potential independent log
        return {"status": final_status, "message": final_message, "result": result_payload, "flow_id": flow_id}

# --- Example Usage ---
if __name__ == "__main__":
    import time # for example_tool_1 simulation
    agent = LoggingAgent(agent_name="DemoLoggerAgent")

    print("\n--- Running Task 1: Successful Tool Call ---")
    task1_data = {"tool_name": "example_tool_1", "parameters": {"param": "hello world"}}
    result1 = agent.process_task("Process a greeting", task1_data)
    print(f"Task 1 Result: {json.dumps(result1, indent=2)}")

    print("\n--- Running Task 2: Tool Call that Fails Internally ---")
    task2_data = {"tool_name": "example_tool_1", "parameters": {"param": "fail"}}
    result2 = agent.process_task("Simulate a tool failure", task2_data)
    print(f"Task 2 Result: {json.dumps(result2, indent=2)}")

    print("\n--- Running Task 3: Invalid Input for Tool ---")
    task3_data = {"tool_name": "example_tool_1", "parameters": {"wrong_param_name": "test"}}
    result3 = agent.process_task("Test input validation", task3_data)
    print(f"Task 3 Result: {json.dumps(result3, indent=2)}")

    print("\n--- Running Task 4: Non-existent Tool ---")
    task4_data = {"tool_name": "non_existent_tool", "parameters": {"param": "test"}}
    result4 = agent.process_task("Test non-existent tool", task4_data)
    print(f"Task 4 Result: {json.dumps(result4, indent=2)}")

# --- Key Takeaways for Logging in Agents ---
# - **Structured Logging:** Use formatters that include important contextual information (timestamp, agent name, flow/session ID, severity).
# - **Flow/Session IDs:** Crucial for tracing a single multi-step operation through logs.
# - **Log Levels:** Use appropriate levels (DEBUG for detailed tracing, INFO for general progress, WARNING for recoverable issues, ERROR for problems, CRITICAL for severe failures).
# - **What to Log:**
#   - Agent/task initialization and termination.
#   - Key decisions (e.g., tool selection, state changes).
#   - Tool calls: name, input parameters (be mindful of sensitive data).
#   - Tool responses: summary or full response (again, mind PII/sensitive data).
#   - Errors: both exceptions caught by the agent and errors reported by tools.
#   - State transitions if using a state machine.
# - **Avoid Sensitive Data in Logs (or mask it):** Be careful not to log PII, API keys, etc., unless appropriately secured/masked.
# - **Centralized Logging:** In production, send logs to a centralized logging system (e.g., ELK stack, Splunk, CloudWatch) for easier analysis and monitoring.
# - **Log Record Factory/Contextvars:** For passing contextual info like `flow_id` to all log messages within a specific execution flow, especially in async or threaded environments. 