// 5. Advanced Error Handling Strategies in Node.js/TypeScript

// Robust error handling is critical for building reliable Node.js applications.
// This involves more than just try...catch blocks; it includes custom errors,
// consistent propagation, and handling top-level unhandled exceptions.

// Ensure @types/node is installed for Node.js specific globals like `process`
// npm install --save-dev @types/node

console.log("--- Advanced Error Handling Strategies ---");

// --- 1. Custom Error Classes ---
// Creating custom error classes helps in identifying and handling specific error types more effectively.
console.log("\n--- 1. Custom Error Classes ---");

class AppError extends Error {
    public readonly statusCode: number;
    public readonly isOperational: boolean;

    constructor(message: string, statusCode: number, isOperational = true) {
        super(message);
        this.name = this.constructor.name; // Set the error name to the class name
        this.statusCode = statusCode;
        this.isOperational = isOperational; // Operational errors are expected (e.g., user input error, API failure)
                                        // Programmer errors are bugs (e.g., accessing undefined property)
        // Error.captureStackTrace is V8 specific (Node.js)
        if (typeof (Error as any).captureStackTrace === 'function') {
            (Error as any).captureStackTrace(this, this.constructor);
        }
    }
}

class UserInputError extends AppError {
    constructor(message = "Invalid user input provided.") {
        super(message, 400); // HTTP 400 Bad Request
    }
}

class NotFoundError extends AppError {
    constructor(resource = "Resource") {
        super(`${resource} not found.`, 404); // HTTP 404 Not Found
    }
}

class ExternalServiceError extends AppError {
    constructor(serviceName: string, originalError?: Error) {
        let message = `Error communicating with external service: ${serviceName}.`;
        if (originalError?.message) {
            message += ` Details: ${originalError.message}`;
        }
        super(message, 503, true); // HTTP 503 Service Unavailable
    }
}

// Define an expected structure for user data, even if simple
interface UserData {
    id: number;
    // other fields can be optional or defined as needed
    [key: string]: any; 
}

function processUserData(data: unknown): string {
    if (typeof data !== 'object' || data === null || !('id' in data) || typeof (data as UserData).id !== 'number') {
        throw new UserInputError("User data must be an object and include a numeric ID.");
    }
    const userData = data as UserData; // Type assertion after check

    if (userData.id === 99) { // Simulate a resource not found
        throw new NotFoundError(`User with ID ${userData.id}`);
    }
    if (userData.id === 100) { // Simulate an external service call failing
        throw new ExternalServiceError("PaymentGateway");
    }
    return `Processed user ${userData.id} successfully.`;
}

try {
    console.log(processUserData({ id: 1 }));
    // console.log(processUserData({ name: "test" })); // Will throw UserInputError
    // console.log(processUserData({ id: 99 }));    // Will throw NotFoundError
    // console.log(processUserData({ id: 100 }));   // Will throw ExternalServiceError
} catch (error) {
    if (error instanceof AppError) {
        console.error(`HANDLED AppError: [${error.name}] (Status ${error.statusCode}) ${error.message}. IsOperational: ${error.isOperational}`);
    } else if (error instanceof Error) {
        console.error("HANDLED Generic Error:", error.message, error.stack);
    } else {
        console.error("HANDLED Unknown error type:", error);
    }
}

// --- 2. Error Propagation in Asynchronous Code ---
console.log("\n--- 2. Error Propagation in Asynchronous Code ---");

// 2.1 Promises
function simulateAsyncOperation(succeed: boolean): Promise<string> {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (succeed) {
                resolve("Async operation successful!");
            } else {
                // It's good practice to reject with an Error object, not just a string.
                reject(new ExternalServiceError("RemoteAPI", new Error("Connection timed out")));
            }
        }, 50);
    });
}

simulateAsyncOperation(true)
    .then(result => console.log("Promise Success:", result))
    .catch((error) => {
        if (error instanceof AppError) {
            console.error(`Promise Handled AppError: [${error.name}] ${error.message}`);
        } else if (error instanceof Error) {
            console.error(`Promise Handled Generic Error: ${error.message}`);
        } else {
            console.error("Promise Handled Unknown error type:", error);
        }
    });

simulateAsyncOperation(false)
    .then(result => console.log("Promise Success (should not happen):", result))
    .catch((error) => {
        if (error instanceof AppError) {
            console.error(`Promise Handled AppError: [${error.name}] ${error.message}`);
        } else if (error instanceof Error) {
            console.error(`Promise Handled Generic Error: ${error.message}`);
        } else {
            console.error("Promise Handled Unknown error type:", error);
        }
    });

