# 8. Robust Error Handling and Logging

# --- Custom Exception Hierarchies ---
# Defining your own exception classes makes error handling more specific and your
# code easier to debug and maintain, especially in larger applications.

print("--- Custom Exception Hierarchies ---")

class AppError(Exception):
    """Base class for application-specific errors."""
    pass

class NetworkError(AppError):
    """For errors related to network operations."""
    def __init__(self, message, host, port):
        super().__init__(message)
        self.host = host
        self.port = port

    def __str__(self):
        return f"{super().__str__()} (Host: {self.host}, Port: {self.port})"

class DatabaseError(AppError):
    """For errors related to database operations."""
    def __init__(self, message, query=None):
        super().__init__(message)
        self.query = query

    def __str__(self):
        base_msg = super().__str__()
        return f"{base_msg} (Query: {self.query})" if self.query else base_msg

def simulate_network_operation(fail=False):
    if fail:
        raise NetworkError("Connection timed out", "api.example.com", 443)
    return "Network data received successfully."

def simulate_db_query(fail=False):
    if fail:
        raise DatabaseError("Failed to execute query", query="SELECT * FROM users")
    return "Query executed, 10 rows returned."

try:
    print(simulate_network_operation(fail=False))
    # print(simulate_network_operation(fail=True))
    print(simulate_db_query(fail=False))
    # print(simulate_db_query(fail=True))
except NetworkError as ne:
    print(f"Caught Network Error: {ne}")
except DatabaseError as dbe:
    print(f"Caught Database Error: {dbe}")
except AppError as ae: # Catch any other app-specific error
    print(f"Caught general Application Error: {ae}")
except Exception as e: # Fallback for unexpected errors
    print(f"Caught unexpected error: {e}")

print("\n")

# --- Advanced `logging` Module Usage ---
import logging
import sys # For logging to stdout

print("--- Advanced Logging ---")

# 1. Get a logger instance (best practice: use __name__ for module-level logger)
logger = logging.getLogger(__name__) # e.g., '__main__' if run as script

# 2. Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#    This is the minimum severity level that the logger will handle.
logger.setLevel(logging.DEBUG) # Process all messages from DEBUG upwards

# 3. Create handlers to send log records to destinations
#    - StreamHandler: Sends to streams like sys.stdout, sys.stderr, or any file-like object.
#    - FileHandler: Sends to a disk file.
#    (Others include RotatingFileHandler, TimedRotatingFileHandler, SysLogHandler, etc.)

# Console Handler (for stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO) # This handler will only output INFO and above

# File Handler (for a log file)
# Using a simple file handler for this example. 
# In real apps, RotatingFileHandler or TimedRotatingFileHandler are often better.
try:
    file_handler = logging.FileHandler("app_adv_tutorial.log", mode='w') # 'w' to overwrite on each run for demo
    file_handler.setLevel(logging.DEBUG) # This handler will log DEBUG and above to the file
except PermissionError:
    print("Permission denied to write app_adv_tutorial.log. File logging disabled.")
    file_handler = None

# 4. Create formatters to define the log message format
# Basic format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
# More fields: %(filename)s, %(lineno)d, %(module)s, %(funcName)s
log_format_str = "%(asctime)s [%(levelname)-8s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
formatter = logging.Formatter(log_format_str, datefmt='%Y-%m-%d %H:%M:%S')

# 5. Add formatters to handlers
console_handler.setFormatter(formatter)
if file_handler:
    file_handler.setFormatter(formatter)

# 6. Add handlers to the logger
# A logger can have multiple handlers.
if not logger.handlers: # Avoid adding handlers multiple times if script is re-run in some envs
    logger.addHandler(console_handler)
    if file_handler:
        logger.addHandler(file_handler)

# --- Example logging calls ---
logger.debug("This is a debug message. (Will go to file, not console by default handler config)")
logger.info("Application started successfully. (Goes to file and console)")
logger.warning("A minor issue occurred: User input format incorrect.")
logger.error("A significant error happened: Failed to connect to external service.")

try:
    result = 10 / 0
except ZeroDivisionError:
    logger.critical("Critical error: Division by zero! Application might be unstable.", exc_info=True)
    # exc_info=True automatically adds exception traceback to the log message

# --- Logging from other modules/classes ---
class MyService:
    def __init__(self):
        # It's good practice for libraries/modules to get their own logger
        self.service_logger = logging.getLogger(f"{__name__}.MyService") 
        # Child logger inherits level from parent if not set, but can have own handlers/level
        # self.service_logger.setLevel(logging.DEBUG) # Can set its own level
        # if not self.service_logger.handlers: # Avoid duplicating handlers
        #     self.service_logger.addHandler(console_handler) # Can share handlers or have its own
        #     if file_handler: self.service_logger.addHandler(file_handler)

    def do_something(self):
        self.service_logger.info("MyService is doing something important.")
        self.service_logger.debug("Detailed step within MyService operation.")

service = MyService()
service.do_something()

# Key Takeaways for Error Handling & Logging:
# - Custom Exceptions: Create a clear hierarchy for application-specific errors.
#   Catch specific exceptions before general ones.
# - Logging Module (`logging`):
#   - Loggers: Your entry point (e.g., `logging.getLogger(__name__)`).
#   - Levels: Control message severity (DEBUG, INFO, WARNING, ERROR, CRITICAL).
#   - Handlers: Determine where log messages go (console, file, network, etc.).
#   - Formatters: Define the structure and content of log messages.
#   - Configuration: Can be done via code (as above) or configuration files (for more complex setups).
# - Always log contextual information. Use `exc_info=True` for errors in `try...except` blocks.
# - Avoid using `print()` for logging in libraries and applications; use the `logging` module.

print("\nCheck 'app_adv_tutorial.log' for detailed log output if file logging was enabled.") 