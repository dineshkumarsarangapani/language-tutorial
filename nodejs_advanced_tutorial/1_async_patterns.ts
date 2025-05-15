// 1. Modern Asynchronous JavaScript & TypeScript

// Asynchronous operations are fundamental in Node.js due to its non-blocking I/O model.
// JavaScript (and by extension TypeScript) has evolved its handling of async operations over time.

console.log("--- 1. Callbacks (The Old Way) ---");

// Simulates a function that takes time (e.g., reading a file, API call)
function fetchDataWithCallback(
    id: number,
    callback: (error: Error | null, data?: string) => void
) {
    console.log(`CALLBACK_FUNC: Started fetching data for ID: ${id}`);
    setTimeout(() => {
        if (id <= 0) {
            callback(new Error("Invalid ID provided. Must be positive."));
            return;
        }
        if (id % 5 === 0) { // Simulate a failure for IDs divisible by 5
            callback(new Error(`Failed to fetch data for ID: ${id}. Network error.`));
            return;
        }
        const resultData = `Data for item ${id} - found at ${new Date().toLocaleTimeString()}`;
        console.log(`CALLBACK_FUNC: Successfully fetched: ${resultData}`);
        callback(null, resultData);
    }, 50); // Short delay for demo
}

// Using the callback-based function
fetchDataWithCallback(1, (err, data) => {
    if (err) {
        console.error("Callback Result (ID 1) Error:", err.message);
    } else {
        console.log("Callback Result (ID 1) Data:", data);
    }
});

fetchDataWithCallback(5, (err, data) => { // This one will fail
    if (err) {
        console.error("Callback Result (ID 5) Error:", err.message);
    } else {
        console.log("Callback Result (ID 5) Data:", data);
    }
});

// "Callback Hell" or "Pyramid of Doom" - nested callbacks for sequential operations
// fetchDataWithCallback(1, (err1, data1) => {
//     if (err1) { console.error(err1); }
//     else { 
//         fetchDataWithCallback(2, (err2, data2) => {
//             if (err2) { console.error(err2); }
//             else { console.log("Nested callback success:", data1, data2); }
//         });
//     }
// });
console.log("Callback-based operations initiated. They will complete asynchronously.\n");

// Issues with callbacks:
// - Callback hell makes code hard to read and maintain.
// - Error handling can be inconsistent and verbose.
// - Difficult to manage complex asynchronous flows (e.g., parallel operations, conditional execution).

