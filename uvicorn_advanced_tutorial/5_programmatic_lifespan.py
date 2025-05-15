# 5. Uvicorn: Programmatic Control & ASGI Lifespan

import uvicorn
import asyncio
import time
from fastapi import FastAPI
from contextlib import asynccontextmanager

# --- Programmatic Control of Uvicorn ---
# As seen in `1_advanced_configuration.py`, Uvicorn can be started from Python code.
# This offers fine-grained control over server setup and lifecycle, useful for:
# - Embedding Uvicorn in larger applications.
# - Custom startup/shutdown sequences beyond what CLI offers.
# - Integration testing where you need to start/stop a server.

# Method 1: `uvicorn.run()` - Simpler, blocking call.
# Method 2: `uvicorn.Config` and `uvicorn.Server` - More control, can be run non-blockingly with asyncio.

print("--- 1. Recap: Programmatic Uvicorn Execution ---")
def simple_programmatic_start_stop_example_concept():
    print("CONCEPT: Starting Uvicorn with uvicorn.run() on port 8001 (blocking)...")
    # uvicorn.run("uvicorn_advanced_tutorial.sample_asgi_app:app", host="127.0.0.1", port=8001, log_level="info")
    # This line would block here. In a real script, execution stops here until server is killed.
    print("CONCEPT: Server would have stopped here.")

