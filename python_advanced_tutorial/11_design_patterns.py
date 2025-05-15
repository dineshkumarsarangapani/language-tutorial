# 11. Design Patterns

# --- What are Design Patterns? ---
# Design patterns are reusable, well-documented solutions to commonly occurring 
# problems within a given context in software design. They are not specific 
# algorithms or code, but rather general concepts or templates for how to structure 
# code to solve a problem efficiently and maintainably.

# We will look at two common patterns: Factory and Singleton.

# --- 1. Factory Pattern --- 
# The Factory pattern provides an interface for creating objects in a superclass, 
# but allows subclasses to alter the type of objects that will be created.
# It's useful when you need to create objects but want to decouple the client code
# from the concrete classes of the objects being created.

print("--- 1. Factory Pattern ---")

# Product Interface (can be an ABC)
class Animal:
    def speak(self) -> str:
        raise NotImplementedError

# Concrete Products
class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

class Duck(Animal):
    def speak(self) -> str:
        return "Quack!"

# Factory Class
class AnimalFactory:
    def create_animal(self, animal_type: str) -> Animal:
        """Creates an animal based on the type string."""
        if animal_type.lower() == "dog":
            return Dog()
        elif animal_type.lower() == "cat":
            return Cat()
        elif animal_type.lower() == "duck":
            return Duck()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# Client code using the factory
factory = AnimalFactory()

animals_to_create = ["dog", "cat", "duck", "dog"]
created_animals = []

for animal_type_str in animals_to_create:
    animal_obj = factory.create_animal(animal_type_str)
    created_animals.append(animal_obj)
    print(f"Created a {animal_type_str}, it says: {animal_obj.speak()}")

try:
    factory.create_animal("lion")
except ValueError as e:
    print(e)

print("\nBenefits of Factory Pattern:")
print("- Decouples client from concrete product classes.")
print("- Easy to add new product types without modifying client code (just update factory).")
print("- Centralizes object creation logic.")
print("")

# --- 2. Singleton Pattern ---
# The Singleton pattern ensures that a class has only one instance and provides a 
# global point of access to that instance.
# Useful for managing shared resources like database connections, configuration managers, etc.

print("\n--- 2. Singleton Pattern ---")

# Method 1: Using a metaclass (more robust for controlling instantiation)
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class DatabaseConnection(metaclass=SingletonMeta):
    def __init__(self, db_url: str):
        # The __init__ will only be called once for the first instantiation
        self.db_url = db_url
        self.connection_id = id(self) # To show it's the same object
        print(f"DatabaseConnection initialized with URL: {self.db_url} (ID: {self.connection_id})")

    def query(self, sql: str):
        return f"Executing query '{sql}' on {self.db_url} (Conn ID: {self.connection_id})"

print("\nSingleton with Metaclass:")
db_conn1 = DatabaseConnection("postgresql://user:pass@host:port/db")
db_conn2 = DatabaseConnection("mysql://another_user@another_host/another_db") # URL ignored after first init

print(f"db_conn1 is db_conn2: {db_conn1 is db_conn2}")
print(f"db_conn1 URL: {db_conn1.db_url}, ID: {db_conn1.connection_id}")
print(f"db_conn2 URL: {db_conn2.db_url}, ID: {db_conn2.connection_id}") # Will show the first URL
print(db_conn1.query("SELECT * FROM users"))
print(db_conn2.query("SELECT * FROM products"))


# Method 2: Using a decorator (simpler for some cases)
# (Note: this decorator version doesn't prevent re-calling __init__ if instance already exists,
#  which might be undesirable. The metaclass approach is often more complete.)
def singleton_decorator(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton_decorator
class AppConfiguration:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self.settings = {} # Load settings from file
        print(f"AppConfiguration initialized with file: {self.config_file_path}")
        # Simulating loading settings
        self.settings["theme"] = "dark"
        self.settings["language"] = "en"

    def get_setting(self, key: str):
        return self.settings.get(key)

print("\nSingleton with Decorator:")
config1 = AppConfiguration("settings.json")
config2 = AppConfiguration("other_settings.yaml") # Path ignored after first init

print(f"config1 is config2: {config1 is config2}")
print(f"config1 file: {config1.config_file_path}")
print(f"config2 file: {config2.config_file_path}")
print(f"Theme from config1: {config1.get_setting('theme')}")
config1.settings["font_size"] = 12 # Modifying one instance affects the other
print(f"Font size from config2: {config2.get_setting('font_size')}")


# --- Using Singleton with Dependency Injection for Testability ---
print("\n--- Singleton with Dependency Injection for Testability ---")

class UserService:
    def __init__(self, config: AppConfiguration):
        self.config = config
        self.user_language = self.config.get_setting("language")

    def get_user_preferences_summary(self) -> str:
        theme = self.config.get_setting("theme")
        return f"User prefers {self.user_language} language and {theme} theme."

# Normal usage:
config_instance = AppConfiguration("main_settings.ini") # Singleton ensures it's the same instance
user_service = UserService(config=config_instance)
print(user_service.get_user_preferences_summary())

# Testing UserService with a mocked configuration:
class MockAppConfig:
    def __init__(self, lang, theme_val):
        self.mock_settings = {"language": lang, "theme": theme_val}
        print(f"MockAppConfig initialized for testing with lang='{lang}', theme='{theme_val}'")

    def get_setting(self, key: str):
        return self.mock_settings.get(key)

print("\nTesting UserService with a mock configuration:")
mock_config_for_test = MockAppConfig(lang="fr", theme_val="light")
testable_user_service = UserService(config=mock_config_for_test)
print(testable_user_service.get_user_preferences_summary()) # Will use mocked values


print("\nConsiderations for Singleton:")
print("- Global state can make testing harder (use dependency injection where possible).")
print("- Can violate Single Responsibility Principle if the singleton does too much.")
print("- Be careful with thread safety if the singleton is accessed by multiple threads.")

# Key Takeaways for Design Patterns:
# - They are established solutions to common software design problems.
# - Factory Pattern: Decouples object creation from client code.
# - Singleton Pattern: Ensures a class has only one instance and a global access point.
# - Many other patterns exist (Observer, Strategy, Decorator (covered earlier!), Adapter, etc.).
# - Understanding patterns helps in designing flexible, maintainable, and scalable systems. 