// Wait for callback examples to finish before moving to Promises for cleaner console output
setTimeout(() => {
    console.log("\n--- 2. Promises ---");

    function fetchDataWithPromise(id: number): Promise<string> {
        console.log(`PROMISE_FUNC: Started fetching data for ID: ${id}`);
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (id <= 0) {
                    reject(new Error("Invalid ID provided. Must be positive."));
                    return;
                }
                if (id % 7 === 0) { // Simulate a failure for IDs divisible by 7
                    reject(new Error(`Failed to fetch data for ID: ${id}. Simulated database error.`));
                    return;
                }
                const resultData = `PROMISE Data for item ${id} - found at ${new Date().toLocaleTimeString()}`;
                console.log(`PROMISE_FUNC: Successfully fetched: ${resultData}`);
                resolve(resultData);
            }, 70);
        });
    }

    // Using a Promise: .then() for success, .catch() for errors
    fetchDataWithPromise(2)
        .then(data => {
            console.log("Promise Result (ID 2) Data:", data);
        })
        .catch(error => {
            console.error("Promise Result (ID 2) Error:", error.message);
        });

    fetchDataWithPromise(7) // This will be rejected
        .then(data => {
            console.log("Promise Result (ID 7) Data:", data); // This won't run
        })
        .catch(error => {
            console.error("Promise Result (ID 7) Error:", error.message);
        })
        .finally(() => {
            console.log("Promise (ID 7) finally() block executed, regardless of success/failure.");
        });

    // Chaining Promises for sequential operations (much cleaner than callback hell)
    console.log("PROMISE_CHAIN: Initiating promise chain...");
    fetchDataWithPromise(3)
        .then(data3 => {
            console.log("Promise Chain (ID 3) Data:", data3);
            // Use the result of the first promise to make another call
            const nextId = Number.parseInt(data3.split(" ")[3]) + 1; // e.g. 3 + 1 = 4. Use Number.parseInt
            return fetchDataWithPromise(nextId);
        })
        .then(data4 => {
            console.log("Promise Chain (ID from prev) Data:", data4);
        })
        .catch(error => {
            console.error("Promise Chain Error:", error.message);
        });

    // Promise.all() - waits for all promises to resolve, or rejects if any one rejects
    console.log("PROMISE_ALL: Initiating Promise.all()...");
    Promise.all([
        fetchDataWithPromise(10),
        fetchDataWithPromise(11),
        // fetchDataWithPromise(14) // Uncomment to make Promise.all() reject
    ])
    .then(results => {
        console.log("Promise.all() Results:", results);
    })
    .catch(error => {
        console.error("Promise.all() Error (one of the promises rejected):", error.message);
    });

    // Promise.allSettled() - waits for all promises to settle (either resolve or reject)
    console.log("PROMISE_ALL_SETTLED: Initiating Promise.allSettled()...");
    Promise.allSettled([
        fetchDataWithPromise(20),
        fetchDataWithPromise(21), // This one will reject (divisible by 7)
        fetchDataWithPromise(22)
    ])
    .then(results => {
        console.log("Promise.allSettled() Results:");
        for (const result of results) {
            if (result.status === "fulfilled") {
                console.log(`  Fulfilled: ${result.value}`);
            } else {
                console.error(`  Rejected: ${result.reason.message}`);
            }
        }
    });

    // Promise.race() - resolves or rejects as soon as one of the promises resolves or rejects
    console.log("PROMISE_RACE: Initiating Promise.race()...");
    Promise.race([
        fetchDataWithPromise(30), // Slower if others are faster
        new Promise(resolve => setTimeout(() => resolve("Fast promise resolved!"), 60)), // Faster promise
        fetchDataWithPromise(31)
    ])
    .then(winner => {
        console.log("Promise.race() Winner:", winner);
    })
    .catch(error => {
        console.error("Promise.race() Error (first settled promise was a rejection):", error.message);
    });

    // Promise.any() - resolves as soon as one promise fulfills, rejects if all reject
    console.log("PROMISE_ANY: Initiating Promise.any()...");
    Promise.any([
        fetchDataWithPromise(42), // Will fail (divisible by 7)
        fetchDataWithPromise(40),
        fetchDataWithPromise(49)  // Will fail
    ])
    .then(firstFulfilled => {
        console.log("Promise.any() First Fulfilled:", firstFulfilled);
    })
    .catch(aggregateError => {
        // aggregateError.errors is an array of rejection reasons
        console.error("Promise.any() All Rejected: Ensure at least one promise can resolve.", aggregateError.errors.map((e: Error) => e.message));
    });

    console.log("Promise-based operations initiated. They will complete asynchronously.\n");

    // Wait for Promise examples to mostly finish for cleaner console output
    setTimeout(() => {
        console.log("\n--- 3. async/await (Syntactic Sugar over Promises) ---");

        async function processDataWithAsyncAwait() {
            console.log("ASYNC_AWAIT: Starting data processing flow...");
            try {
                const dataA = await fetchDataWithPromise(100);
                console.log("Async/Await Result (ID 100) Data:", dataA);

                const dataB = await fetchDataWithPromise(101);
                console.log("Async/Await Result (ID 101) Data:", dataB);
                
                console.log("ASYNC_AWAIT: Attempting to fetch data that will fail (ID 105)...");
                const dataC = await fetchDataWithPromise(105); // 105 is divisible by 7, will reject
                console.log("Async/Await Result (ID 105) Data (should not reach here):", dataC);

            } catch (error) {
                if (error instanceof Error) {
                    console.error("Async/Await Flow Error:", error.message);
                } else {
                    console.error("Async/Await Flow Error: An unknown error occurred", error);
                }
            }
            console.log("ASYNC_AWAIT: Data processing flow finished (or caught an error).");
        }

        processDataWithAsyncAwait();

        // async function that returns a value (implicitly a Promise)
        async function getUserDetails(userId: number): Promise<{ id: number; name: string }> {
            console.log(`ASYNC_AWAIT: Fetching user details for ${userId}`);
            await new Promise(resolve => setTimeout(resolve, 80)); // Simulate network delay
            if (userId < 0) throw new Error("User ID cannot be negative in getUserDetails");
            return { id: userId, name: `User ${userId}` };
        }

        async function displayUserDetails() {
            try {
                const user = await getUserDetails(200);
                console.log("Async/Await UserDetails:", user);
                const failingUser = await getUserDetails(-1); // This will throw
                console.log("Async/Await FailingUserDetails (should not reach here):", failingUser);
            } catch (error) {
                if (error instanceof Error) {
                    console.error("Async/Await displayUserDetails Error:", error.message);
                } else {
                    console.error("Async/Await displayUserDetails Error: An unknown error occurred", error);
                }
            }
        }

        displayUserDetails();
        console.log("Async/await operations initiated.");

        // Using async/await with Promise.all for concurrent operations
        async function fetchMultipleDataConcurrently() {
            console.log("ASYNC_AWAIT_ALL: Starting concurrent fetches...");
            try {
                const [result1, result2, result3] = await Promise.all([
                    fetchDataWithPromise(300),
                    fetchDataWithPromise(301),
                    fetchDataWithPromise(302) // Ensuring three promises
                ]);
                console.log("Async/Await Promise.all() Results:", { result1, result2, result3 });
            } catch (error) {
                if (error instanceof Error) {
                    console.error("Async/Await Promise.all() Error:", error.message);
                } else {
                    console.error("Async/Await Promise.all() Error: An unknown error occurred", error);
                }
            }
        }
        fetchMultipleDataConcurrently();

    }, 2000); // Delay to let promise examples run

}, 1000); // Delay to let callback examples run


// Key Takeaways:
// - Callbacks: Prone to "callback hell", error handling is manual and can be tricky.
// - Promises: Provide a cleaner way to handle async operations with .then() for success/chaining 
//   and .catch() for errors. Methods like Promise.all, allSettled, race, any provide powerful concurrency patterns.
// - async/await: Syntactic sugar on top of Promises, making asynchronous code look and behave 
//   a bit more like synchronous code, especially with try/catch for error handling.
//   It greatly improves readability and maintainability for complex async flows.
// - Node.js heavily relies on these patterns for its non-blocking nature.

// To compile and run this TypeScript file:
// 1. Save as `1_async_patterns.ts`
// 2. Compile: `tsc 1_async_patterns.ts` (ensure you have tsconfig.json or use appropriate flags)
// 3. Run: `node 1_async_patterns.js` 