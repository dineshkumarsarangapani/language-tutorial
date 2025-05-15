from fastapi import FastAPI, BackgroundTasks, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import the Celery app instance and tasks
# This assumes celery_app_setup.py and agent_tasks.py are in the same directory
# or accessible via Python path. The __init__.py helps make this a package.
from .celery_app_setup import celery_agent_app
from .agent_tasks import process_large_data_task, send_agent_report_email_task, simple_log_task

# For retrieving task results/status
from celery.result import AsyncResult

app = FastAPI(title="FastAPI with Celery for Agentic Flows")

# --- Pydantic Models for Request/Response ---
class DataPayload(BaseModel):
    data_id: str
    items: List[Dict[str, Any]]
    user_email: str

class ReportPayload(BaseModel):
    recipient_email: str
    report_title: str
    report_body: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    progress: Optional[Dict[str, Any]] = None # For tasks that report progress

# --- FastAPI Endpoints to Dispatch Celery Tasks ---

@app.post("/process-data-async", status_code=202) # 202 Accepted: request accepted, processing not complete
async def trigger_data_processing(payload: DataPayload) -> Dict[str, str]:
    """
    Receives data and dispatches a long-running processing task to Celery.
    Also sends a simple log task and an email report task.
    """
    print(f"FastAPI: Received request to process data for ID: {payload.data_id}")

    # Send the main data processing task to Celery
    # .delay() is a shortcut for .send_task().apply_async()
    task_main = process_large_data_task.delay(data_id=payload.data_id, data_chunk=payload.items)
    print(f"FastAPI: Dispatched process_large_data_task with ID: {task_main.id}")

    # Send a simple logging task
    task_log = simple_log_task.delay(message=f"Data processing initiated for {payload.data_id}")
    print(f"FastAPI: Dispatched simple_log_task with ID: {task_log.id}")

    # Send an email report task after a slight conceptual delay (tasks are async anyway)
    report_content = f"Processing for data ID '{payload.data_id}' involving {len(payload.items)} items has started."
    task_email = send_agent_report_email_task.delay(
        recipient_email=payload.user_email, 
        report_content=report_content
    )
    print(f"FastAPI: Dispatched send_agent_report_email_task with ID: {task_email.id}")

    return {
        "message": "Data processing tasks dispatched. Check task status for progress.",
        "main_processing_task_id": task_main.id,
        "logging_task_id": task_log.id,
        "email_task_id": task_email.id
    }

@app.post("/send-report-async", status_code=202)
async def trigger_send_report(payload: ReportPayload) -> Dict[str, str]:
    """Dispatches an email sending task to Celery."""
    print(f"FastAPI: Received request to send report to: {payload.recipient_email}")
    task = send_agent_report_email_task.delay(
        recipient_email=payload.recipient_email, 
        report_content=f"{payload.report_title}\n\n{payload.report_body}"
    )
    print(f"FastAPI: Dispatched send_agent_report_email_task with ID: {task.id}")
    return {"message": "Report sending task dispatched.", "task_id": task.id}


@app.get("/task-status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Retrieves the status and result of a Celery task."""
    print(f"FastAPI: Checking status for task ID: {task_id}")
    task_result = AsyncResult(task_id, app=celery_agent_app)
    
    response_data = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None,
        "progress": None
    }

    if task_result.successful():
        response_data["result"] = task_result.get() # Get the actual result
    elif task_result.failed():
        # Get the exception details if it failed
        # result.traceback might be large, so be cautious in production
        response_data["result"] = str(task_result.info) if task_result.info else "Task failed without specific info."
    elif task_result.status == 'PENDING':
        response_data["result"] = "Task is pending or not found. Ensure workers are running and task ID is correct."
    elif task_result.status == 'PROGRESS':
        response_data["progress"] = task_result.info # Contains meta like {'current': ..., 'total': ...}
        response_data["result"] = "Task is in progress."
    else:
        response_data["result"] = f"Task in state: {task_result.status}"
        if task_result.info: # Some other states might have info
             response_data["progress"] = task_result.info 

    return TaskStatusResponse(**response_data)

# --- How to Run This Example ---
# 1. Ensure you have a message broker (e.g., Redis) running.
#    Update `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` in `celery_app_setup.py` if needed.
#
# 2. Start Celery worker(s) in your project's root directory (where `agentic_flows_tutorial` is a subdir):
#    Navigate one level up from `agentic_flows_tutorial` if you are inside it.
#    Command: `celery -A agentic_flows_tutorial.celery_app_setup:celery_agent_app worker -l info -P eventlet`
#    (Use `-P eventlet` or `-P gevent` on Windows if you encounter issues with the default pool).
#    You should see the worker connect and discover the tasks from `agent_tasks.py`.
#
# 3. Start this FastAPI application:
#    `uvicorn agentic_flows_tutorial.4_fastapi_with_celery:app --reload --port 8000`
#    (Adjust path if running from a different directory)
#
# 4. Interact with the API:
#    - Go to http://127.0.0.1:8000/docs
#    - Try the `/process-data-async` endpoint with a sample JSON payload like:
#      ```json
#      {
#        "data_id": "doc123",
#        "items": [{"value": 1}, {"value": 2}, {"value": 3}],
#        "user_email": "user@example.com"
#      }
#      ```
#    - Copy the returned `main_processing_task_id`.
#    - Use the `/task-status/{task_id}` endpoint with that ID to check its progress/completion.
#    - Observe the Celery worker logs and FastAPI application logs.

print("--- FastAPI with Celery for Agentic Flows ---")
print("This app dispatches tasks to Celery workers and can check their status.")
print("Ensure your Celery workers are running and connected to the broker.") 