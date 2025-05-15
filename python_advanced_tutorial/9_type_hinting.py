# 9. Type Hinting (Static Typing with `typing` module)

# --- What is Type Hinting? ---
# Type hinting allows you to specify the expected types of variables, function 
# parameters, and return values. Python itself remains dynamically typed; these 
# hints are not enforced by the interpreter at runtime by default (though some 
# libraries can do runtime type checking).
# Instead, they are primarily for:
# 1. Static Analysis: Tools like MyPy, Pyright, or Pytype can check your code 
#    for type consistency before you run it, catching potential errors early.
# 2. Readability and Maintainability: Type hints make code easier to understand 
#    by clarifying what kind of data functions expect and return.
# 3. Improved IDE Support: Better autocompletion and error detection in code editors.

# --- Basic Type Hinting ---
print("--- Basic Type Hinting ---")

# For variables
user_id: int = 123
user_name: str = "Alice"
is_active: bool = True

# For function parameters and return types
def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

print(greet("Bob"))
print(f"add(5, 3) = {add(5, 3)}")

# If a function doesn't return anything explicitly (returns None implicitly)
def log_message(message: str) -> None:
    print(f"LOG: {message}")

log_message("System initialized.")
print("")

# --- Using the `typing` module for more complex types ---
import typing # Or from typing import List, Dict, Tuple, Union, Optional, Any, Callable, etc.

print("--- Complex Types from `typing` module ---")

# List: A list of integers
ids: typing.List[int] = [1, 2, 3, 4]

# Dict: A dictionary with string keys and integer values
scores: typing.Dict[str, int] = {"math": 90, "science": 85}

# Tuple: A tuple of fixed size and types
coordinates: typing.Tuple[int, int, str] = (10, 20, "origin")

# Union: A value that can be one of several types
item_id: typing.Union[int, str] = "ITEM_XYZ"
item_id = 404 

# Optional: A value that can be of a specific type or None (shorthand for Union[Type, None])
user_email: typing.Optional[str] = None
user_email = "test@example.com"

# Any: When the type can be anything (use sparingly, as it reduces type safety)
flexible_data: typing.Any = "Could be anything" 
flexible_data = [1, 2, {"key": "value"}]

# Callable: For functions or methods
# Callable[[Arg1Type, Arg2Type], ReturnType]
def process_data(data: typing.List[int], callback: typing.Callable[[int], str]) -> typing.List[str]:
    return [callback(x) for x in data]

def format_number(n: int) -> str:
    return f"Number: {n:03d}"

numbers = [7, 12, 5]
formatted_numbers = process_data(numbers, format_number)
print(f"Processed numbers: {formatted_numbers}")

# --- Type Hinting for Classes and Methods ---
print("\n--- Type Hinting for Classes and Methods ---")

class User:
    # Class attributes
    user_count: typing.ClassVar[int] = 0

    def __init__(self, name: str, age: typing.Optional[int] = None) -> None:
        self.name: str = name
        self.age: typing.Optional[int] = age
        User.user_count += 1

    def get_profile(self) -> typing.Dict[str, typing.Any]:
        profile_data: typing.Dict[str, typing.Any] = {"name": self.name}
        if self.age is not None:
            profile_data["age"] = self.age
        return profile_data

    @classmethod
    def get_user_count(cls) -> int:
        return cls.user_count

user_a = User("Charlie")
user_b = User("Diana", 30)

print(f"User A profile: {user_a.get_profile()}")
print(f"User B profile: {user_b.get_profile()}")
print(f"Total users: {User.get_user_count()}")

# --- Generics (e.g., for custom container types) ---
print("\n--- Generics ---")

from typing import TypeVar, Generic

T = TypeVar('T') # Declare a type variable

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: typing.List[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("Cannot pop from an empty stack")
        return self._items.pop()

    def is_empty(self) -> bool:
        return not self._items

# Stack of integers
int_stack = Stack[int]()
int_stack.push(1)
int_stack.push(2)
print(f"Popped from int_stack: {int_stack.pop()}") # MyPy would know this is an int

# Stack of strings
str_stack = Stack[str]()
str_stack.push("hello")
str_stack.push("world")
print(f"Popped from str_stack: {str_stack.pop()}") # MyPy would know this is a str

# --- Benefits Recap ---
# - Early Error Detection: Catch type mismatches before runtime with tools like MyPy.
# - Code Clarity: Makes function signatures and data structures self-documenting.
# - Refactoring Confidence: Easier to refactor code with the assurance of type safety.
# - Better Collaboration: Clear contracts between different parts of a large codebase.

# To run MyPy (install with `pip install mypy`):
# mypy your_script_name.py

print("\nType hints added. Use a static type checker like MyPy to verify.") 