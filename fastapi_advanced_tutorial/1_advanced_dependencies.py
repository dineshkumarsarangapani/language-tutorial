# 1. Advanced Dependencies (with `yield`)

from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated # For Depends and newer Python versions
import time

app = FastAPI()

# --- What are Dependencies with `yield`? ---
# FastAPI's dependency injection system is very powerful. For simple dependencies,
# a function can return a value, and that value is injected.
# However, sometimes a dependency needs to perform some setup actions before
# yielding a value, and some teardown actions after the path operation function
# has finished (e.g., closing a database connection, releasing a resource).

# Dependencies with `yield` allow for this setup and teardown pattern.
# The code before `yield` is executed before the response is generated.
# The code after `yield` is executed after the response has been sent.
# This is similar to a context manager.

# --- Example: Simulated Database Connection Pool ---
class DBPool:
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self._active_connections = 0
        print(f"DBPool created with max_connections={max_connections}")

    def get_connection(self):
        if self._active_connections >= self.max_connections:
            print("DBPool: No available connections, waiting...")
            # In a real scenario, this might block or raise an error immediately
            time.sleep(0.5) # Simulate waiting for a connection
            if self._active_connections >= self.max_connections:
                 raise HTTPException(status_code=503, detail="Service Unavailable: No DB connections")
        self._active_connections += 1
        connection_id = f"conn_{self._active_connections}_{int(time.time()*1000)}"
        print(f"DBPool: Connection '{connection_id}' acquired. Active: {self._active_connections}")
        return {"id": connection_id, "status": "connected", "pool": self}

    def release_connection(self, conn_id: str):
        self._active_connections -= 1
        print(f"DBPool: Connection '{conn_id}' released. Active: {self._active_connections}")

# Global DB Pool instance (in a real app, this might be managed differently)
db_pool = DBPool(max_connections=2)

async def get_db_connection():
    """Dependency that provides a database connection and ensures it's released."""
    print("Dependency: Attempting to get DB connection...")
    db_conn = None
    try:
        db_conn = db_pool.get_connection()
        yield db_conn # The yielded value is injected into the path operation
    except HTTPException: # Re-raise HTTP exceptions from the pool
        raise
    except Exception as e:
        print(f"Dependency: Error acquiring DB connection: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: DB issue")
    finally:
        if db_conn:
            print(f"Dependency: Releasing DB connection '{db_conn['id']}'...")
            db_pool.release_connection(db_conn['id'])
        else:
            print("Dependency: No DB connection was acquired, nothing to release.")

# --- Example: Shared Resource / State ---
# This could be a configuration object, a machine learning model, etc.
class SharedResource:
    def __init__(self, name: str):
        self.name = name
        self.load_time = None
        self.access_count = 0
        print(f"SharedResource '{self.name}': Initializing (but not loading yet).")

    def load(self):
        print(f"SharedResource '{self.name}': Loading resource... (simulating delay)")
        time.sleep(0.2)
        self.load_time = time.ctime()
        print(f"SharedResource '{self.name}': Loaded at {self.load_time}.")

    def unload(self):
        print(f"SharedResource '{self.name}': Unloading resource.")
        self.load_time = None # Reset state

    def use(self):
        self.access_count += 1
        return f"Using {self.name}, loaded at {self.load_time}, accessed {self.access_count} times."

# Global shared resource
heavy_resource = SharedResource("ML_Model_A")

async def get_loaded_resource():
    """Dependency that ensures a resource is loaded before use and unloaded after."""
    if heavy_resource.load_time is None: # Load only if not already loaded
        heavy_resource.load()
    try:
        yield heavy_resource # Make the loaded resource available
    finally:
        # Teardown logic: For this example, let's not unload it immediately
        # to show it can persist across requests if desired.
        # In other scenarios, you might want to unload it here.
        print(f"Dependency (get_loaded_resource): Request finished. Resource '{heavy_resource.name}' remains loaded.")
        # heavy_resource.unload() # Uncomment to unload after each request

# --- Path Operations using the dependencies ---
@app.get("/items/{item_id}")
async def read_item(item_id: str, db: Annotated[dict, Depends(get_db_connection)]):
    print(f"Path op /items/{item_id}: Using DB connection '{db['id']}'. Querying item...")
    time.sleep(0.1) # Simulate work
    return {"item_id": item_id, "data": f"Data for {item_id}", "db_connection_status": db["status"]}

@app.get("/users/{user_id}")
async def read_user(user_id: str, db: Annotated[dict, Depends(get_db_connection)]):
    print(f"Path op /users/{user_id}: Using DB connection '{db['id']}'. Querying user...")
    time.sleep(0.15) # Simulate work
    return {"user_id": user_id, "name": f"User {user_id} Name", "db_connection_status": db["status"]}

@app.post("/process")
async def process_data(data_payload: dict, 
                       db: Annotated[dict, Depends(get_db_connection)],
                       resource: Annotated[SharedResource, Depends(get_loaded_resource)]):
    print(f"Path op /process: Using DB connection '{db['id']}'. Processing data...")
    resource_usage_info = resource.use()
    print(f"Path op /process: {resource_usage_info}")
    time.sleep(0.2)
    return {"status": "processed", "payload_received": data_payload, "db_ops_done": True, "resource_info": resource_usage_info}

@app.get("/resource-status")
async def get_resource_status(resource: Annotated[SharedResource, Depends(get_loaded_resource)]):
    return {
        "resource_name": resource.name,
        "loaded_at": resource.load_time,
        "access_count": resource.access_count
    }

# To run this example:
# 1. Save as a Python file (e.g., main.py)
# 2. Run with Uvicorn: `uvicorn main:app --reload`
# 3. Open your browser to http://127.0.0.1:8000/docs
#    - Try calling /items/ and /users/ endpoints, possibly concurrently to see DB pool behavior.
#    - Try /process with some JSON body.
#    - Check /resource-status multiple times.

print("--- Advanced Dependencies with `yield` ---")
print("This FastAPI application demonstrates dependencies that manage resources like DB connections or shared objects.")
print("The code before `yield` in a dependency is for setup, and after `yield` is for teardown.")
print("Run with: uvicorn filename:app --reload (e.g., uvicorn 1_advanced_dependencies:app --reload)") 