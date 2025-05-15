// 4. Modules, Packages & Project Structure in Node.js/TypeScript

// Effective management of modules, packages, and overall project structure is key to
// building maintainable and scalable Node.js and TypeScript applications.

// Note: For TypeScript to correctly understand Node.js built-in modules and features,
// ensure you have `@types/node` installed in your project: `npm install --save-dev @types/node`

console.log("--- Modules, Packages & Project Structure ---");

// --- 1. Module Systems: CommonJS vs. ES Modules (ESM) ---

console.log("\n--- 1.1 CommonJS (CJS) - The Traditional Node.js Way ---");
// - Used by default in `.js` files or when `"type": "commonjs"` is in `package.json` (or no type is set).
// - Uses `require()` to import modules and `module.exports` or `exports` to export.
// - Synchronous: `require()` calls are blocking.
// - TypeScript can compile to CommonJS.

// Conceptual example (if this were a .js file or TS compiling to CJS):
// // my-math-module.js
// const add = (a, b) => a + b;
// module.exports = { add };
// 
// // main.js
// const { add } = require('./my-math-module');
// console.log(add(2, 3)); // 5

console.log("- Uses `require()` for imports and `module.exports` or `exports`.");
console.log("- Synchronous module loading.");
console.log("- TypeScript typically compiles to CommonJS by default for Node.js targets unless configured otherwise.");

console.log("\n--- 1.2 ES Modules (ESM) - The JavaScript Standard ---");
// - The standard module system for JavaScript, increasingly adopted by Node.js.
// - Used in `.mjs` files, or when `"type": "module"` is in `package.json`.
// - Uses `import` and `export` statements.
// - Asynchronous loading (top-level await is supported).
// - TypeScript fully supports ESM and can compile to ESM targets.

// Conceptual example (if this were an .mjs file or TS compiling to ESM):
// // my-string-utils.ts (or .mjs)
// export const greet = (name: string) => `Hello, ${name}!`;
// export const PI = 3.14159;
// 
// // main.ts (or .mjs)
// import { greet, PI } from './my-string-utils';
// import * as path from 'node:path'; // Importing built-in Node module with ESM
// console.log(greet('World'));
// console.log(`Path sep: ${path.sep}`);

console.log("- Uses `import` and `export` syntax.");
console.log("- Supports asynchronous loading and top-level await.");
console.log("- To use ESM in Node.js: use `.mjs` extension, or set `\"type\": \"module\"` in `package.json`.");
console.log("- When using ESM, import built-in Node modules with `node:` prefix (e.g., `import fs from 'node:fs'`).");

console.log("\n--- 1.3 TypeScript Configuration for Modules (`tsconfig.json`) ---");
// The `tsconfig.json` file controls how TypeScript compiles your code, including module output.
// Key compilerOptions related to modules:
// - `module`: Specifies the module system for the output JavaScript.
//   - `"CommonJS"`: (Default for many Node.js projects) Emits CommonJS.
//   - `"ESNext"`, `"ES2015"`, `"ES2020"`, `"ES2022"`: Emits modern ES Modules.
//   - `"NodeNext"` (or `"Node16"`): A newer option that adapts to the `type` field in your `package.json`
//     and supports features like a mix of CJS/ESM if Node.js version allows.
// - `moduleResolution`: How TypeScript resolves module imports.
//   - `"Node"`: The classic Node.js resolution strategy (for CommonJS).
//   - `"NodeNext"` (or `"Node16"`): Modern Node.js resolution, supports conditional exports, self-referencing, etc.
//     Recommended when `module` is `NodeNext` or `Node16`.
// - `target`: The JavaScript version of the output (e.g., `"ES2020"`). Should generally be modern.
// - `esModuleInterop`: (Default `true`) Enables better interoperability between CommonJS and ES Modules.
//   Allows default imports from CommonJS modules like `import fs from 'fs';` (if `module` is not CJS).

console.log('Key tsconfig.json options for modules:');
console.log(`  - "module": e.g., "CommonJS", "ESNext", "NodeNext"`);
console.log(`  - "moduleResolution": e.g., "Node", "NodeNext"`);
console.log(`  - "target": e.g., "ES2020", "ESNext"`);
console.log(`  - "esModuleInterop": true (usually recommended)`);
console.log("Choosing `NodeNext` for both `module` and `moduleResolution` is often a good modern default when `\"type\": \"module\"` is in package.json.");

