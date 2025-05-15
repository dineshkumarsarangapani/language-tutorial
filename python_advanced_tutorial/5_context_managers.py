# 5. Context Managers and the `with` statement

# --- What are Context Managers? ---
# Context managers are a way to manage resources (like files, network connections,
# database connections, locks) by ensuring they are properly set up before a block
# of code is executed and properly cleaned up afterwards, even if errors occur.
# The `with` statement is used to invoke context managers.

# --- How they work: `__enter__` and `__exit__` ---
# A class-based context manager implements two special methods:
# - `__enter__(self)`: Called when entering the `with` block. 
#   It sets up the resource and can optionally return an object that will be 
#   assigned to the variable after `as` in the `with` statement.
# - `__exit__(self, exc_type, exc_val, exc_tb)`: Called when exiting the `with` block.
#   It performs cleanup actions. 
#   - `exc_type`, `exc_val`, `exc_tb` provide information about an exception if one occurred.
#   - If `__exit__` returns `True`, it indicates the exception has been handled, 
#     and it won't be propagated. If it returns `False` or `None` (implicitly), 
#     the exception is re-raised.

# --- Example 1: A simple custom context manager for a resource ---
print("--- Example 1: Simple Resource Context Manager ---")

class ManagedResource:
    def __init__(self, name):
        self.name = name
        print(f"Resource '{self.name}': Initializing.")

    def __enter__(self):
        print(f"Resource '{self.name}': Entering context (acquiring). Status: OPEN")
        # You could return self or another specific object here
        return self 

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Resource '{self.name}': Exiting context (releasing). Status: CLOSED")
        if exc_type:
            print(f"  Exception occurred: {exc_type.__name__}: {exc_val}")
            # To suppress the exception, return True. Otherwise, it propagates.
            # return True # Uncomment to suppress ZeroDivisionError
        return False # Default behavior: propagate exception if any

    def use(self):
        print(f"Resource '{self.name}': Being used.")

# Using the context manager
with ManagedResource("MyFile") as res:
    res.use()
    print("Inside the 'with' block.")

print("\n--- Example 1b: With an error inside the 'with' block ---")
try:
    with ManagedResource("MyConnection") as conn:
        conn.use()
        print("Attempting a risky operation...")
        result = 10 / 0 # This will cause a ZeroDivisionError
        print(f"Result: {result}") # This line won't be reached
except ZeroDivisionError as e:
    print(f"Main: Caught expected error: {e}")

print("\nAfter 'with' block (connection should be closed regardless of error).")


# --- Example 2: Using `contextlib.contextmanager` decorator ---
# The `contextlib` module provides a convenient decorator for creating
# context managers from generator functions.

import contextlib

@contextlib.contextmanager
def managed_resource_generator(name):
    print(f"Generator CM '{name}': Initializing & Entering (before yield).")
    # Code before yield is like __enter__
    resource_state = {"status": "acquired"}
    try:
        yield resource_state # The yielded value is what `as` receives
    except Exception as e:
        print(f"Generator CM '{name}': Exception caught: {e}")
        # Handle exception if needed, then re-raise or suppress
        raise # Re-raising the exception by default
    finally:
        # Code after yield (in finally block) is like __exit__
        resource_state["status"] = "released"
        print(f"Generator CM '{name}': Exiting (after yield in finally). Status: {resource_state['status']}")

print("\n--- Example 2: Using @contextlib.contextmanager ---")
with managed_resource_generator("GeneratorResource") as res_state:
    print(f"Inside generator CM. Resource state: {res_state}")
    res_state["data"] = "Sample data"

print("\n--- Example 2b: Generator CM with an error ---")
try:
    with managed_resource_generator("ErrorProneGenerator") as res_state:
        print(f"Inside generator CM. Resource state: {res_state}")
        res_state["data"] = "More data"
        raise ValueError("Something went wrong inside generator CM")
except ValueError as e:
    print(f"Main: Caught expected error from generator CM: {e}")

# --- Why use Context Managers? ---
# 1. Reliability: Guarantees cleanup code runs (like closing files/connections).
# 2. Readability: Makes resource management clear and concise with `with`.
# 3. Error Safety: Properly handles exceptions during resource use and cleanup.

# Common built-in context managers:
# - `open()` for files.
# - `threading.Lock()` for acquiring and releasing locks.
# - `decimal.localcontext()` for managing decimal arithmetic context.

# Key Takeaways:
# - `with` statement simplifies resource management.
# - Implement `__enter__` and `__exit__` for class-based context managers.
# - Use `@contextlib.contextmanager` for simpler generator-based ones.
# - Essential for robust applications dealing with external resources. 