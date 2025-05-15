// 6. Testing Node.js & TypeScript Applications

// Testing is a critical part of software development, ensuring code quality, 
// preventing regressions, and facilitating refactoring.
// For Node.js/TypeScript, popular testing frameworks include Jest, Mocha with Chai, Ava, etc.

// This file will use Jest-like syntax for conceptual examples, as it's widely used.
// To run actual tests, you'd need to install a test runner (e.g., `npm install --save-dev jest @types/jest ts-jest`).
// And configure it (e.g., `jest.config.js` and `tsconfig.json` for `ts-jest`).

console.log("--- Testing Node.js & TypeScript Applications (Conceptual Examples) ---");

// --- 1. Types of Tests ---
console.log("\n--- 1. Types of Tests ---");
console.log("- **Unit Tests:** Test individual functions, classes, or modules in isolation. Dependencies are often mocked.");
console.log("- **Integration Tests:** Test how multiple components/modules interact with each other. " +
  "May involve real external services (like a test database) or mocked services.");
console.log("- **End-to-End (E2E) Tests:** Test the entire application flow from the user\'s perspective " +
  "(e.g., making HTTP requests to an API and checking responses, or simulating UI interactions).");

// --- 2. Example Code to Test ---
// Let's define a simple module to test.

// src/utils/math.ts (Conceptual file)
export function add(a: number, b: number): number {
    return a + b;
}

export function subtract(a: number, b: number): number {
    return a - b;
}

export async function fetchDataFromAPI(userId: number): Promise<{ id: number; name: string }> {
    // In a real app, this would make an HTTP request.
    console.log(`TEST_TARGET: Simulating API call for userId: ${userId}`);
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (userId <= 0) {
                reject(new Error("User ID must be positive"));
            }
            if (userId === 99) {
                reject(new Error("User not found (simulated)"));
            }
            resolve({ id: userId, name: `User ${userId}` });
        }, 50);
    });
}

// src/services/userService.ts (Conceptual file)
// import { fetchDataFromAPI } from '../utils/apiClient'; // Assuming apiClient.ts has fetchDataFromAPI
export class UserService {
    // Simulating a dependency that would normally be injected or imported
    private apiFetcher: (userId: number) => Promise<{ id: number; name: string }>;

    constructor(fetcher?: (userId: number) => Promise<{ id: number; name: string }>) {
        this.apiFetcher = fetcher || fetchDataFromAPI;
    }

    async getUserGreeting(userId: number): Promise<string> {
        try {
            const user = await this.apiFetcher(userId);
            return `Hello, ${user.name}!`;
        } catch (error) {
            // Type check the error before accessing properties
            if (error instanceof Error && error.message === "User not found (simulated)") {
                return "User not found.";
            }
            // Re-throw or throw a new error if it's not the one we're specifically handling
            if (error instanceof Error) {
                 throw new Error(`Failed to get user greeting: ${error.message}`);
            }
            throw new Error(`Failed to get user greeting due to an unknown error.`);
        }
    }
}

console.log("\n--- 2. Unit Testing Examples (Jest-like syntax) ---");

// describe('Math Utils', () => {
//     describe('add function', () => {
//         it('should correctly add two positive numbers', () => {
//             expect(add(2, 3)).toBe(5);
//         });
// 
//         it('should correctly add a positive and a negative number', () => {
//             expect(add(5, -2)).toBe(3);
//         });
//     });
// 
//     describe('subtract function', () => {
//         it('should correctly subtract two numbers', () => {
//             expect(subtract(10, 4)).toBe(6);
//         });
//     });
// });

console.log('// Example Test for `add` function:');
console.log("//   test('adds 2 + 3 to equal 5', () => { expect(add(2, 3)).toBe(5); });");

console.log("\n--- 3. Testing Asynchronous Code (Jest-like syntax) ---");

// describe('fetchDataFromAPI', () => {
//     it('should fetch user data for a valid ID', async () => {
//         const user = await fetchDataFromAPI(1);
//         expect(user).toEqual({ id: 1, name: 'User 1' });
//     });
// 
//     it('should reject with an error for an invalid ID (<=0)', async () => {
//         // When testing for promises that should reject
//         await expect(fetchDataFromAPI(0)).rejects.toThrow('User ID must be positive');
//     });
// 
//     it('should handle user not found error', async () => {
//         await expect(fetchDataFromAPI(99)).rejects.toThrow('User not found (simulated)');
//     });
// });

