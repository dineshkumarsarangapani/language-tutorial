# celery_app_setup.py for Agentic Flows Tutorial

from celery import Celery

# --- Celery Application Setup ---
# This file defines the Celery application instance.
# To run Celery workers, you would typically point them to this app instance.

# Requirements for this example:
# - Celery: `pip install celery`
# - A message broker (e.g., Redis or RabbitMQ). For Redis: `pip install redis`
#   You need to have a Redis server running. Example connection URL for local Redis: `redis://localhost:6379/0`
#   For RabbitMQ, the URL would be like: `amqp://guest:guest@localhost:5672//`

# For simplicity, we'll use Redis as the broker and also as the result backend.
# In a production setup, you might choose different brokers or result backends based on needs.

# IMPORTANT: Replace with your actual broker URL
# Ensure your Redis server is running if you use this.
CELERY_BROKER_URL = 'redis://localhost:6379/0' # Example for local Redis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0' # Example for local Redis

# If you don't have Redis/RabbitMQ running, Celery workers won't connect.
# The FastAPI app can still try to send tasks, but they won't be processed without workers.

celery_agent_app = Celery(
    'agent_tasks', # A name for the task namespace, often the module name where tasks are defined
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['agentic_flows_tutorial.agent_tasks'] # List of modules to import when a worker starts
)

# Optional Celery configuration (can also be in a separate config file)
celery_agent_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Example: a simple route for specific tasks to a specific queue
    # task_routes=({
    #     'agentic_flows_tutorial.agent_tasks.long_document_processing_task': {'queue': 'long_tasks'},
    # },),
)

if __name__ == '__main__':
    # This allows you to run a worker directly using this file for testing:
    # `python celery_app_setup.py worker -l info`
    # Ensure your broker (e.g., Redis) is running.
    print("Celery app configured. To start a worker (ensure Redis or your broker is running):")
    print(f"celery -A {__name__}:celery_agent_app worker -l info -P eventlet") # Use -P eventlet or gevent on Windows
    print("Or, if your tasks are in agent_tasks.py and this is celery_app_setup.py:")
    print("celery -A celery_app_setup:celery_agent_app worker -l info") 