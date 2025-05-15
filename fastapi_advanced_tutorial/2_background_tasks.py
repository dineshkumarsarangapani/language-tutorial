# 2. Background Tasks

from fastapi import FastAPI, BackgroundTasks, Depends
from typing import Annotated
import time
import os # For a slightly more realistic task

app = FastAPI()

# --- What are Background Tasks? ---
# Background tasks are operations that you need to perform after returning a response
# to the client. This is useful for tasks that are not critical for the immediate
# response and might take some time, such as sending an email notification,
# processing data, generating a report, etc.
# The client doesn't have to wait for these tasks to complete.

# --- How to use BackgroundTasks ---
# 1. Add `BackgroundTasks` as a parameter to your path operation function.
#    FastAPI will automatically inject an instance of `BackgroundTasks`.
# 2. Use the `add_task()` method on the `BackgroundTasks` instance to add a
#    function to be run in the background. You pass the function itself and any
#    arguments it needs.

# --- Example Functions to be run in the background ---
def write_log_message(log_file: str, message: str):
    # Simulate a task that takes some time (e.g., I/O operation)
    time.sleep(2)
    with open(log_file, mode="a") as f:
        f.write(f"{time.ctime()}: {message}\n")
    print(f"Background task: Log message written to '{log_file}'.")

def send_email_notification(email: str, subject: str, content: str):
    # Simulate sending an email
    time.sleep(3)
    print(f"Background task: Email supposedly sent to '{email}' with subject '{subject}'.")
    print(f"  Content: {content}")
    # In a real app, you'd use smtplib or an email service SDK here.

# --- Path Operations using BackgroundTasks ---

# Ensure the directory for log files exists
LOG_DIR = "fastapi_logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

TEMP_LOG_FILE = os.path.join(LOG_DIR, "temp_app_log.txt")

@app.post("/send-notification/{email}")
async def send_notification_endpoint(email: str, message_body: dict, background_tasks: BackgroundTasks):
    """
    Sends a notification. The actual email sending is done in the background.
    """
    subject = f"Notification: {message_body.get('title', 'Important Update')}"
    content = message_body.get('body', 'Something happened!')
    
    # Add tasks to be run after the response is sent
    background_tasks.add_task(write_log_message, TEMP_LOG_FILE, f"Notification sent to {email}")
    background_tasks.add_task(send_email_notification, email, subject, content)
    
    print(f"Endpoint /send-notification: Response being sent for {email}. Email will be sent in background.")
    return {"message": "Notification sending process initiated", "recipient": email}


# --- Background Tasks with Dependencies ---
# If a background task needs a resource managed by a dependency (like a DB session),
# you need to be careful. The dependency's teardown phase (after `yield`) might
# run before the background task completes, closing the resource prematurely.

# Solution: Pass the necessary data/session directly to the background task function,
# or create a new session/resource within the background task itself.

# Simulated DB session (very basic for illustration)
class DBSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.is_active = True
        print(f"DBSession {self.session_id}: Created and active.")

    def close(self):
        self.is_active = False
        print(f"DBSession {self.session_id}: Closed.")

    def execute_query(self, query: str):
        if not self.is_active:
            print(f"DBSession {self.session_id}: Error! Query '{query}' on closed session.")
            return False
        print(f"DBSession {self.session_id}: Executing '{query}'.")
        return True

async def get_db_session(): # Dependency with yield
    session_id = f"sess_{int(time.time()*1000)}"
    db_session = DBSession(session_id)
    try:
        yield db_session
    finally:
        db_session.close()

# Incorrect way (db_session might be closed by the time the task runs)
# def unsafe_background_db_task(db: DBSession, user_id: int, data: str):
#     time.sleep(1) # Simulate delay, by now db_session from Depends might be closed
#     print(f"Unsafe BG Task: Attempting to use DB session {db.session_id} for user {user_id}")
#     db.execute_query(f"UPDATE users SET data = '{data}' WHERE id = {user_id}")

# Corrected way: Pass necessary data or create a new session inside the task
def safe_background_db_task_with_new_session(user_id: int, data: str):
    # Create a new session specifically for this background task
    # (or fetch necessary data before adding the task)
    task_session = DBSession(f"bg_task_sess_{user_id}")
    time.sleep(1)
    print(f"Safe BG Task: Using its own DB session {task_session.session_id} for user {user_id}")
    task_session.execute_query(f"UPDATE users SET data = '{data}' WHERE id = {user_id}")
    task_session.close() # Clean up the session created by the task

@app.post("/update-user-data/{user_id}")
async def update_user_data(
    user_id: int, 
    data: dict,
    background_tasks: BackgroundTasks,
    # current_db_session: Annotated[DBSession, Depends(get_db_session)] # This session is for the request path
):
    user_update_data = data.get("info", "default_info")
    
    # This would be unsafe if unsafe_background_db_task used current_db_session:
    # background_tasks.add_task(unsafe_background_db_task, current_db_session, user_id, user_update_data)
    
    # Safe way: the background task manages its own resources or uses data passed to it.
    background_tasks.add_task(safe_background_db_task_with_new_session, user_id, user_update_data)
    background_tasks.add_task(write_log_message, TEMP_LOG_FILE, f"User data update initiated for {user_id}")

    print(f"Endpoint /update-user-data: Data update for user {user_id} requested. Processing in background.")
    return {"message": f"User {user_id} data update initiated in background."}

# To run this example:
# 1. Save as a Python file (e.g., main_bg.py)
# 2. Run with Uvicorn: `uvicorn main_bg:app --reload`
# 3. Open your browser to http://127.0.0.1:8000/docs
#    - Try the `/send-notification/{email}` endpoint. You should get a quick response,
#      and see console logs for background tasks appearing after a delay.
#      Check the `fastapi_logs/temp_app_log.txt` file.
#    - Try the `/update-user-data/{user_id}` endpoint.

print("--- Background Tasks ---")
print("FastAPI application demonstrating background tasks.")
print("Tasks are executed after the HTTP response is sent.")
print("Run with: uvicorn filename:app --reload (e.g., uvicorn 2_background_tasks:app --reload)")
print(f"Log messages from background tasks will be written to: {os.path.abspath(TEMP_LOG_FILE)}") 