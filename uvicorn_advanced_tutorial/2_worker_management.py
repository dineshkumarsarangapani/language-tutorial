# 2. Uvicorn: Worker Management & Process Models

# Uvicorn can run multiple worker processes to handle incoming requests concurrently,
# improving performance and resilience. However, its built-in worker management
# is simpler compared to dedicated process managers like Gunicorn.

# We'll use `uvicorn_advanced_tutorial.sample_asgi_app:app` for command-line examples.

print("--- 1. Uvicorn's Built-in Worker Model (`--workers`) ---")
print("Uvicorn can manage multiple worker processes directly using the `--workers` flag.")
print("Each worker runs its own event loop and handles requests independently.")

print("\n# Example: Running Uvicorn with 4 worker processes (run from project root):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8000 --workers 4")
print("  # This will start a master process that manages 4 child worker processes.")
print("  # Requests will be distributed among these workers.")

print("\nConsiderations for Uvicorn's built-in `--workers`:")
print("- Simplicity: Easy to use for development or simple deployments.")
print("- Reloading: When using `--reload` with `--workers > 1`, the master process watches for changes and restarts workers.")
print("- Process Management: Uvicorn's master process handles basic worker lifecycle (spawning, reaping).")
print("- Limitations: For production, Uvicorn recommends using a dedicated process manager like Gunicorn for more advanced features "
      "(e.g., daemonization, sophisticated worker health checks, graceful restarts without dropping connections, security settings).")

# --- 2. Using Gunicorn with Uvicorn Workers (Recommended for Production) ---
# Gunicorn is a mature, feature-rich WSGI HTTP server for Unix. It can also manage ASGI applications
# by using Uvicorn-compatible worker classes.

print("\n\n--- 2. Using Gunicorn with Uvicorn Workers (Production Standard) ---")
print("For production deployments, it's highly recommended to use Gunicorn as a process manager for Uvicorn.")
print("Gunicorn provides robust process management, and Uvicorn provides the high-performance ASGI server capabilities.")

print("\n# Installation (if not already installed):")
print("# pip install gunicorn uvicorn")

print("\n# Example: Running Gunicorn with Uvicorn workers (run from project root):")
print("# gunicorn -w 4 -k uvicorn.workers.UvicornWorker uvicorn_advanced_tutorial.sample_asgi_app:app -b 0.0.0.0:8001")
print("  # -w 4: Specifies 4 worker processes (Gunicorn's syntax for workers).")
print("  # -k uvicorn.workers.UvicornWorker: Tells Gunicorn to use Uvicorn's worker class. This is key.")
print("  # -b 0.0.0.0:8001: Binds to address and port (Gunicorn's syntax).")

print("\n# Using a different Uvicorn worker class (e.g., with uvloop if installed):")
print("# gunicorn -w 4 -k uvicorn.workers.UvicornH11Worker uvicorn_advanced_tutorial.sample_asgi_app:app -b 0.0.0.0:8002")
print("  # `UvicornH11Worker` is an alternative. `UvicornWorker` typically defaults to using httptools if available.")

print("\nBenefits of Gunicorn + Uvicorn:")
print("- Robust Process Management: Gunicorn handles worker spawning, monitoring, restarting, and graceful shutdowns.")
print("- Scalability: Easy to scale the number of worker processes.")
print("- Security: Gunicorn offers options for running as a non-privileged user, setting server names, etc.")
print("- Configuration: Gunicorn has extensive configuration options via command-line or a config file (gunicorn.conf.py).")
print("- Logging: Integrates well with Gunicorn's logging for access and error logs.")
print("- Daemonization: Gunicorn can run the server as a daemon process.")

print("\n# Example Gunicorn configuration file (`gunicorn.conf.py` - create this in your project root):")
gunicorn_conf_example = """
# gunicorn.conf.py (example)

workers = 4  # Number of worker processes
worker_class = 'uvicorn.workers.UvicornWorker'  # The type of worker to use

# Bind to a Unix socket (often used with a reverse proxy like Nginx)
# bind = 'unix:/tmp/gunicorn_sample_app.sock'

# Or bind to a host and port
bind = '0.0.0.0:8003'

# Logging
loglevel = 'info'
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stdout

# You can add many other Gunicorn settings here
# For example, to enable daemon mode (not recommended if using a process supervisor like systemd):
# daemon = True 

# For Uvicorn-specific settings when using Gunicorn, you might need to pass them
# differently, often by customizing the worker or through environment variables
# that Uvicorn itself picks up if not overridden by Gunicorn's management.
"""
print(f"```python\n{gunicorn_conf_example}\n```")
print("# To run Gunicorn with this config file (from project root):")
print("# gunicorn uvicorn_advanced_tutorial.sample_asgi_app:app -c ./gunicorn.conf.py")


# --- 3. Reloading Mechanisms ---
# Uvicorn supports auto-reloading, which is extremely useful during development.

print("\n\n--- 3. Reloading Mechanisms (for Development) ---")

print("\n# Standard Reload (`--reload`):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --reload --port 8005")
print("  # Uvicorn watches for changes in Python files in the current working directory and subdirectories.")
print("  # When a change is detected, the server restarts.")

print("\n# Specifying Reload Directories (`--reload-dir`):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --reload --reload-dir ./uvicorn_advanced_tutorial --reload-dir ./another_project_module --port 8006")
print("  # Use if your project files are outside the standard watch paths or if you want to be more specific.")
print("  # Can be specified multiple times.")

print("\n# `watchfiles` for Reloading (Recommended if installed):")
print("# If `watchfiles` is installed (`pip install watchfiles`), Uvicorn will use it by default for reloading.")
print("# `watchfiles` is generally faster and more reliable than Uvicorn's default `watchgod`.")
print("# No special flag is needed if `watchfiles` is installed; `--reload` will automatically use it.")

print("\n# Reloading with Gunicorn + Uvicorn:")
print("# Gunicorn itself has a `--reload` flag. When used with Uvicorn workers, it will manage the reload process.")
print("# gunicorn -w 2 -k uvicorn.workers.UvicornWorker uvicorn_advanced_tutorial.sample_asgi_app:app --reload -b 0.0.0.0:8007")
print("  # This can be convenient, but ensure your Gunicorn and Uvicorn versions are compatible for smooth reloading.")

print("\n--- Key Takeaways for Worker Management & Reloading ---")
print("- For simple development: `uvicorn --reload` is often sufficient.")
print("- For production: Use Gunicorn with `uvicorn.workers.UvicornWorker` for robust process management.")
print("- `watchfiles` enhances Uvicorn's reloading if installed.")
print("- Understand the difference between Uvicorn's `--workers` and Gunicorn's `-w` for managing worker processes.") 