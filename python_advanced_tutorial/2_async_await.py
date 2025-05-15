# 2. Asynchronous Programming with `async` and `await`

# --- What is Asynchronous Programming? ---
# Asynchronous programming allows your program to perform multiple tasks seemingly
# at the same time. Instead of waiting for one task to complete before starting
# another (synchronous), it can switch between tasks that are waiting for 
# operations (like I/O: network requests, file operations) to complete.
# This is particularly useful for I/O-bound operations, not CPU-bound ones.

# --- `async` and `await` Keywords ---
# - `async def`: Defines an asynchronous function, also known as a coroutine.
#   Coroutine functions return coroutine objects when called, they don't execute immediately.
# - `await`: Pauses the execution of the current coroutine, allowing the event
#   loop to run other tasks, until the awaited expression (another coroutine or 
#   an awaitable object) completes.
# - Event Loop: The core of asyncio, it manages and distributes the execution of different tasks.

# --- Example: Simulating I/O-bound tasks (like API calls) ---
import asyncio
import time

async def fetch_data(source_name, delay):
    """Simulates fetching data from a source with a delay."""
    print(f"Starting to fetch data from {source_name}...")
    await asyncio.sleep(delay)  # Simulate I/O operation (e.g., network request)
    print(f"Finished fetching data from {source_name}.")
    return f"Data from {source_name}"

async def main_sync_style_call():
    """Demonstrates how it would look if run sequentially (for comparison)."""
    print("--- Synchronous Style (Simulated) ---")
    start_time = time.time()
    
    data1 = await fetch_data("API_1", 2) # Waits for this to complete
    data2 = await fetch_data("API_2", 1) # Then waits for this
    
    end_time = time.time()
    print(f"{data1}")
    print(f"{data2}")
    print(f"Total time (sync style): {end_time - start_time:.2f} seconds\n")

async def main_async_style_call():
    """Demonstrates running tasks concurrently."""
    print("--- Asynchronous Style (Concurrent) ---")
    start_time = time.time()

    # Create tasks to run coroutines concurrently
    # asyncio.create_task() schedules the coroutine to run on the event loop.
    task1 = asyncio.create_task(fetch_data("Source_A", 2))
    task2 = asyncio.create_task(fetch_data("Source_B", 1))

    # await gathers results once both tasks are complete
    # If you await them one by one without create_task, it becomes sequential.
    result1 = await task1
    result2 = await task2
    
    # Alternatively, use asyncio.gather to wait for multiple tasks
    # results = await asyncio.gather(
    #     fetch_data("Source_A", 2),
    #     fetch_data("Source_B", 1)
    # )
    # result1, result2 = results

    end_time = time.time()
    print(f"{result1}")
    print(f"{result2}")
    print(f"Total time (async style): {end_time - start_time:.2f} seconds")
    print("(Note: Total time is close to the longest individual task, not sum of all)")

# To run an asyncio program, you typically use asyncio.run()
if __name__ == "__main__":
    # Running the synchronous-style demonstration (still using async/await for sleep)
    asyncio.run(main_sync_style_call()) 
    
    # Running the asynchronous-style demonstration
    asyncio.run(main_async_style_call())

# --- Key Concepts ---
# - Coroutines (`async def` functions): The building blocks.
# - `await`: Used to pause a coroutine and wait for another awaitable to complete.
# - Event Loop: Manages and executes coroutines.
# - `asyncio.create_task()`: Schedules a coroutine to run soon.
# - `asyncio.gather()`: Runs multiple awaitables concurrently and waits for all to finish.

# --- When to use asyncio? ---
# - I/O-bound tasks: Network requests, database queries, file system operations.
# - High concurrency: When you need to handle many connections or operations simultaneously.

# --- Not for CPU-bound tasks ---
# For CPU-bound tasks (e.g., complex calculations), asyncio doesn't provide a speedup
# because it runs on a single thread. For those, use multiprocessing or threading.

async def another_example():
    print("\\n--- Another Example: asyncio.gather ---")
    start_time = time.time()
    results = await asyncio.gather(
        fetch_data("Server X", 3),
        fetch_data("Server Y", 1),
        fetch_data("Server Z", 2)
    )
    end_time = time.time()
    for r in results:
        print(r)
    print(f"Total time for gather example: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(another_example()) 