async def controlled_programmatic_start_stop_example_concept():
    config = uvicorn.Config(
        app="uvicorn_advanced_tutorial.sample_asgi_app:app", 
        host="127.0.0.1", 
        port=8002, 
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    print("CONCEPT: Starting Uvicorn with uvicorn.Server on port 8002 (non-blocking with asyncio)...")
    # In a real application, you would typically run this in an event loop:
    # loop = asyncio.get_event_loop()
    # server_task = loop.create_task(server.serve())
    
    # Simulate server running for a bit
    # await asyncio.sleep(5) 
    
    # print("CONCEPT: Attempting to shut down server gracefully...")
    # server.should_exit = True # Signal server to exit
    # await server.shutdown() # Wait for graceful shutdown (if server.serve() is running)
    # Or if server_task was created: await server_task to ensure it finishes after should_exit is set.
    print("CONCEPT: Server would have started, run, and potentially shut down here.")

print("Refer to `1_advanced_configuration.py` for runnable examples of programmatic setup.")
print("The key is that `uvicorn.Server(config).serve()` can be `await`ed in an asyncio task,")
print("allowing other async operations to run concurrently or to manage its lifecycle.")


# --- 2. ASGI Lifespan Protocol ---
# ASGI applications can define "lifespan" events: `startup` and `shutdown`.
# - `startup`: Executed when Uvicorn starts up, before it begins accepting requests.
#   Useful for initializing resources (e.g., database connections, ML models, background tasks).
# - `shutdown`: Executed when Uvicorn is shutting down (e.g., on Ctrl+C or when signaled).
#   Useful for cleaning up resources (e.g., closing database connections, saving state).

# FastAPI uses a `lifespan` context manager for this.

print("\n\n--- 2. ASGI Lifespan Events (`startup` and `shutdown`) ---")

# This is a runnable example. Create `app_with_lifespan.py` or integrate into existing file.
app_with_lifespan_code = """
# app_with_lifespan.py (Example content)
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import time

# Simulate some resources that need setup/teardown
fake_db_connection = None
background_task_handle = None

async def simulate_background_task():
    count = 0
    while True:
        print(f"LIFESPAN_APP: Background task running... (Tick {count})")
        count += 1
        await asyncio.sleep(5) # Run every 5 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code here will run BEFORE the application starts accepting requests (startup)
    global fake_db_connection, background_task_handle
    print("LIFESPAN_APP: Startup event triggered!")
    print("LIFESPAN_APP: Initializing resources...")
    await asyncio.sleep(1) # Simulate async setup
    fake_db_connection = {"status": "connected", "id": int(time.time())}
    print(f"LIFESPAN_APP: Database connection established: {fake_db_connection}")
    
    # Start a conceptual background task
    # background_task_handle = asyncio.create_task(simulate_background_task())
    # print("LIFESPAN_APP: Background task started.")
    print("LIFESPAN_APP: Application startup complete. Ready to serve requests.")
    yield # This is where the application runs
    # Code here will run AFTER the application has finished handling requests, during shutdown
    print("\nLIFESPAN_APP: Shutdown event triggered!")
    print("LIFESPAN_APP: Cleaning up resources...")
    if background_task_handle and not background_task_handle.done():
        background_task_handle.cancel()
        try:
            await background_task_handle
        except asyncio.CancelledError:
            print("LIFESPAN_APP: Background task cancelled successfully.")
    fake_db_connection = None
    await asyncio.sleep(0.5)
    print("LIFESPAN_APP: Database connection closed. Resources cleaned up.")
    print("LIFESPAN_APP: Application shutdown complete.")

app_lifespan = FastAPI(lifespan=lifespan, title="Lifespan App")

@app_lifespan.get("/")
async def main_route():
    # Access resources initialized during startup (be careful with global state in real apps)
    db_status = fake_db_connection["status"] if fake_db_connection else "disconnected"
    return {"message": "Application is running!", "db_status": db_status}

# To run this app and see lifespan events:
# uvicorn uvicorn_advanced_tutorial.5_programmatic_lifespan:app_lifespan --port 8003
# Or programmatically as shown below.
"""

# For demonstration, let's define the app within this file to run it programmatically.
# In a real project, `app_lifespan` would be in its own file (e.g., `app_with_lifespan.py`)

# Simulate some resources that need setup/teardown for our embedded app
main_fake_db_connection = None
main_background_task_handle = None

async def main_simulate_background_task():
    count = 0
    try:
        while True:
            print(f"PROGRAMMATIC_LIFESPAN_APP: Background task running... (Tick {count})")
            count += 1
            await asyncio.sleep(2) # Shortened for demo
    except asyncio.CancelledError:
        print("PROGRAMMATIC_LIFESPAN_APP: Background task successfully cancelled.")
        raise

@asynccontextmanager
async def main_app_lifespan_handler(app_instance: FastAPI):
    global main_fake_db_connection, main_background_task_handle
    print("PROGRAMMATIC_LIFESPAN_APP: STARTUP event triggered!")
    print("PROGRAMMATIC_LIFESPAN_APP: Initializing resources...")
    await asyncio.sleep(0.5)
    main_fake_db_connection = {"status": "connected", "id": int(time.time())}
    print(f"PROGRAMMATIC_LIFESPAN_APP: Database connection established: {main_fake_db_connection}")
    
    main_background_task_handle = asyncio.create_task(main_simulate_background_task())
    print("PROGRAMMATIC_LIFESPAN_APP: Background task started.")
    app_instance.state.db_connection = main_fake_db_connection # Store on app state
    print("PROGRAMMATIC_LIFESPAN_APP: Application startup complete. Ready to serve requests.")
    yield
    print("\nPROGRAMMATIC_LIFESPAN_APP: SHUTDOWN event triggered!")
    print("PROGRAMMATIC_LIFESPAN_APP: Cleaning up resources...")
    if main_background_task_handle and not main_background_task_handle.done():
        main_background_task_handle.cancel()
        try:
            await main_background_task_handle
        except asyncio.CancelledError:
            pass # Expected
    main_fake_db_connection = None
    del app_instance.state.db_connection
    await asyncio.sleep(0.2)
    print("PROGRAMMATIC_LIFESPAN_APP: Database connection closed. Resources cleaned up.")
    print("PROGRAMMATIC_LIFESPAN_APP: Application shutdown complete.")

# Define the FastAPI app that uses this lifespan handler
app_for_programmatic_run = FastAPI(lifespan=main_app_lifespan_handler)

@app_for_programmatic_run.get("/")
async def programmatic_main_route():
    db_conn = getattr(app_for_programmatic_run.state, "db_connection", None)
    db_status = db_conn["status"] if db_conn else "disconnected"
    return {"message": "Lifespan App (Programmatic) is running!", "db_status": db_status}


async def run_server_with_lifespan():
    config = uvicorn.Config(
        app_for_programmatic_run, # Use the app defined in this file
        host="127.0.0.1",
        port=8004,
        log_level="info"
    )
    server = uvicorn.Server(config)
    print("\nStarting Uvicorn server programmatically to demonstrate lifespan events (port 8004).")
    print("Server will run for ~7 seconds and then shut down to show both startup and shutdown events.")
    print("Make a request to http://127.0.0.1:8004/ during this time.")

    server_task = asyncio.create_task(server.serve())
    await asyncio.sleep(0.2) # Give server a moment to start up fully and print startup messages
    
    # Simulate server running for some time
    await asyncio.sleep(7) 
    
    print("\nPROGRAMMATIC_CONTROL: Signaling server to shut down...")
    server.should_exit = True
    # Allow time for graceful shutdown and lifespan events to complete
    # Wait for the server.serve() task to actually finish
    try:
        await asyncio.wait_for(server_task, timeout=5.0) 
    except asyncio.TimeoutError:
        print("PROGRAMMATIC_CONTROL: Server shutdown timed out.")
    except asyncio.CancelledError: # Should not happen if should_exit is respected
        print("PROGRAMMATIC_CONTROL: Server task was cancelled unexpectedly.")
    print("PROGRAMMATIC_CONTROL: Server has shut down.")


if __name__ == "__main__":
    print(f"To see the lifespan code in action, this script (`{__file__}`) can be run directly.")
    print("It will start a server, demonstrate startup/shutdown lifespan events, and then exit.")
    
    print("\n--- Code for an app with lifespan (`app_with_lifespan.py` content): ---")
    print(f"```python\n{app_with_lifespan_code}\n```")
    print("# You would run the above with: uvicorn path_to_app_with_lifespan:app_lifespan --port 8003")

    # Run the programmatic server example that demonstrates lifespan
    try:
        asyncio.run(run_server_with_lifespan())
    except KeyboardInterrupt:
        print("\nUser interrupted. Exiting.")

print("\n--- Key Takeaways for Programmatic Control & Lifespan ---")
print("- `uvicorn.Config` and `uvicorn.Server` offer fine-grained programmatic control.")
print("- ASGI lifespan protocol (`startup`, `shutdown`) is crucial for managing resources.")
print("- FastAPI uses an `@asynccontextmanager` function passed to `FastAPI(lifespan=...)`.")
print("- Code before `yield` in the lifespan context manager is `startup`.")
print("- Code after `yield` (typically in a `finally` block conceptually) is `shutdown`.")
print("- Ensure cleanup in `shutdown` is robust (e.g., handles tasks that might need cancellation).") 