# 4. Testing FastAPI Applications

# FastAPI provides a `TestClient` (based on `httpx`) to test your application
# without needing to run a live Uvicorn server. This makes testing fast and efficient.

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.testclient import TestClient # Key import for testing
from pydantic import BaseModel
from typing import List, Optional, Annotated

# --- Example Application to be Tested ---
# Let's define a simple application with a few endpoints and Pydantic models.

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    tags: List[str] = []

# In-memory "database" for items
fake_items_db = [
    Item(id=1, name="Foo", description="A foo item", price=10.50, tags=["food"]),
    Item(id=2, name="Bar", description="A bar item", price=20.75, tags=["beverage"]),
    Item(id=3, name="Baz", description="A baz item", price=5.00, tags=["snack", "food"])
]

app = FastAPI(title="Testable Item API")

# Dependency for an API key (simple example)
async def get_api_key(api_key: Optional[str] = Depends(lambda: None)): # Placeholder
    # In a real app, you might use `Header(None, alias="X-API-Key")`
    # For testing, we'll make it easy to override or pass
    if api_key == "testsecretkey":
        return api_key
    # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    # For this example, let's allow no key for some tests and require it for others
    return api_key 

@app.get("/items/", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in fake_items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item, api_key: Annotated[str, Depends(get_api_key)]):
    if api_key != "testsecretkey": # Enforce API key for creation
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API Key for create")
    new_id = max(i.id for i in fake_items_db) + 1 if fake_items_db else 1
    item.id = new_id
    fake_items_db.append(item)
    return item

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: Item, api_key: Annotated[str, Depends(get_api_key)]):
    if api_key != "testsecretkey":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API Key for update")
    for idx, existing_item in enumerate(fake_items_db):
        if existing_item.id == item_id:
            updated_item_data = item_update.model_dump(exclude_unset=True)
            fake_items_db[idx] = Item(**{**existing_item.model_dump(), **updated_item_data, "id": item_id})
            return fake_items_db[idx]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found for update")

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, api_key: Annotated[str, Depends(get_api_key)]):
    if api_key != "testsecretkey":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API Key for delete")
    global fake_items_db
    original_len = len(fake_items_db)
    fake_items_db = [item for item in fake_items_db if item.id != item_id]
    if len(fake_items_db) == original_len:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found for delete")
    return None # FastAPI handles 204 No Content response automatically


# --- Testing with TestClient ---
# The TestClient is used within your test functions.
# You typically instantiate it once per test module or test class.
client = TestClient(app)

# Example Test Cases (usually in a separate test file, e.g., test_main.py)
# For demonstration, they are included here. To run with pytest: `pytest your_file.py`

def test_read_items_no_auth():
    response = client.get("/items/")
    assert response.status_code == 200
    assert len(response.json()) == 3 # Initially 3 items
    assert response.json()[0]["name"] == "Foo"

def test_read_specific_item_success():
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Foo"
    assert data["id"] == 1

def test_read_specific_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_create_item_success():
    new_item_data = {"name": "Qux", "price": 15.00, "tags": ["new", "test"]}
    # Pass API key via headers for a dependency that expects it in a header
    # For our simple Depends(lambda: None) or direct param, we can override or pass directly
    # To simulate a header, you'd do: headers={"X-API-Key": "testsecretkey"}
    # Here, we modify the dependency for create_item to accept it directly if needed
    # or override it.

    # For this example, create_item expects api_key as a query/body param if not header.
    # We'll use headers to show a common way.
    response = client.post("/items/", json=new_item_data, headers={"api-key": "testsecretkey"})
    
    # If the dependency was `api_key: Optional[str] = Header(None, alias="X-API-Key")`
    # response = client.post("/items/", json=new_item_data, headers={"X-API-Key": "testsecretkey"})
    
    # If we wanted to override dependency for testing (more advanced):
    # app.dependency_overrides[get_api_key] = lambda: "testsecretkey"
    # response = client.post("/items/", json=new_item_data)
    # app.dependency_overrides = {} # Clear overrides after test

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Qux"
    assert "id" in data
    assert data["id"] is not None
    # Check if it's in our fake_items_db (it should be, as it's global)
    assert any(item.id == data["id"] and item.name == "Qux" for item in fake_items_db)

def test_create_item_no_api_key():
    new_item_data = {"name": "NoKeyItem", "price": 5.00}
    response = client.post("/items/", json=new_item_data) # No API key header
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API Key for create"}