// 2.2 async/await
async function performChainedAsyncOperations() {
    console.log("Async/Await: Starting chained operations...");
    try {
        const result1 = await simulateAsyncOperation(true);
        console.log("Async/Await Result 1:", result1);
        
        // This will throw an error
        const result2 = await simulateAsyncOperation(false);
        console.log("Async/Await Result 2 (should not reach here):", result2);
        
    } catch (error) {
        if (error instanceof AppError) {
            console.error(`Async/Await Handled AppError: [${error.name}] (Status ${error.statusCode}) ${error.message}`);
        } else if (error instanceof Error) {
             console.error("Async/Await Handled Generic Error:", error.message);
        } else {
            console.error("Async/Await Handled Unknown Error Type:", error);
        }
    }
    console.log("Async/Await: Chained operations finished or error handled.");
}

// performChainedAsyncOperations(); // Call this to see async/await error handling

// --- 3. Handling Unhandled Rejections and Uncaught Exceptions ---
// These are global error handlers, acting as a last line of defense.
// They should primarily be used for logging the error and then gracefully shutting down the application.
// Attempting to recover and continue running after such an error is generally risky as the application state might be corrupted.
console.log("\n--- 3. Handling Unhandled Rejections and Uncaught Exceptions (Process Level) ---");

process.on('unhandledRejection', (reason: unknown, promise: Promise<unknown>) => {
    console.error('------------------------------------');
    console.error('GLOBAL_HANDLER: Unhandled Rejection at:', promise, 'reason:', reason);
    if (reason instanceof Error) {
        console.error('Stack trace:', reason.stack);
    } else {
        console.error('Reason (not an Error object):', reason);
    }
    console.error('------------------------------------');
    // Recommended: Log the error to a monitoring service.
    // Then, gracefully shut down the server. Forcing an exit might lose ongoing requests or data.
    // For a server, this might involve closing DB connections, stopping new requests, etc.
    // process.exit(1); // Exit with a failure code (use with caution in a real server)
});

process.on('uncaughtException', (error: Error, origin: string) => {
    console.error('------------------------------------');
    console.error(`GLOBAL_HANDLER: Uncaught Exception. Origin: ${origin}. Error:`, error);
    console.error('Stack trace:', error.stack);
    console.error('------------------------------------');
    // Recommended: Log the error to a monitoring service.
    // CRITICAL: The application is in an undefined state. It's not safe to resume normal operation.
    // Gracefully shut down. No more requests should be processed.
    // fs.writeSync(process.stderr.fd, `Uncaught Exception: ${error.message}\nStack: ${error.stack}`); // Log to stderr before exiting
    // process.exit(1); // Exit with a failure code
});

// Example to trigger unhandledRejection (if not caught elsewhere):
// Promise.reject(new AppError("Async task failed badly and was not caught!", 500));

// Example to trigger uncaughtException:
// setTimeout(() => {
//     throw new Error("Something broke synchronously in an async callback and wasn't caught!");
// }, 1500);

console.log("Global unhandledRejection and uncaughtException handlers are set up.");
console.log("In a real app, these should log and gracefully exit.");

// --- 4. Operational Errors vs. Programmer Errors ---
// - Operational Errors: Expected errors that can occur during normal operation due to external factors
//   (e.g., network failure, invalid user input, third-party API unavailable, DB timeout).
//   - These should be handled gracefully, often by retrying, informing the user, or using fallbacks.
//   - Our `AppError` with `isOperational = true` is an example.
// - Programmer Errors (Bugs): Mistakes in the code (e.g., `TypeError`, `ReferenceError`, accessing `undefined` property).
//   - These are unexpected and indicate a flaw in the application logic.
//   - Ideally, they should be caught during development/testing.
//   - If they occur in production, they should be logged thoroughly, and the application might need to be
//     restarted as its state could be inconsistent. `uncaughtException` often catches these.

console.log("\n--- 4. Operational vs. Programmer Errors ---");
console.log("- Operational errors are expected (e.g., bad user input, API down). Handle them.");
console.log("- Programmer errors are bugs. Log them, and the process may need to restart.");

// --- Key Takeaways ---
// - Use custom error classes inheriting from `Error` for better error identification.
// - Include properties like `statusCode` and `isOperational` in custom errors for context.
// - Ensure errors are consistently propagated (returned or thrown) in async code (Promises/async-await).
// - Implement global `unhandledRejection` and `uncaughtException` handlers to log critical errors
//   and gracefully shut down the application. Avoid resuming operation after an uncaught exception.
// - Distinguish between operational errors (handle, retry, inform user) and programmer errors (fix the bug).

// To run this (after tsc compilation to JS):
// node 5_error_handling.js
// (You might need to uncomment some of the error-triggering examples to see handlers in action)
// (Also, the global handlers might cause the Node process to exit if `process.exit(1)` is uncommented)

// Small delay to allow async promise examples to run before script potentially ends due to global handlers
setTimeout(() => {
    console.log("\nError handling script finished its main execution path.");
    // Call performChainedAsyncOperations to see its error handling
    performChainedAsyncOperations();
}, 200); 