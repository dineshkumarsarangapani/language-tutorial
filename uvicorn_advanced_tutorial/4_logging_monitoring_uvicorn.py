# 4. Uvicorn: Logging and Monitoring

# Uvicorn provides logging for access requests and server errors. Understanding and
# configuring this logging is important for monitoring and debugging your ASGI application.

# We'll use `uvicorn_advanced_tutorial.sample_asgi_app:app` for command-line examples.

print("--- 1. Uvicorn's Default Logging ---")
print("By default, Uvicorn logs access messages to stdout and errors to stderr.")
print("The default access log format is a common standard, showing client IP, request line, status code, etc.")

print("\n# Example: Run with default logging (run from project root):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8000")
print("  # Make some requests to http://127.0.0.1:8000/ and http://127.0.0.1:8000/info")
print("  # Observe the access logs in your terminal.")

print("\n--- 2. Configuring Log Levels ---")
print("You can control the verbosity of Uvicorn's own logs using `--log-level`.")
print("This affects Uvicorn's server messages, not necessarily your application's internal logging (unless your app also uses the root logger configured by Uvicorn).")

print("\n# Log levels (from most verbose to least):")
print("- `trace`: Extremely detailed, including raw socket data (use with caution).")
print("- `debug`: Detailed information, useful for debugging Uvicorn internals or request flow.")
print("- `info`: Default. General operational information, access logs.")
print("- `warning`: Warnings about potential issues.")
print("- `error`: Errors that occurred during request processing or server operation.")
print("- `critical`: Severe errors causing the server to potentially stop.")

print("\n# Example: Running with debug log level:")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8001 --log-level debug")

print("\n# Example: Running with warning log level (less verbose access logs):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8002 --log-level warning")
print("  # Note: With `--log-level warning` or higher, standard access logs (INFO level) might not appear.")
print("  # To suppress access logs entirely, you can use `--no-access-log` (see below).")

print("\n--- 3. Customizing Access Log Format ---")
print("Uvicorn allows some customization of the access log format, although it's not as flexible as, say, Gunicorn's or Nginx's.")
print("Uvicorn primarily uses Python's standard `logging` module.")
print("If you need highly custom log formats, you might consider:")
print("  a) Using middleware in your ASGI application to log requests in your desired format.")
print("  b) When using Gunicorn with Uvicorn workers, leverage Gunicorn's access log formatting capabilities.")

print("\nUvicorn does respect some log configuration if you set it up programmatically or via a log config file loaded by your app or Uvicorn.")
print("However, direct CLI flags for arbitrary access log format strings are limited.")

print("\n# Disabling Access Logs:")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8003 --no-access-log")
print("  # This completely disables the default INFO level access logging.")

print("\n--- 4. Application Logging vs. Uvicorn Logging ---")
print("It's important to distinguish between Uvicorn's server logs and your application's own internal logging.")
print("- Uvicorn's logs: Primarily about server operations, request handling lifecycle, and errors at the server level.")
print("- Application logs: Messages logged from your FastAPI/Starlette/Django code using Python's `logging` module.")

print("\nBy default, Uvicorn configures the root Python logger. If your application also uses the root logger or loggers that propagate to root, " \
      "their output might be affected by Uvicorn's `--log-level` and will appear in Uvicorn's stream.")

print("\n# To have separate control, configure specific loggers for your application distinct from the root logger.")
print("  (Refer to the `8_error_handling_logging.py` in `python_advanced_tutorial` for general Python logging setup).")

print("\n# Using `--log-config <path_to_logging_config.ini_or.json_or.yaml>`:")
print("Uvicorn can load a Python logging configuration file. This gives you full control over loggers, handlers, and formatters.")

example_log_config_ini = """
; example_uvicorn_log_config.ini
[loggers]
keys=root,uvicorn.error,uvicorn.access,myapp

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter,accessFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_uvicorn.error]
level=INFO
handlers=consoleHandler
qualname=uvicorn.error
propagate=0

[logger_uvicorn.access]
level=INFO
handlers=consoleHandler
qualname=uvicorn.access
propagate=0

[logger_myapp] ; Your application's logger
level=DEBUG
handlers=consoleHandler
qualname=myapp ; Assuming your app uses logging.getLogger('myapp')
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S

[formatter_accessFormatter] ; Example for a custom access log, though uvicorn.access might not use it directly without code changes
format=%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s
"""
print(f"\n# Example `example_uvicorn_log_config.ini` (save this to a file):\n```ini\n{example_log_config_ini}\n```")
print("# Then run Uvicorn (from project root):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8004 --log-config ./example_uvicorn_log_config.ini")
print("  # Note: You might need to `import sys` in the .ini for `args=(sys.stdout,)` or use `ext://sys.stdout` depending on Python version.")

print("\n--- 5. Error Logging ---")
print("Uvicorn logs server errors and unhandled exceptions from your application to stderr by default.")
print("- `uvicorn.error` logger is used for these.")
print("- If an exception propagates from your ASGI app and isn't caught, Uvicorn will typically log it and return a 500 Internal Server Error.")
print("- The detail of the traceback in logs can be influenced by `--log-level`.")

print("\n--- 6. Logging when using Gunicorn ---")
print("When using Gunicorn with Uvicorn workers (`-k uvicorn.workers.UvicornWorker`):")
print("- Gunicorn takes over the primary responsibility for access and error logging based on its own configuration (`--access-logfile`, `--error-logfile`, `loglevel` in Gunicorn config).")
print("- Uvicorn's specific loggers (`uvicorn.error`, `uvicorn.access`) might still emit logs, which Gunicorn can capture.")
print("- Generally, you'd configure logging at the Gunicorn level for a unified setup.")

print("\n--- Key Takeaways for Logging & Monitoring with Uvicorn ---")
print("- `--log-level` controls Uvicorn's verbosity.")
print("- `--no-access-log` disables standard access logs.")
print("- `--log-config` provides fine-grained control using a Python logging configuration file.")
print("- Distinguish between Uvicorn's server logs and your application's logs.")
print("- For production with Gunicorn, configure logging primarily through Gunicorn.") 