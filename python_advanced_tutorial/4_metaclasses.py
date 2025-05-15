# 4. Metaclasses

# --- What are Metaclasses? ---
# In Python, everything is an object. Classes are objects too. And just like
# objects are instances of classes, classes are instances of metaclasses.
# The default metaclass for most classes is `type`.

# You can create a class by calling `type` directly:
# MyClass = type('MyClass', (MyBaseClass,), {'attribute': value, 'method': some_function})

# Metaclasses allow you to customize the creation of classes. When you define a
# class, its metaclass controls how that class is constructed.

# --- Why use Metaclasses? (Use with caution!) ---
# Metaclasses are powerful but can make code harder to understand if overused.
# They are typically used for:
# 1. Framework development (e.g., ORMs like Django models, API validation).
# 2. Automatically adding methods or attributes to classes.
# 3. Enforcing coding standards or patterns across multiple classes.
# 4. Class registration (e.g., plugin systems).

# --- Simple Metaclass Example: Adding an attribute ---
print("--- Simple Metaclass: Adding an attribute ---")

class MyMeta(type):
    def __new__(mcs, name, bases, dct):
        """
        mcs: The metaclass itself (MyMeta)
        name: The name of the class being created (e.g., 'MyKlass')
        bases: A tuple of base classes
        dct: A dictionary of the class's attributes and methods
        """
        print(f"MyMeta.__new__ called for class: {name}")
        print(f"  Bases: {bases}")
        print(f"  Attributes/methods dict: {dct}")
        
        # Add a new attribute to the class being created
        dct['added_by_meta'] = "This attribute was added by MyMeta!"
        
        # Call the parent metaclass's __new__ method to actually create the class
        return super().__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, dct):
        """
        cls: The class itself that was just created (e.g., MyKlass)
        name, bases, dct: Same as in __new__
        """
        print(f"MyMeta.__init__ called for class: {name}")
        super().__init__(name, bases, dct)

# Now, let's define a class that uses MyMeta as its metaclass
class MyKlass(metaclass=MyMeta):
    existing_attr = 100
    def existing_method(self):
        return "This is an existing method."

# Inspect the created class
print(f"MyKlass.existing_attr: {MyKlass.existing_attr}")
print(f"MyKlass.added_by_meta: {MyKlass.added_by_meta}")

instance = MyKlass()
print(f"Instance method call: {instance.existing_method()}")
print("")

# --- Example: Enforcing a specific method implementation (Conceptual) ---
# This example is more advanced and shows a common use case.
print("--- Metaclass: Enforcing Method Implementation (Conceptual) ---")

class APIEndpointMeta(type):
    def __new__(mcs, name, bases, dct):
        # Check if the class being created has essential API methods
        required_methods = ['get', 'post', 'delete']
        for method_name in required_methods:
            if method_name not in dct or not callable(dct[method_name]):
                # In a real framework, you might raise an error or provide a default
                print(f"Warning: Class '{name}' is missing or has non-callable '{method_name}' method.")
                # For this example, let's add a placeholder if missing
                # dct[method_name] = lambda self, *args, **kwargs: f"Placeholder for {method_name}"
        
        # Add a utility method to all API endpoint classes
        dct['api_version'] = "v1.0"
        
        print(f"APIEndpointMeta creating class: {name}")
        return super().__new__(mcs, name, bases, dct)

class UserAPI(metaclass=APIEndpointMeta):
    def get(self, user_id):
        return f"Fetching user {user_id}"
    
    def post(self, user_data):
        return f"Creating user with data: {user_data}"
    
    # 'delete' method is missing, our metaclass will warn (or could enforce)

class ProductAPI(metaclass=APIEndpointMeta):
    def get(self, product_id):
        return f"Fetching product {product_id}"
    
    # Missing 'post' and 'delete'

user_api = UserAPI()
print(f"UserAPI.get(123): {user_api.get(123)}")
print(f"UserAPI version: {UserAPI.api_version}") # Added by metaclass

product_api = ProductAPI()
print(f"ProductAPI.get(456): {product_api.get(456)}")
print(f"ProductAPI version: {ProductAPI.api_version}")

# Key Takeaways for Metaclasses:
# - They control class creation, not instance creation.
# - `type` is the default metaclass.
# - `__new__` in a metaclass creates the class; `__init__` initializes it.
# - Powerful but complex. Use them when you need to programmatically control
#   class structure or behavior at a large scale or for framework design.
# - Often, decorators or abstract base classes can achieve similar goals with less complexity. 