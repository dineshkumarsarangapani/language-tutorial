// 2. The Node.js Event Loop, Non-Blocking I/O & Concurrency Model

// For this file to type-check correctly, especially for Node.js specific globals
// like `process`, `Buffer`, `__filename`, `setImmediate`, and for module imports,
// you would typically need Node.js type definitions in your project:
// npm install --save-dev @types/node

import * as fs from 'node:fs'; // Modern way to import built-in Node.js modules

// Understanding the Node.js event loop is crucial for writing efficient and scalable applications.
// Node.js uses a single-threaded event loop to handle concurrency for I/O-bound operations,
// which allows it to manage many connections simultaneously without creating many OS threads.

console.log("--- Understanding the Node.js Event Loop & Non-Blocking I/O ---");

// --- Key Concepts ---
// 1. Single Thread: Your JavaScript/TypeScript code runs in a single main thread.
//    This simplifies programming as you don't usually have to worry about thread safety for your own code.
// 2. Event Loop: An constantly running process that takes tasks from a queue and executes them.
//    It allows Node.js to perform non-blocking I/O operations.
// 3. Non-Blocking I/O: When Node.js encounters an I/O operation (e.g., reading a file, making an HTTP request),
//    it doesn't wait for the operation to complete. Instead, it offloads the operation to the system's kernel
//    (often via libuv) and continues to execute other code. When the I/O operation finishes, a callback,
//    Promise, or async function resumption is added to the event queue to be processed.
// 4. Libuv: A C library that provides the event loop and asynchronous I/O capabilities to Node.js.
//    It handles tasks like network requests, file system operations, and child processes by using
//    OS-level asynchronous mechanisms and a thread pool for operations that don't have a native
//    non-blocking equivalent on all platforms.
// 5. Worker Threads (libuv thread pool): For some operations that are inherently blocking or CPU-intensive
//    at the OS level (like certain file system operations, DNS lookups, or custom C++ addons),
//    libuv maintains a small pool of worker threads. These are *not* the main Node.js thread where your JS runs.
//    Your JS code still interacts with these via non-blocking APIs.

console.log("\n--- Phases of the Event Loop (Simplified) ---");
// The event loop has several phases. Each phase has its own FIFO queue of callbacks to execute.
// When the event loop enters a given phase, it will perform any operations specific to that phase
// and then execute callbacks in that phase's queue until the queue has been exhausted or the
// maximum number of callbacks has executed.

// 1. Timers (`setTimeout`, `setInterval`):
//    - Executes callbacks scheduled by `setTimeout()` and `setInterval()` whose timers have elapsed.
console.log("TIMER_PHASE: Callbacks for expired timers are processed here.");

// 2. Pending Callbacks (I/O Callbacks / Poll Phase related):
//    - Executes I/O callbacks deferred to the next loop iteration (e.g., some TCP errors).
//    - More importantly, this is related to the **Poll phase**.
console.log("PENDING_CALLBACKS_PHASE: Some system-level I/O callbacks.");

// 3. Idle, Prepare (Internal):
//    - Only used internally by Node.js.
console.log("IDLE_PREPARE_PHASE: Internal Node.js usage.");

// 4. Poll Phase (Most I/O related callbacks):
//    - This is where most of the action happens for I/O.
//    - It retrieves new I/O events and executes I/O-related callbacks (e.g., from file reads, network requests).
//    - If the poll queue is empty, Node.js will block here for a short time waiting for new I/O events.
//    - If there are `setImmediate()` callbacks scheduled, it will end the poll phase and go to the check phase.
//    - If there are timers whose thresholds have been reached, it will also wrap back to the timers phase.
console.log("POLL_PHASE: Retrieve new I/O events; execute I/O-related callbacks.");

// 5. Check Phase (`setImmediate`):
//    - Executes callbacks scheduled by `setImmediate()`.
//    - `setImmediate()` is designed to execute a script once the current poll phase has completed.
console.log("CHECK_PHASE: Callbacks scheduled by setImmediate() are processed here.");

// 6. Close Callbacks Phase (`close` events):
//    - Executes callbacks for `close` events (e.g., `socket.on('close', ...)`).
console.log("CLOSE_CALLBACKS_PHASE: Callbacks for 'close' events (e.g., socket closed).");

// `process.nextTick()` and Promises (`.then`, `.catch`, `await`):
// - These are *not* part of the event loop phases directly.
// - `process.nextTick()` callbacks are processed *after* the current operation completes, regardless of the
//   current phase of the event loop. They run before any I/O or timers are fired.
// - Promise callbacks (microtasks) are also processed very quickly after the current operation, typically
//   before `setImmediate` but after `nextTick` if both are queued in the same scope.

