# agent_tasks.py for Agentic Flows Tutorial

from agentic_flows_tutorial.celery_app_setup import celery_agent_app # Import the Celery app instance
import time
import random

# --- Defining Celery Tasks ---
# Celery tasks are functions decorated with `@celery_agent_app.task`.
# These functions will be executed by Celery workers in the background.

@celery_agent_app.task(bind=True, name="process_large_data_task") # `bind=True` makes `self` (the task instance) available
def process_large_data_task(self, data_id: str, data_chunk: list):
    """Simulates a long-running task that processes a chunk of data."""
    task_id = self.request.id
    print(f"CELERY_TASK (ID: {task_id}): Starting to process data_id '{data_id}' with {len(data_chunk)} items.")
    
    total_items = len(data_chunk)
    processed_items = 0
    
    for i, item in enumerate(data_chunk):
        # Simulate work for each item
        time.sleep(random.uniform(0.05, 0.2))
        processed_items += 1
        
        # Update task state for progress tracking (optional)
        if i % (total_items // 10 if total_items > 10 else 1) == 0 or i == total_items - 1:
            progress = (processed_items / total_items) * 100
            self.update_state(
                state='PROGRESS',
                meta={'current': processed_items, 'total': total_items, 'percent': round(progress, 2)}
            )
            print(f"CELERY_TASK (ID: {task_id}): Processed {processed_items}/{total_items} for '{data_id}'.")

    result_summary = f"Successfully processed {total_items} items for data_id '{data_id}'."
    print(f"CELERY_TASK (ID: {task_id}): {result_summary}")
    return {"data_id": data_id, "items_processed": total_items, "status": "Completed", "summary": result_summary}

@celery_agent_app.task(name="send_agent_report_email_task", max_retries=3, default_retry_delay=60) # Retry on failure
def send_agent_report_email_task(recipient_email: str, report_content: str):
    """Simulates sending an email report. Can be retried on failure."""
    print(f"CELERY_TASK: Attempting to send report to '{recipient_email}'.")
    
    # Simulate a chance of failure for email sending
    if random.random() < 0.3: # 30% chance of failure
        error_message = "Simulated failure: Email service temporarily unavailable."
        print(f"CELERY_TASK: Failed to send email to '{recipient_email}'. Error: {error_message}")
        # This will cause Celery to retry the task based on max_retries and default_retry_delay
        raise Exception(error_message) 
    
    time.sleep(2) # Simulate email sending delay
    print(f"CELERY_TASK: Email report successfully sent to '{recipient_email}'. Content hash: {hash(report_content)}")
    return {"recipient": recipient_email, "status": "Email Sent", "content_length": len(report_content)}

@celery_agent_app.task(name="simple_log_task")
def simple_log_task(message: str):
    """A very simple task that just logs a message."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    log_entry = f"{timestamp} - CELERY_TASK_LOG: {message}"
    print(log_entry)
    # In a real app, this might write to a dedicated log file or system.
    return {"logged_message": message, "status": "Logged"}

# To make these tasks discoverable, ensure this module is included in the
# `celery_agent_app.conf.include` list in `celery_app_setup.py`.
# (Which we did: `include=['agentic_flows_tutorial.agent_tasks']`)

# When a Celery worker starts, it will import these tasks. 