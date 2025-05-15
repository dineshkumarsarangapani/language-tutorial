# 3. Control Flow and Orchestration in Agentic Flows

from typing import Dict, Any, List, Callable, Optional

# Import concepts from previous files (assuming they are in the same directory or accessible)
# For simplicity in this standalone example, we might redefine simplified versions
# or assume their interfaces.

# Let's use simplified versions of State and Tool concepts for clarity here,
# focusing on the orchestration logic itself.

# --- What is Orchestration in Agentic Flows? ---
# Orchestration is the process of coordinating multiple steps, components, and decisions
# to achieve a larger goal. An orchestrator acts like a conductor, managing:
# - The sequence of operations (which can be dynamic).
# - Invoking different tools or services.
# - Managing and transitioning state (often using a state machine).
# - Handling results and errors from sub-components.
# - Making decisions based on current context and incoming data.

# For complex agents, a dedicated orchestrator logic is crucial for maintainability
# and clarity, rather than embedding all control flow within a single monolithic block.

# --- Simplified Tool Definitions (similar to 2_tool_usage.py) ---
def get_current_time() -> Dict[str, Any]:
    import datetime
    print("TOOL_ORCH: get_current_time called")
    return {"current_time": datetime.datetime.now().isoformat()}

def query_knowledge_base(question: str) -> Dict[str, Any]:
    print(f"TOOL_ORCH: query_knowledge_base called with question: '{question}'")
    # Simulated KB
    kb = {
        "what is the capital of france?": "The capital of France is Paris.",
        "what is python?": "Python is a high-level, interpreted programming language."
    }
    answer = kb.get(question.lower().strip(), "I don't have information on that specific question.")
    return {"question": question, "answer": answer}

# --- Simple Orchestrator Example ---