console.log("\n--- Example: Observing Event Loop Order (Conceptual) ---");

// This example uses setTimeout, setImmediate, and process.nextTick to show potential order.
// The exact order can sometimes be subtle due to system load or timer granularity.

// To run this specific block, you can copy it into a separate .ts file and execute.
const eventLoopOrderExample = () => {
    console.log("\nEVENT_LOOP_DEMO: Script Start");

    // File I/O (will go to Poll phase queue after libuv finishes)
    // const fs = require('fs'); // Old way
    fs.readFile(__filename, (err: Error | null, data: Buffer) => {
        if (err) console.error("fs.readFile Error:", err);
        console.log("EVENT_LOOP_DEMO: fs.readFile (I/O) callback - Poll Phase");
    });

    setTimeout(() => {
        console.log("EVENT_LOOP_DEMO: setTimeout callback (min delay) - Timers Phase");
    }, 0); // 0ms delay doesn't mean immediate, means "as soon as possible in timers phase"

    setImmediate(() => {
        console.log("EVENT_LOOP_DEMO: setImmediate callback - Check Phase");
    });

    process.nextTick(() => {
        console.log("EVENT_LOOP_DEMO: process.nextTick callback 1 (executes ASAP)");
    });

    Promise.resolve().then(() => {
        console.log("EVENT_LOOP_DEMO: Promise.resolve().then() callback (microtask, executes ASAP)");
    });
    
    process.nextTick(() => {
        console.log("EVENT_LOOP_DEMO: process.nextTick callback 2 (executes ASAP)");
    });

    console.log("EVENT_LOOP_DEMO: Script End (synchronous part done)");
    // Expected rough order (nextTick and Promise are high priority):
    // Script Start
    // Script End
    // process.nextTick callback 1
    // process.nextTick callback 2
    // Promise.resolve().then() callback
    // setTimeout callback (min delay) OR fs.readFile (if file is cached & read extremely fast)
    // setImmediate callback
    // fs.readFile (I/O) callback OR setTimeout callback (depending on I/O speed and timer setup)
};

// eventLoopOrderExample(); // Uncomment to run this example in isolation
console.log("To see eventLoopOrderExample in action, uncomment the call and run the compiled JS file.");


console.log("\n--- Implications for Writing Code ---");
console.log("- **Don't Block the Event Loop:** CPU-intensive tasks in your main JavaScript thread will block the event loop, " +
  "preventing Node.js from handling other requests or I/O. This makes the server unresponsive. " +
  "For CPU-bound work: use Worker Threads (Node.js module), child processes, or offload to a separate service.");
console.log("- **Embrace Asynchronicity:** Use async patterns (callbacks, Promises, async/await) for all I/O operations.");
console.log("- **Understand Callback Queues:** Knowing the different queues (timers, I/O, immediate, close) and microtask queues " +
  "(nextTick, Promises) helps in debugging and understanding the execution order of complex async code.");
console.log("- **Error Handling:** Proper error handling in asynchronous code is vital to prevent crashes and ensure stability.");

// --- Concurrency Model ---
// Node.js achieves concurrency (handling multiple things at once) through its event-driven, non-blocking I/O model.
// While your JS code runs on a single main thread, Node.js (via libuv) can handle many I/O operations concurrently
// in the background using system calls and its thread pool.
// When an I/O operation completes, its callback is placed in the event queue, and the event loop picks it up.
// This is different from traditional multi-threaded servers where each connection might get its own OS thread (which can be resource-intensive).

// Worker Threads (Node.js `worker_threads` module - distinct from libuv's internal pool):
// For CPU-bound tasks that *you* write in JavaScript/TypeScript, Node.js provides the `worker_threads` module.
// This allows you to create additional threads that can execute JavaScript in parallel, each with its own V8 instance and event loop.
// This is useful for offloading heavy computations without blocking the main event loop responsible for I/O.
// (Detailed example of `worker_threads` could be a separate advanced topic or part of Child Processes).

console.log("\n--- Key Takeaways ---");
console.log("- Node.js uses a single-threaded event loop for your JS code.");
console.log("- I/O operations are non-blocking, offloaded to the OS/libuv.");
console.log("- The event loop processes callbacks from different phases/queues.");
console.log("- `process.nextTick` and Promise microtasks have high priority.");
console.log("- Avoid blocking the event loop with long-running synchronous code in the main thread.");
console.log("- For CPU-bound tasks in JS, explore Node.js Worker Threads.");

// To compile and run this TypeScript file:
// 1. Save as `2_event_loop_concurrency.ts`
// 2. Compile: `tsc 2_event_loop_concurrency.ts`
// 3. Run: `node 2_event_loop_concurrency.js`
// (You might need to install `fs` types if not already: `npm install --save-dev @types/node`) 