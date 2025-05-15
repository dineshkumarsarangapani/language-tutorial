# 1. Uvicorn: Deep Dive into Configuration

# Uvicorn can be configured in several ways, offering flexibility for different
# development and deployment scenarios. We'll use the `sample_asgi_app.py` for these examples.

# Assumed project structure:
# your_project_root/
# |-- uvicorn_advanced_tutorial/
# |   |-- __init__.py (optional, but good practice for imports)
# |   |-- sample_asgi_app.py
# |   |-- 1_advanced_configuration.py
# |   |-- ... (other tutorial files)

# --- 1. Command-Line Interface (CLI) Options ---
# This is the most common way to run Uvicorn during development.

print("--- 1. Command-Line Interface (CLI) Options ---")
print("Uvicorn provides a rich set of CLI options. Run `uvicorn --help` to see all of them.")
print("Example commands (run these in your terminal from the project root):")

print("\n# Basic usage:")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app")

print("\n# Specify host and port:")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --host 0.0.0.0 --port 8001")
print("  # --host 0.0.0.0 makes it accessible on your network, not just localhost.")

print("\n# Enable auto-reload for development (watches for file changes):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --reload --port 8002")

print("\n# Specify reload directories (if default watching isn't catching all changes):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --reload --reload-dir ./uvicorn_advanced_tutorial --port 8003")

print("\n# Change the number of workers (more relevant for production, see Gunicorn topic later):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --workers 4 --port 8004")
print("  # Note: Uvicorn's built-in worker management is basic. For robust multi-process, Gunicorn is often preferred.")

print("\n# Set log level:")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --log-level debug --port 8005")
print("  # Levels: trace, debug, info, warning, error, critical")

print("\n# Specify a Unix domain socket instead of host/port (for inter-process communication on Unix-like systems):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --uds /tmp/uvicorn.sock")

print("\n# Limit maximum concurrent connections (default: no limit):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --limit-concurrency 100 --port 8006")

print("\n# Set server header (default: uvicorn):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --header server:MyCustomServer --port 8007")

print("\n# For a full list, always refer to `uvicorn --help`")


# --- 2. Environment Variables for Configuration ---
# Many CLI options can also be set via environment variables.
# Uvicorn typically prefixes them with `UVICORN_`.
# Example: `--port 8000` becomes `UVICORN_PORT=8000`.
# This is useful for containerized environments or CI/CD pipelines.

print("\n\n--- 2. Environment Variables for Configuration ---")
print("Most CLI options can be set via environment variables, prefixed with `UVICORN_`.")
print("This is useful for Docker, Kubernetes, or CI/CD environments.")

print("\n# Example (run these in your terminal from the project root):")
print("# export UVICORN_PORT=8008")
print("# export UVICORN_LOG_LEVEL=debug")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app")
print("  # Uvicorn will pick up UVICORN_PORT and UVICORN_LOG_LEVEL.")
print("# unset UVICORN_PORT UVICORN_LOG_LEVEL # To clean up env vars after testing")

print("\nKey environment variables include:")
print("- UVICORN_HOST")
print("- UVICORN_PORT")
print("- UVICORN_WORKERS")
print("- UVICORN_LOG_LEVEL")
print("- UVICORN_SSL_KEYFILE, UVICORN_SSL_CERTFILE")
print("- UVICORN_RELOAD (set to `true` or `1`)")
print("Consult Uvicorn documentation for a full list of environment variable mappings.")


# --- 3. Programmatic Uvicorn Server Setup (Running from Python) ---
# You can also run Uvicorn programmatically using `uvicorn.run()` or by creating
# a `uvicorn.Server` instance.

print("\n\n--- 3. Programmatic Uvicorn Server Setup ---")
print("You can start Uvicorn from within your Python code. This offers great flexibility.")

# This part is intended to be run as a Python script.
# To run this specific section: `python 1_advanced_configuration.py` (if __main__ block is added)
# Or, integrate this logic into your application's entry point.

programmatic_example_code = """
import uvicorn
# To run this, you'd typically execute the Python script directly.

# Method 1: Using uvicorn.run() (simple, often used for scripts)
def run_programmatically_simple():
    print("Starting Uvicorn programmatically (simple method) on port 8009...")
    uvicorn.run(
        "uvicorn_advanced_tutorial.sample_asgi_app:app", 
        host="127.0.0.1", 
        port=8009, 
        log_level="info",
        reload=False # Reload doesn't work as effectively in this simple programmatic mode without more setup
    )
    # This call is blocking. Code after it won't run until server stops.

# Method 2: Using uvicorn.Server and uvicorn.Config (more control)
# This method is better if you need to manage the server lifecycle, e.g., in tests or complex setups.
async def run_programmatically_controlled():
    print("Starting Uvicorn programmatically (controlled method) on port 8010...")
    config = uvicorn.Config(
        app="uvicorn_advanced_tutorial.sample_asgi_app:app",
        host="127.0.0.1",
        port=8010,
        log_level="debug",
        # workers=2, # Can specify workers here too
        # You can pass many other parameters here as you would via CLI
    )
    server = uvicorn.Server(config)
    
    # To run this in an asyncio context:
    # await server.serve()
    
    # If not in an async function, you might run it in a separate thread or use server.run()
    # For this example, we'll assume it's called from an async context if you uncomment await server.serve()
    print("Server configured. To run: `await server.serve()` in an async context.")
    print("Or `server.run()` if in a synchronous context (blocking).")
    
    # Example of running it (blocking):
    # server.run() # This would block here.
    
    # For a non-blocking start if you are managing an event loop yourself (advanced):
    # asyncio.create_task(server.serve())
    # print("Server started non-blockingly (conceptual). You'd need an active event loop.")

if __name__ == "__main__":
    print("\nDemonstrating programmatic Uvicorn startup.")
    print("If you run this script, it will attempt to start servers.")
    print("Press Ctrl+C to stop a server if it blocks.")
    
    # print("\n--- Example: uvicorn.run() ---")
    # print("Starting server on http://127.0.0.1:8009 - Press Ctrl+C to stop.")
    # # run_programmatically_simple() # This is blocking, uncomment to run
    # print("Server (simple) would have run here if uncommented.")

    print("\n--- Example: uvicorn.Server and uvicorn.Config ---")
    print("Configuring server for http://127.0.0.1:8010")
    # To actually run the controlled server:
    # import asyncio
    # asyncio.run(run_programmatically_controlled()) # If run_programmatically_controlled is async and calls await server.serve()
    # Or, for a synchronous blocking call:
    # config = uvicorn.Config("uvicorn_advanced_tutorial.sample_asgi_app:app", port=8010, log_level="info")
    # server = uvicorn.Server(config)
    # server.run()
    print("See comments in the code for how to actually run the controlled server example.")
    print("The script itself doesn't block by default to allow the tutorial text to be read.")

"""

print(f"\nPython code for programmatic setup:\n```python\n{programmatic_example_code}\n```")
print("To test the programmatic setup, you would typically save the above Python code snippet")
print("into a .py file (or uncomment parts in this script's __main__ block) and run it directly.")

print("\n--- Key Takeaways for Configuration ---")
print("- CLI: Great for development and simple deployments. Use `uvicorn --help`.")
print("- Environment Variables: Ideal for containerized/CI/CD environments (e.g., `UVICORN_PORT`).")
print("- Programmatic (`uvicorn.run` or `uvicorn.Server`): Provides maximum control for embedding Uvicorn")
print("  within Python applications or for complex startup sequences.") 