class SimpleOrchestrator:
    def __init__(self):
        self.tools: Dict[str, Callable[..., Dict[str, Any]]] = {
            "get_current_time": get_current_time,
            "query_knowledge_base": query_knowledge_base
        }
        self.max_steps = 5 # To prevent infinite loops in this simple example
        self.history: List[Dict[str, Any]] = [] # To store interaction history
        print("SimpleOrchestrator initialized.")

    def _log_step(self, action_type: str, details: Any, result: Optional[Any] = None):
        step_log = {"action_type": action_type, "details": details}
        if result is not None:
            step_log["result"] = result
        self.history.append(step_log)
        print(f"ORCH_LOG: {step_log}")

    def _decide_next_action(self, current_goal: str, last_tool_result: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Very basic decision logic. Returns a dict describing the next action or None to stop."""
        print(f"ORCH_DECIDE: Goal='{current_goal}', LastResult={last_tool_result}")
        
        if "time" in current_goal.lower():
            # If the goal involves time and we haven't just used the time tool, use it.
            if not last_tool_result or "current_time" not in last_tool_result:
                return {"tool_name": "get_current_time", "args": {}}
        
        if "capital of france" in current_goal.lower() and (not last_tool_result or "Paris" not in str(last_tool_result.get("answer"))):
             return {"tool_name": "query_knowledge_base", "args": {"question": "What is the capital of France?"}}

        if "python definition" in current_goal.lower() and (not last_tool_result or "programming language" not in str(last_tool_result.get("answer"))):
            return {"tool_name": "query_knowledge_base", "args": {"question": "What is Python?"}}

        # If no specific tool matches or if the last tool provided the answer for the goal, stop.
        if last_tool_result is not None:
            if "error" not in last_tool_result:
                if current_goal.lower() == "what is the time?" and "current_time" in last_tool_result:
                    return None # Goal achieved
                if "capital of france" in current_goal.lower() and "Paris" in str(last_tool_result.get("answer")):
                    return None # Goal achieved
                if "python definition" in current_goal.lower() and "programming language" in str(last_tool_result.get("answer")):
                    return None # Goal achieved

        # Fallback or if goal is not tool-related for this simple orchestrator
        if not last_tool_result and "search" in current_goal.lower(): # Generic search if no other tool fits
             return {"tool_name": "query_knowledge_base", "args": {"question": current_goal.replace("search for ","")}} 

        return None # Cannot decide or goal seems met/unclear

    def execute_task(self, initial_goal: str) -> Dict[str, Any]:
        print(f"\nORCH_EXEC: Starting task with goal: '{initial_goal}'")
        self.history = [] # Reset history for new task
        self._log_step("task_start", {"goal": initial_goal})

        current_goal = initial_goal
        last_tool_result: Optional[Dict[str, Any]] = None
        final_answer = "Could not complete the task to your satisfaction."

        for step_count in range(self.max_steps):
            print(f"  Step {step_count + 1}/{self.max_steps}")
            next_action = self._decide_next_action(current_goal, last_tool_result)

            if next_action is None:
                self._log_step("decision", "No further action decided or goal achieved.")
                if last_tool_result is not None:
                    if "error" not in last_tool_result:
                        final_answer = f"Based on the information gathered: {last_tool_result}"
                break

            tool_name = next_action["tool_name"]
            tool_args = next_action["args"]

            if tool_name in self.tools:
                tool_function = self.tools[tool_name]
                self._log_step("tool_selection", {"tool_name": tool_name, "arguments": tool_args})
                try:
                    last_tool_result = tool_function(**tool_args)
                    self._log_step("tool_execution", {"tool_name": tool_name}, result=last_tool_result)
                    if "error" in last_tool_result:
                        final_answer = f"An error occurred while using {tool_name}: {last_tool_result['error']}"
                        self._log_step("task_end", {"status": "failed", "reason": final_answer})
                        return {"goal": initial_goal, "status": "failed", "answer": final_answer, "history": self.history}
                except Exception as e:
                    last_tool_result = {"error": f"Orchestrator failed to execute tool {tool_name}: {e}"}
                    self._log_step("tool_execution_error", {"tool_name": tool_name}, result=last_tool_result)
                    final_answer = last_tool_result["error"]
                    break # Stop on critical tool execution error
            else:
                self._log_step("error", f"Selected tool '{tool_name}' not found in orchestrator.")
                final_answer = f"Internal error: tool '{tool_name}' not recognized."
                break
        else: # Loop completed max_steps without breaking
            self._log_step("max_steps_reached", f"Task stopped after {self.max_steps} steps.")
            if not last_tool_result or "error" in last_tool_result:
                 final_answer = f"Task took too many steps to complete. Last known info: {last_tool_result if last_tool_result else 'None'}"
            else:
                final_answer = f"After {self.max_steps} steps, the result is: {last_tool_result}"


        self._log_step("task_end", {"status": "completed", "final_answer_summary": final_answer[:100]+"..." if len(final_answer) > 100 else final_answer})
        return {"goal": initial_goal, "status": "completed", "answer": final_answer, "history": self.history}

# --- Example Usage ---
if __name__ == "__main__":
    orchestrator = SimpleOrchestrator()

    result1 = orchestrator.execute_task("What is the time?")
    print(f"FINAL_ANSWER for 'What is the time?': {result1['answer']}")
    # print("History for task 1:", json.dumps(result1['history'], indent=2))

    result2 = orchestrator.execute_task("Tell me about the capital of France and then what is the time.") 
    # This goal is a bit complex for the current _decide_next_action, it will likely do one or stop.
    print(f"FINAL_ANSWER for 'capital of France and time': {result2['answer']}")

    result3 = orchestrator.execute_task("Define python for me.") # Should try to map to "python definition"
    print(f"FINAL_ANSWER for 'Define python': {result3['answer']}")

    result4 = orchestrator.execute_task("search for LLM agents") # Generic search
    print(f"FINAL_ANSWER for 'search for LLM agents': {result4['answer']}")

# --- Key Takeaways for Orchestration ---
# - Separation of Concerns: The orchestrator focuses on the "how" and "when", 
#   while tools/state machines focus on the "what".
# - Decision Making: The `_decide_next_action` (or similar) is the core "brain". 
#   In real agents, this could involve LLM calls, complex rule sets, or planning algorithms.
# - State & History: Maintaining history and current state is vital for context-aware decisions.
# - Error Handling: Orchestrators must gracefully handle failures in tools or decision logic.
# - Scalability: For very complex flows, consider dedicated workflow engines or libraries 
#   (e.g., Celery for distributing tasks, Temporal, Prefect, Dagster for workflows).
# - Extensibility: Design the orchestrator to easily add new tools, states, or decision rules. 