def test_create_item_wrong_api_key():
    new_item_data = {"name": "WrongKeyItem", "price": 5.00}
    response = client.post("/items/", json=new_item_data, headers={"api-key": "wrongkey"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API Key for create"}

# You would add more tests for update, delete, edge cases, etc.
# For example, a test for updating an item:
def test_update_item_success():
    item_id_to_update = 1
    update_data = {"name": "Updated Foo", "price": 12.99, "description": "An updated foo"}
    response = client.put(f"/items/{item_id_to_update}", json=update_data, headers={"api-key": "testsecretkey"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated Foo"
    assert data["price"] == 12.99
    assert data["id"] == item_id_to_update
    # Verify in db
    updated_db_item = next(item for item in fake_items_db if item.id == item_id_to_update)
    assert updated_db_item.name == "Updated Foo"

def test_delete_item_success():
    # Ensure there's an item to delete (e.g., from create_item or setup)
    # For simplicity, let's assume item with ID 2 exists from initial db
    item_id_to_delete = 2
    response = client.delete(f"/items/{item_id_to_delete}", headers={"api-key": "testsecretkey"})
    assert response.status_code == 204
    # Verify it's gone
    response_get = client.get(f"/items/{item_id_to_delete}")
    assert response_get.status_code == 404
    assert not any(item.id == item_id_to_delete for item in fake_items_db)


# --- Running Tests ---
# To run these tests if they were in a file like `test_main_app.py`:
# 1. Install pytest: `pip install pytest`
# 2. Run from your terminal in the directory of the test file: `pytest`
# Pytest will automatically discover functions prefixed with `test_`.

# You can also use unittest, but TestClient integrates very well with pytest fixtures
# for managing setup/teardown (e.g., initializing a test database).

# --- Overriding Dependencies in Tests ---
# Sometimes you need to override a dependency for testing purposes (e.g., mock an external service).

async def override_get_api_key_always_valid():
    return "mocked_valid_key_for_test"

async def override_get_api_key_always_invalid():
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Mocked Invalid API Key")

def test_create_item_with_dependency_override():
    # Apply the override
    app.dependency_overrides[get_api_key] = override_get_api_key_always_valid
    
    new_item_data = {"name": "OverrideItem", "price": 7.77}
    response = client.post("/items/", json=new_item_data)
    
    assert response.status_code == 201, response.text
    assert response.json()["name"] == "OverrideItem"
    
    # Clean up the override after the test
    app.dependency_overrides = {}
    # or del app.dependency_overrides[get_api_key]

print("--- Testing FastAPI Applications ---")
print("This file demonstrates how to use TestClient for testing FastAPI apps.")
print("Includes example Pydantic models, path operations, and test functions.")
print("To run tests (if in a separate test_*.py file): pip install pytest; pytest")

# If you want to run these specific test functions when executing this file directly:
if __name__ == "__main__":
    print("\nRunning example tests directly (normally use pytest):")
    
    # Reset DB state for each pseudo-run if needed
    initial_db_state = [
        Item(id=1, name="Foo", description="A foo item", price=10.50, tags=["food"]),
        Item(id=2, name="Bar", description="A bar item", price=20.75, tags=["beverage"]),
        Item(id=3, name="Baz", description="A baz item", price=5.00, tags=["snack", "food"])
    ]
    
    print("\nRunning test_read_items_no_auth...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_read_items_no_auth()
    print("test_read_items_no_auth PASSED")

    print("\nRunning test_read_specific_item_success...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_read_specific_item_success()
    print("test_read_specific_item_success PASSED")

    print("\nRunning test_read_specific_item_not_found...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_read_specific_item_not_found()
    print("test_read_specific_item_not_found PASSED")

    print("\nRunning test_create_item_success...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_create_item_success()
    print("test_create_item_success PASSED")

    print("\nRunning test_create_item_no_api_key...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_create_item_no_api_key()
    print("test_create_item_no_api_key PASSED")

    print("\nRunning test_create_item_wrong_api_key...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_create_item_wrong_api_key()
    print("test_create_item_wrong_api_key PASSED")

    print("\nRunning test_update_item_success...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_update_item_success()
    print("test_update_item_success PASSED")

    print("\nRunning test_delete_item_success...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_delete_item_success()
    print("test_delete_item_success PASSED")
    
    print("\nRunning test_create_item_with_dependency_override...")
    fake_items_db = [Item(**i.model_dump()) for i in initial_db_state]
    test_create_item_with_dependency_override()
    print("test_create_item_with_dependency_override PASSED")
    
    print("\nAll direct example tests finished.") 