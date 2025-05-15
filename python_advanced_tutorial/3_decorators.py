# 3. Decorators (as Interceptors)

# --- What are Decorators? ---
# Decorators are a very powerful and expressive feature in Python.
# A decorator is a function that takes another function (or method) as an argument,
# adds some functionality to it, and then returns the modified function or a new one.
# They provide a way to wrap additional logic around an existing function without
# explicitly changing its core behavior. This is a form of metaprogramming.

# --- Basic Decorator Structure ---
import functools
import time

def my_decorator_function(original_function):
    # This is the decorator
    @functools.wraps(original_function) # Preserves original function's metadata
    def wrapper_function(*args, **kwargs):
        print(f"Wrapper executed before {original_function.__name__}()")
        result = original_function(*args, **kwargs) # Call the original function
        print(f"Wrapper executed after {original_function.__name__}()")
        return result
    return wrapper_function

# --- Applying a decorator ---
@my_decorator_function
def say_hello(name):
    """A simple function to greet someone."""
    print(f"Hello, {name}!")
    return f"Greeting for {name} complete."

print("--- Basic Decorator Example ---")
returned_value = say_hello("Alice")
print(f"Returned value from decorated function: {returned_value}")
print(f"Original function name (preserved by functools.wraps): {say_hello.__name__}")
print(f"Original docstring (preserved): {say_hello.__doc__}\n")

# The above @my_decorator_function is syntactic sugar for:
# def say_hello_original(name):
#     print(f"Hello, {name}!")
# say_hello = my_decorator_function(say_hello_original)

# --- Practical Example: Timing a function's execution ---
def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"Function '{func.__name__}' took {end_time - start_time:.4f} seconds to execute.")
        return result
    return wrapper

@timing_decorator
def slow_function(delay):
    """A function that simulates some work by sleeping."""
    time.sleep(delay)
    print("Slow function finished.")
    return "Work done"

print("--- Timing Decorator Example ---")
slow_function(1)
print("")

# --- Decorators with Arguments ---
# Sometimes you want to pass arguments to the decorator itself.
# This requires an extra layer of nesting.

def repeat_decorator(num_times):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(num_times):
                result = func(*args, **kwargs)
                results.append(result)
            return results
        return wrapper
    return actual_decorator

@repeat_decorator(num_times=3)
def greet(name):
    message = f"Hi, {name}!"
    print(message)
    return message

print("--- Decorator with Arguments Example ---")
greeting_results = greet("Bob")
print(f"Results from repeated greet: {greeting_results}\n")

# --- Class-based Decorators ---
# Decorators can also be implemented as classes.
class CountCallsDecorator:
    def __init__(self, func):
        functools.update_wrapper(self, func) # Preserves metadata
        self.func = func
        self.num_calls = 0

    def __call__(self, *args, **kwargs):
        self.num_calls += 1
        print(f"Call {self.num_calls} of {self.func.__name__}()")
        return self.func(*args, **kwargs)

@CountCallsDecorator
def say_whee():
    print("Whee!")

print("--- Class-based Decorator Example ---")
say_whee()
say_whee()
say_whee()

# --- Why use Decorators (as Interceptors)? ---
# 1. Code Reusability: Add common functionality (logging, timing, auth checks) to multiple functions.
# 2. Readability: Keeps the core function logic clean, separating cross-cutting concerns.
# 3. Extensibility: Modify behavior without changing the original function's code.
#    This aligns with the Open/Closed Principle (open for extension, closed for modification).

# --- `functools.wraps` ---
# It's crucial to use `functools.wraps` when writing decorators.
# It copies metadata (like the function name, docstring, and argument list)
# from the original function to your wrapper function. Without it, the
# decorated function would lose its original identity, which can be problematic
# for debugging and introspection. 