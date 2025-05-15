# 10. Effective Testing Strategies (unittest, unittest.mock)

# --- Why Test? ---
# Automated tests are crucial for:
# - Ensuring code correctness and reliability.
# - Preventing regressions (re-introducing old bugs).
# - Facilitating refactoring and code changes with confidence.
# - Serving as documentation for how code is intended to be used.

# Python has a built-in `unittest` module for creating tests.
# `pytest` is a popular third-party alternative with a more concise syntax (not covered here).

import unittest
from unittest.mock import Mock, patch, MagicMock # For mocking
import sys

# --- Code to be Tested (Example: A simple calculator) ---
class Calculator:
    def add(self, a, b):
        if not all(isinstance(x, (int, float)) for x in [a, b]):
            raise TypeError("Inputs must be numeric")
        return a + b

    def subtract(self, a, b):
        if not all(isinstance(x, (int, float)) for x in [a, b]):
            raise TypeError("Inputs must be numeric")
        return a - b

    def multiply(self, a, b):
        if not all(isinstance(x, (int, float)) for x in [a, b]):
            raise TypeError("Inputs must be numeric")
        return a * b

    def divide(self, a, b):
        if not all(isinstance(x, (int, float)) for x in [a, b]):
            raise TypeError("Inputs must be numeric")
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

# --- Writing Unit Tests with `unittest` ---
# Test classes must inherit from `unittest.TestCase`.
# Test methods must start with `test_`.

class TestCalculator(unittest.TestCase):
    # setUp is called before each test method
    def setUp(self):
        print("\nSetting up for a Calculator test...")
        self.calculator = Calculator()

    # tearDown is called after each test method
    def tearDown(self):
        print("Tearing down after a Calculator test.")
        # Clean up resources if any were created in setUp
        del self.calculator

    def test_add_integers(self):
        self.assertEqual(self.calculator.add(2, 3), 5, "Should be 5")
        self.assertEqual(self.calculator.add(-1, 1), 0, "Should be 0")

    def test_add_floats(self):
        self.assertAlmostEqual(self.calculator.add(0.1, 0.2), 0.3, places=7, msg="Should be close to 0.3")

    def test_add_invalid_type(self):
        # Test that an exception is raised
        with self.assertRaises(TypeError):
            self.calculator.add(2, "3")
        with self.assertRaisesRegex(TypeError, "Inputs must be numeric"):
            self.calculator.add("two", 3)

    def test_subtract(self):
        self.assertEqual(self.calculator.subtract(5, 2), 3)

    def test_multiply(self):
        self.assertEqual(self.calculator.multiply(3, 4), 12)

    def test_divide(self):
        self.assertEqual(self.calculator.divide(10, 2), 5)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            self.calculator.divide(10, 0)

# --- Mocking with `unittest.mock` ---
# Mocking is used to replace parts of your system (dependencies) with objects 
# that you can control, to isolate the code you are testing.

# Example: A service that uses an external API client
class ApiClient:
    def fetch_data(self, endpoint):
        # In a real scenario, this would make a network request
        print(f"ApiClient: Actually fetching from {endpoint} (should be mocked in tests)")
        if endpoint == "/users":
            return {"data": [{"id": 1, "name": "Test User"}]}
        elif endpoint == "/products":
            return {"data": [{"id": 101, "name": "Gadget"}]}
        raise ConnectionError(f"Failed to fetch {endpoint}")

class MyService:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_user_names(self):
        try:
            response = self.api_client.fetch_data("/users")
            return [user["name"] for user in response["data"]]
        except ConnectionError:
            return [] # Or handle error differently
    
    def get_product_details(self, product_id):
        # Imagine this method needs to make multiple calls or has complex logic
        try:
            product_data = self.api_client.fetch_data(f"/products/{product_id}")
            # ... more processing ...
            return product_data["data"]
        except ConnectionError:
            return None

