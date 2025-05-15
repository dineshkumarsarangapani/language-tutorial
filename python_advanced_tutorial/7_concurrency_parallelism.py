# 7. Concurrency and Parallelism (threading, multiprocessing, concurrent.futures)

# --- Introduction ---
# Python offers several ways to run code concurrently (appearing to do multiple 
# things at once) or in parallel (actually doing multiple things at once using 
# multiple CPU cores).

# - Concurrency: Achieved using threads (`threading`) or asynchronous programming (`asyncio`).
#   Useful for I/O-bound tasks where the program spends time waiting for external operations.
#   Due to Python's Global Interpreter Lock (GIL), threads in CPython don't achieve 
#   true parallelism for CPU-bound tasks.
# - Parallelism: Achieved using multiple processes (`multiprocessing`). 
#   Each process has its own Python interpreter and memory space, bypassing the GIL.
#   Ideal for CPU-bound tasks that can be broken down into independent sub-tasks.

# `concurrent.futures` provides a high-level interface for both.

import threading
import multiprocessing
import concurrent.futures
import time
import os

# --- Helper functions for demonstration ---
def io_bound_task(name, duration):
    print(f"Task '{name}' (I/O-bound): Starting on process {os.getpid()}, thread {threading.get_ident()}")
    time.sleep(duration) # Simulate I/O wait (e.g., network request, disk read/write)
    result = f"Task '{name}' completed after {duration}s"
    print(result)
    return result

def cpu_bound_task(name, count_to):
    print(f"Task '{name}' (CPU-bound): Starting on process {os.getpid()}, thread {threading.get_ident()}")
    start_time = time.time()
    c = 0
    for i in range(count_to):
        c += 1 # Simple CPU work
    duration = time.time() - start_time
    result = f"Task '{name}' counted to {count_to} in {duration:.4f}s. Final count: {c}"
    print(result)
    return result 

# --- 1. `threading` for I/O-bound tasks ---
print("--- 1. `threading` for I/O-bound tasks ---")

def run_with_threading():
    start_total_time = time.perf_counter()
    threads = []
    tasks_data = [("A-IO", 2), ("B-IO", 1)]

    for name, duration in tasks_data:
        thread = threading.Thread(target=io_bound_task, args=(name, duration))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join() # Wait for each thread to complete

    end_total_time = time.perf_counter()
    print(f"Threading Total Time: {end_total_time - start_total_time:.4f}s (should be close to max task duration)")

run_with_threading()
print("\n")

# --- 2. `multiprocessing` for CPU-bound tasks ---
print("--- 2. `multiprocessing` for CPU-bound tasks ---")

def run_with_multiprocessing():
    # Important: On some platforms (like Windows), multiprocessing code that spawns 
    # new processes must be within a `if __name__ == "__main__":` block.
    start_total_time = time.perf_counter()
    processes = []
    # Use smaller numbers for CPU bound tasks in examples to keep them quick
    tasks_data = [("X-CPU", 25_000_000), ("Y-CPU", 30_000_000)] 

    for name, count in tasks_data:
        process = multiprocessing.Process(target=cpu_bound_task, args=(name, count))
        processes.append(process)
        process.start()

    for process in processes:
        process.join() # Wait for each process to complete

    end_total_time = time.perf_counter()
    # If you have multiple cores, this should be faster than sequential execution.
    print(f"Multiprocessing Total Time: {end_total_time - start_total_time:.4f}s")

# We need the __main__ guard for multiprocessing on some OSes
if __name__ == "__main__": # This is crucial for multiprocessing
    run_with_multiprocessing()
    print("\n")


# --- 3. `concurrent.futures` (High-level interface) ---
print("--- 3. `concurrent.futures` ---")

# 3a. ThreadPoolExecutor for I/O-bound tasks
print("\n--- 3a. `concurrent.futures.ThreadPoolExecutor` (I/O-bound) ---")
def run_with_threadpoolexecutor():
    start_total_time = time.perf_counter()
    tasks_data = [("Alpha-IO", 2), ("Beta-IO", 1), ("Gamma-IO", 3)]
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # `submit` schedules a callable to be executed and returns a Future object
        future_to_task = {executor.submit(io_bound_task, name, duration): name for name, duration in tasks_data}
        
        for future in concurrent.futures.as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                data = future.result() # Blocks until the future is complete, gets return value
                results.append(data)
            except Exception as exc:
                print(f"Task '{task_name}' generated an exception: {exc}")
            else:
                print(f"Task '{task_name}' result retrieved.")
                
    end_total_time = time.perf_counter()
    print(f"ThreadPoolExecutor Total Time: {end_total_time - start_total_time:.4f}s")
    # print(f"Results from ThreadPoolExecutor: {results}")

run_with_threadpoolexecutor()
print("\n")

# 3b. ProcessPoolExecutor for CPU-bound tasks
if __name__ == "__main__": # Crucial for ProcessPoolExecutor as well
    print("\n--- 3b. `concurrent.futures.ProcessPoolExecutor` (CPU-bound) ---")
    def run_with_processpoolexecutor():
        start_total_time = time.perf_counter()
        tasks_data = [("P-CPU", 20_000_000), ("Q-CPU", 25_000_000), ("R-CPU", 15_000_000)]
        results = []
        
        # max_workers defaults to number of processors on the machine
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Using map for simplicity if you don't need individual Future objects immediately
            # map returns results in the order tasks were submitted
            # Note: cpu_bound_task needs to be picklable for multiprocessing, which it is.
            # For map, we need a way to pass multiple arguments. We can use functools.partial or a wrapper.
            # Or, structure tasks_data as [(cpu_bound_task, "P-CPU", 20_000_000), ...]
            # and use executor.map(lambda p: p[0](p[1], p[2]), tasks_args)
            
            # Using submit for consistency with ThreadPoolExecutor example
            future_to_task = {executor.submit(cpu_bound_task, name, count): name for name, count in tasks_data}

            for future in concurrent.futures.as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    print(f"Task '{task_name}' (in process pool) generated an exception: {exc}")
                else:
                    print(f"Task '{task_name}' (in process pool) result retrieved.")

        end_total_time = time.perf_counter()
        print(f"ProcessPoolExecutor Total Time: {end_total_time - start_total_time:.4f}s")
        # print(f"Results from ProcessPoolExecutor: {results}")

    run_with_processpoolexecutor()
    print("\n")

# --- Key Takeaways ---
# - `threading`: For I/O-bound concurrency within a single process. Limited by GIL for CPU tasks.
# - `multiprocessing`: For CPU-bound parallelism by using multiple processes, bypassing GIL.
#   Processes have more overhead (memory, inter-process communication if needed).
# - `concurrent.futures`: High-level API (ThreadPoolExecutor, ProcessPoolExecutor) for managing 
#   thread and process pools. Often preferred for its simplicity and flexibility.
# - GIL (Global Interpreter Lock): A mutex that protects access to Python objects, preventing
#   multiple native threads from executing Python bytecodes at once in CPython.
# - Always consider if your task is I/O-bound or CPU-bound to choose the right tool.
# - `if __name__ == "__main__":` is critical for multiprocessing code on platforms like Windows
#   to prevent issues when new processes are spawned.

print("Script finished. If multiprocessing examples didn't run, execute the file directly.") 