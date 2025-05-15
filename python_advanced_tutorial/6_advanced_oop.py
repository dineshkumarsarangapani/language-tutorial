# 6. Advanced Object-Oriented Programming (OOP)

# This file covers several advanced OOP concepts:
# - Abstract Base Classes (ABCs)
# - Descriptors
# - Mixin Classes

import abc # For Abstract Base Classes

# --- Abstract Base Classes (ABCs) --- 
print("--- Abstract Base Classes (ABCs) ---")

# ABCs define a common interface for a set of subclasses. 
# They can enforce that subclasses implement specific methods.

class MediaLoader(abc.ABC): # Inherit from abc.ABC
    @abc.abstractmethod
    def load(self, source):
        """Load media from a source."""
        pass

    @abc.abstractmethod
    def play(self):
        """Play the loaded media."""
        pass

    def common_utility(self):
        return "This is a common utility in all MediaLoaders."

class ImageLoader(MediaLoader):
    def __init__(self):
        self.image_data = None

    def load(self, filepath):
        print(f"ImageLoader: Loading image from {filepath}")
        self.image_data = f"[Image data from {filepath}]"
        return self.image_data

    def play(self):
        if self.image_data:
            print(f"ImageLoader: Displaying {self.image_data}")
        else:
            print("ImageLoader: No image loaded.")

class VideoLoader(MediaLoader):
    def __init__(self):
        self.video_frames = None

    def load(self, url):
        print(f"VideoLoader: Streaming video from {url}")
        self.video_frames = f"[Video frames from {url}]"
        return self.video_frames

    def play(self):
        if self.video_frames:
            print(f"VideoLoader: Playing {self.video_frames}")
        else:
            print("VideoLoader: No video loaded.")

# Attempting to instantiate an ABC directly will raise an error:
# try:
#     loader = MediaLoader()
# except TypeError as e:
#     print(f"Error: {e}") # Can't instantiate abstract class MediaLoader...

img_loader = ImageLoader()
img_loader.load("my_photo.jpg")
img_loader.play()
print(img_loader.common_utility())

vid_loader = VideoLoader()
vid_loader.load("http://example.com/my_video.mp4")
vid_loader.play()
print("")

# --- Descriptors --- 
print("\n--- Descriptors ---")
# Descriptors allow you to customize attribute access (get, set, delete).
# They are classes that implement `__get__`, `__set__`, or `__delete__` methods.
# Properties are a common use case implemented with descriptors.

class PositiveNumber:
    """A descriptor that ensures a number is positive."""
    def __init__(self, default_value=0):
        self._default = default_value
        self._name = None # Will be set by __set_name__

    def __set_name__(self, owner_class, name):
        # Called when the descriptor is assigned to an attribute in the owner class
        # print(f"__set_name__: owner={owner_class.__name__}, name={name}")
        self._name = name # Store the attribute name (e.g., 'width', 'height')

    def __get__(self, instance, owner_class):
        # instance: The instance of the class using the descriptor (e.g., a Rectangle object)
        # owner_class: The class itself (e.g., Rectangle)
        if instance is None:
            return self # Accessing via class, e.g., Rectangle.width
        # print(f"__get__ for {self._name}: instance has _{self._name} = {instance.__dict__.get(f'_{self._name}', self._default)}")
        return instance.__dict__.get(f'_{self._name}', self._default) # Use mangled name convention

    def __set__(self, instance, value):
        # print(f"__set__ for {self._name}: setting value {value}")
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self._name} must be a number.")
        if value < 0:
            raise ValueError(f"{self._name} must be positive.")
        instance.__dict__[f'_{self._name}'] = value # Store in instance's __dict__

class Rectangle:
    width = PositiveNumber(1)  # width is a PositiveNumber descriptor instance
    height = PositiveNumber(1) # height is also a PositiveNumber descriptor instance

    def __init__(self, width, height):
        self.width = width   # This calls PositiveNumber.__set__ for width
        self.height = height # This calls PositiveNumber.__set__ for height

    def area(self):
        return self.width * self.height # Calls PositiveNumber.__get__

r = Rectangle(10, 20)
print(f"Rectangle r: width={r.width}, height={r.height}, area={r.area()}")

r.width = 15
print(f"Rectangle r: new width={r.width}, area={r.area()}")

try:
    r.height = -5
except ValueError as e:
    print(f"Error setting height: {e}")

try:
    r.width = "not a number"
except TypeError as e:
    print(f"Error setting width: {e}")

# Accessing via class:
# print(f"Rectangle.width descriptor object: {Rectangle.width}") # Returns the descriptor itself


# --- Mixin Classes ---
print("\n--- Mixin Classes ---")
# Mixins are classes that provide methods to other classes through multiple inheritance.
# They are not meant to be instantiated on their own.
# They bundle a specific set of functionalities.

class DebugMixin:
    def print_attributes(self):
        print(f"Attributes of {self.__class__.__name__} (instance {id(self)}):")
        for key, value in self.__dict__.items():
            print(f"  {key}: {value}")

class AsDictMixin:
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class Point(DebugMixin, AsDictMixin):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Config(DebugMixin, AsDictMixin):
    def __init__(self, setting1, setting2, secret_key="dont_show"):
        self.setting1 = setting1
        self.setting2 = setting2
        self._internal_detail = "some internal stuff"
        self.secret_key = secret_key

p = Point(2, 3)
p.print_attributes() # From DebugMixin
print(f"Point as dict: {p.to_dict()}") # From AsDictMixin

conf = Config("value1", True, secret_key="12345")
conf.print_attributes()
print(f"Config as dict: {conf.to_dict()}") # `_internal_detail` and `secret_key` might be filtered based on `to_dict` logic

# Key Takeaways for Advanced OOP:
# - ABCs: Enforce common interfaces and contracts for subclasses (using `abc` module).
# - Descriptors: Customize attribute access; power behind properties, static/class methods.
#   Implement `__get__`, `__set__`, `__delete__`, and `__set_name__`.
# - Mixins: Add reusable functionalities to classes via multiple inheritance without 
#   being part of a strict 'is-a' hierarchy. Good for cross-cutting concerns. 