class TestMyService(unittest.TestCase):
    def setUp(self):
        print("\nSetting up for a MyService test...")
        # Create a mock object for ApiClient
        self.mock_api_client = Mock(spec=ApiClient) # spec ensures mock has same interface
        self.service = MyService(self.mock_api_client)

    def test_get_user_names_success(self):
        # Configure the mock's return value for a specific call
        self.mock_api_client.fetch_data.return_value = {
            "data": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        }
        
        user_names = self.service.get_user_names()
        
        self.assertEqual(user_names, ["Alice", "Bob"])
        # Verify that the mock method was called correctly
        self.mock_api_client.fetch_data.assert_called_once_with("/users")

    def test_get_user_names_api_failure(self):
        # Configure the mock to raise an exception
        self.mock_api_client.fetch_data.side_effect = ConnectionError("API down")
        
        user_names = self.service.get_user_names()
        self.assertEqual(user_names, [])
        self.mock_api_client.fetch_data.assert_called_once_with("/users")

    # Using @patch as a decorator (another way to mock)
    @patch('__main__.ApiClient') # Path to the class to be patched
    def test_get_user_names_with_patch_decorator(self, MockedApiClient): # Patched object is passed as argument
        print("Inside test_get_user_names_with_patch_decorator")
        mock_instance = MockedApiClient.return_value # Get the instance of the mocked ApiClient
        mock_instance.fetch_data.return_value = {"data": [{"id": 3, "name": "Charlie"}]}
        
        # Create service with the (now mocked) ApiClient
        # When MyService is instantiated *inside this test*, it will get the mocked ApiClient
        service_with_patched_client = MyService(ApiClient()) # ApiClient() here will be the mock
        
        user_names = service_with_patched_client.get_user_names()
        self.assertEqual(user_names, ["Charlie"])
        mock_instance.fetch_data.assert_called_once_with("/users")

    def test_get_product_details_magicmock(self):
        # MagicMock is a subclass of Mock with default implementations of most magic methods.
        # Useful if the mocked object is used in ways that trigger magic methods.
        mock_client = MagicMock(spec=ApiClient)
        service = MyService(mock_client)

        # Configure return values for different calls if needed
        def fetch_side_effect(endpoint):
            if endpoint == "/products/101":
                return {"data": {"id": 101, "name": "SuperGadget", "price": 99.99}}
            raise ConnectionError("Product not found")
        
        mock_client.fetch_data.side_effect = fetch_side_effect

        details = service.get_product_details(101)
        self.assertEqual(details, {"id": 101, "name": "SuperGadget", "price": 99.99})
        mock_client.fetch_data.assert_called_once_with("/products/101")

# --- Running Tests ---
# If this script is run directly, `unittest.main()` will discover and run tests.
# python your_script_name.py
# python -m unittest your_script_name.py
# python -m unittest discover (to run all tests in a directory)

# Key Takeaways for Testing:
# - `unittest` module: Provides a test discovery and execution framework.
#   - `TestCase`: Base class for tests.
#   - `assertEqual`, `assertTrue`, `assertRaises`, etc.: Assertion methods.
#   - `setUp` / `tearDown`: For test fixture setup and cleanup.
# - `unittest.mock`: Powerful for creating mock objects.
#   - `Mock`: Basic mock object.
#   - `MagicMock`: Mock with magic methods pre-configured.
#   - `patch`: Temporarily replaces objects in a module with mocks (decorator or context manager).
#   - `return_value`, `side_effect`: Configure mock behavior.
#   - `assert_called_once_with`, `call_count`: Verify mock interactions.
# - Test Isolation: Each test should be independent.
# - Test Coverage: Aim for high coverage but focus on critical paths and business logic.

if __name__ == '__main__':
    print("--- Running Unit Tests ---")
    # You can run tests by calling unittest.main()
    # unittest.main(verbosity=2) # For more detailed output
    
    # To run specific tests or test classes, you can create a TestSuite.
    # suite = unittest.TestSuite()
    # suite.addTest(TestCalculator('test_add_integers'))
    # suite.addTest(unittest.makeSuite(TestMyService))
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)

    # For simplicity, just running all tests found in this file:
    unittest.main(argv=[sys.argv[0], '-v'], exit=False) # -v for verbose, exit=False for script to continue
    print("\n--- Finished Running Unit Tests ---")
    print("Note: Some mock examples print to console to show when real vs. mock is called.") 