console.log('// Example Test for `fetchDataFromAPI` (successful case):');
console.log("//   test('fetches user 1 data', async () => { ");
console.log("//     const user = await fetchDataFromAPI(1); ");
console.log("//     expect(user).toEqual({ id: 1, name: 'User 1' }); ");
console.log("//   });");
console.log('// Example Test for `fetchDataFromAPI` (error case):');
console.log("//   test('throws for invalid user ID', async () => { ");
console.log("//     await expect(fetchDataFromAPI(0)).rejects.toThrow('User ID must be positive'); ");
console.log("//   });");

console.log("\n--- 4. Mocking and Stubbing Dependencies (Jest-like syntax) ---");
// Mocking is replacing parts of your code (especially external dependencies)
// with controlled fakes during tests, to isolate the unit under test.

// Conceptual: If fetchDataFromAPI was in its own module, e.g., './apiClient'
// // __mocks__/apiClient.ts (Jest auto-mocking or manual mock)
// export const fetchDataFromAPI = jest.fn();

// describe('UserService with Mocked API', () => {
//     let userService: UserService;
//     const mockFetch = jest.fn(); // Create a Jest mock function

//     beforeEach(() => {
//         mockFetch.mockReset(); // Reset mock state before each test
//         userService = new UserService(mockFetch as any); // Inject the mock
//     });

//     it('should return a greeting if user is found', async () => {
//         mockFetch.mockResolvedValue({ id: 1, name: 'Mocked Alice' }); // Configure mock to return a value
        
//         const greeting = await userService.getUserGreeting(1);
//         expect(greeting).toBe('Hello, Mocked Alice!');
//         expect(mockFetch).toHaveBeenCalledWith(1); // Verify mock was called correctly
//         expect(mockFetch).toHaveBeenCalledTimes(1);
//     });

//     it('should return "User not found." if API indicates user not found', async () => {
//         mockFetch.mockRejectedValue(new Error('User not found (simulated)'));
        
//         const greeting = await userService.getUserGreeting(99);
//         expect(greeting).toBe('User not found.');
//         expect(mockFetch).toHaveBeenCalledWith(99);
//     });

//     it('should throw an error if API call fails with an unexpected error', async () => {
//         mockFetch.mockRejectedValue(new Error('Network Failure'));
        
//         await expect(userService.getUserGreeting(2)).rejects.toThrow('Failed to get user greeting: Network Failure');
//         expect(mockFetch).toHaveBeenCalledWith(2);
//     });
// });

console.log('// Example: Mocking `fetchDataFromAPI` for `UserService` tests:');
console.log("//   const mockApiFetcher = jest.fn();");
console.log("//   const userService = new UserService(mockApiFetcher); ");
console.log("//   mockApiFetcher.mockResolvedValue({ id: 1, name: 'Mock User' }); ");
console.log("//   const greeting = await userService.getUserGreeting(1); ");
console.log("//   expect(greeting).toBe('Hello, Mock User!'); ");
console.log("//   expect(mockApiFetcher).toHaveBeenCalledWith(1); ");

console.log("\n--- 5. Code Coverage ---");
// - Test runners like Jest can generate code coverage reports.
// - This shows what percentage of your code (lines, branches, functions) is executed by your tests.
// - Aim for high coverage, but focus on testing critical paths and complex logic thoroughly.
// - 100% coverage doesn't guarantee bug-free code, but low coverage indicates untested areas.
// - Jest command: `jest --coverage`

console.log("\n--- Key Takeaways for Testing ---");
console.log("- Write tests for different granularities: unit, integration, E2E.");
console.log("- Use a testing framework like Jest or Mocha/Chai.");
console.log("- Test both success paths and error/edge cases.");
console.log("- Isolate units under test by mocking their external dependencies.");
console.log("- Asynchronous code requires specific testing patterns (e.g., `async/await` in tests, `expect(...).rejects`).");
console.log("- Strive for good code coverage and maintain tests as your code evolves.");

// To set up and run these tests properly (e.g., with Jest):
// 1. `npm install --save-dev jest @types/jest ts-jest typescript`
// 2. Create `jest.config.js`:
//    module.exports = {
//        preset: 'ts-jest',
//        testEnvironment: 'node',
//    };
// 3. Place tests in files like `*.test.ts` or `*.spec.ts` (e.g., `math.test.ts`).
// 4. Run tests: `npx jest` or add to `package.json` scripts: `"test": "jest"` then `npm test`. 