// --- 2. Packages and `package.json` ---
console.log("\n--- 2. Package Management (`npm` or `yarn`) and `package.json` ---");
// - `package.json`: The manifest file for your Node.js project.
//   - `name`, `version`, `description`, `author`, `license`.
//   - `main`: Entry point for CommonJS packages (e.g., `"main": "dist/index.js"`).
//   - `module`: Entry point for ES Modules (often used by bundlers).
//   - `type`: Specifies module system (`"commonjs"` or `"module"`).
//   - `scripts`: Defines runnable scripts (e.g., `"start": "node dist/index.js"`, `"build": "tsc"`).
//   - `dependencies`: Packages required for your application to run in production.
//   - `devDependencies`: Packages needed only for development (e.g., TypeScript, linters, testing libraries).
//   - `exports`: (For ESM and modern Node.js) Defines the public API of your package, allowing conditional exports for different environments or module systems.
// - `npm` (Node Package Manager) or `yarn`: Command-line tools to manage dependencies.
//   - `npm install <package>` or `yarn add <package>`
//   - `npm install` or `yarn install`: Installs all dependencies from `package.json`.
// - `node_modules/`: Directory where dependencies are installed.
// - `package-lock.json` (npm) or `yarn.lock` (yarn): Lock files that record the exact versions of installed dependencies,
//   ensuring consistent installs across different environments.

console.log("- `package.json` is the project manifest (metadata, scripts, dependencies).");
console.log("- `dependencies` are for runtime, `devDependencies` for development.");
console.log("- `package-lock.json` or `yarn.lock` ensures deterministic builds.");


// --- 3. Project Structure Best Practices (General Guidelines) ---
console.log("\n--- 3. Project Structure Best Practices ---");
// While there's no single "correct" structure, some common patterns improve maintainability:

// /my-node-app
// |-- /dist                     // Compiled JavaScript output (from TypeScript)
// |-- /src                      // TypeScript source files
// |   |-- /app                  // Core application logic (e.g., services, controllers if building an API)
// |   |   |-- /services
// |   |   |-- /routes (or /controllers)
// |   |   |-- index.ts          // Main application setup
// |   |-- /config               // Configuration files or modules
// |   |-- /lib (or /utils)      // Shared utility functions, helper modules
// |   |-- /middlewares          // (If applicable, e.g., for Express/Fastify)
// |   |-- /models (or /entities)// Data models, interfaces, types
// |   |-- /types                // Global or shared TypeScript type definitions (e.g., custom.d.ts)
// |   |-- server.ts             // Entry point to start the server (imports from app/index.ts)
// |-- /tests                    // Unit, integration, E2E tests
// |   |-- /unit
// |   |-- /integration
// |-- .env                      // Environment variables (add to .gitignore)
// |-- .eslintignore
// |-- .eslintrc.js (or .json)
// |-- .gitignore
// |-- .prettierrc.js (or .json)
// |-- nodemon.json              // (If using nodemon for development)
// |-- package.json
// |-- package-lock.json (or yarn.lock)
// |-- README.md
// |-- tsconfig.json

console.log("Common directory structure recommendations:");
console.log("  - `/src`: Contains all your TypeScript source code.");
console.log("  - `/dist`: Output directory for compiled JavaScript (from `tsc`). Add to `.gitignore`.");
console.log("  - `/tests`: Houses all test files, often mirroring the `/src` structure.");
console.log("  - Group by feature or by type (e.g., `/src/users/user.service.ts`, `/src/users/user.controller.ts` vs. `/src/services/user.service.ts`, `/src/controllers/user.controller.ts`). Feature-based grouping often scales better.");
console.log("  - Clear entry point (e.g., `src/server.ts` or `src/index.ts`).");
console.log("  - Configuration separated from core logic (e.g., in `/src/config` or using .env files).");

// --- Example: Conceptual Module Import/Export (Illustrative) ---
// This is to illustrate how you might structure and use modules.

// // src/utils/formatter.ts
// export function formatDate(date: Date): string {
//     return date.toISOString().split('T')[0];
// }

// // src/services/userService.ts
// import { formatDate } from '../utils/formatter';
// interface User { id: number; name: string; joined: Date }
// export class UserService {
//     getUserGreeting(user: User): string {
//         return `Hello, ${user.name}! You joined on ${formatDate(user.joined)}.`;
//     }
// }

// // src/app/index.ts (or main application file)
// import { UserService } from '../services/userService';
// const userService = new UserService();
// console.log(userService.getUserGreeting({ id: 1, name: "Alice", joined: new Date() }));

console.log("\n--- Key Takeaways ---");
console.log("- Understand the differences and configuration for CommonJS vs. ES Modules.");
console.log("- Use `\"type\": \"module\"` in `package.json` and `\"module\": \"NodeNext\"`, `\"moduleResolution\": \"NodeNext\"` in `tsconfig.json` for modern Node.js projects.");
console.log("- `package.json` is central to managing project metadata and dependencies.");
console.log("- Adopt a consistent and scalable project structure. Grouping by feature is often preferred for larger applications.");
console.log("- Separate compiled output (`/dist`) from source code (`/src`).");

// To compile this file (assuming you have a tsconfig.json set up):
// tsc 4_modules_structure.ts
// node 4_modules_structure.js (output will be just the console.logs from this file) 