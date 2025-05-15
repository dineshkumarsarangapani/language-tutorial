// Topic 7: Child Processes in Node.js
// --------------------------------------

// The `child_process` module in Node.js provides the ability to create subprocesses
// in a way that is similar, but not identical, to popen(3). This capability is
// primarily provided by the `child_process.spawn()` function, with other functions
// being conveniences built on top of it.

// Key Concepts:
// 1. Different functions for creating child processes:
//    - `spawn()`: Spawns a new process using the given command. Good for long-running processes and streaming data.
//    - `exec()`: Spawns a shell and runs a command within that shell, buffering any generated output.
//    - `execFile()`: Similar to `exec()`, but spawns the command directly without first spawning a shell. More efficient and safer.
//    - `fork()`: A special case of `spawn()` for spawning new Node.js processes. Allows for IPC (Inter-Process Communication).

// 2. Communicating with child processes:
//    - Standard I/O (stdio): `stdin`, `stdout`, `stderr` streams can be used for communication.
//    - IPC (Inter-Process Communication): Available with `fork()`, allowing messages to be sent between parent and child.

// 3. Use cases:
//    - Offloading CPU-bound tasks to separate processes to avoid blocking the event loop.
//    - Running external scripts or binaries.
//    - Parallel processing.

console.log("Topic 7: Child Processes in Node.js - File Created");

// More detailed examples and explanations will follow for each sub-topic.
// We will explore:
// - How to use each function (`spawn`, `exec`, `execFile`, `fork`).
// - Different ways to configure child processes (e.g., environment variables, working directory).
// - How to handle data streams from child processes.
// - How to send messages using IPC with `fork()`.
// - Error handling with child processes.
// - Practical examples.

// Let's start with `child_process.spawn()`
// ========================================

// `spawn(command[, args][, options])`
// - `command`: The command to run.
// - `args`: List of string arguments.
// - `options`:
//   - `cwd`: Current working directory of the child process.
//   - `env`: Environment key-value pairs.
//   - `stdio`: Child's stdio configuration (e.g., 'pipe', 'inherit', 'ignore'). Default: 'pipe'.
//   - `shell`: If true, runs command inside of a shell. Uses '/bin/sh' on UNIX, and process.env.ComSpec on Windows.
//   - `detached`: Prepare child to run independently of its parent process.
//   - ... and many more.

import { spawn } from 'node:child_process';
import * as path from 'node:path'; // For path.join if needed later

console.log("\n--- Demonstrating child_process.spawn() ---");

// Example 1: Listing directory contents (e.g., 'ls -lh /usr')
// On Windows, you might use 'cmd' with '/c' and then 'dir'.
// For cross-platform, you might need to check os.platform().
// For simplicity, we'll use 'ls'. If you are on Windows, this specific command will fail.
// You can adapt it to `spawn('cmd', ['/c', 'dir'])` or similar.

const listDir = spawn('ls', ['-lh', '/usr']); // For Unix-like systems

// Handling stdout
listDir.stdout.on('data', (data) => {
  console.log(`stdout:\n${data}`);
});

// Handling stderr
listDir.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

// Handling errors during spawning (e.g., command not found)
listDir.on('error', (error) => {
  console.error(`Failed to start subprocess: ${error.message}`);
});

// Handling process exit
listDir.on('close', (code) => {
  if (code === 0) {
    console.log(`Child process exited successfully (code ${code})`);
  } else {
    console.log(`Child process exited with code ${code}`);
  }
});

listDir.on('exit', (code, signal) => {
    if (code !== null) {
        console.log(`Child process exited with code ${code}`);
    } else if (signal !== null) {
        console.log(`Child process was killed with signal ${signal}`);
    }
});


// Note on 'close' vs 'exit' events:
// - 'exit': Emitted when the child process ends. The stdio streams might still be open.
// - 'close': Emitted when all stdio streams of a child process have been closed.
// It's generally safer to listen for 'close' to ensure all I/O is finished.
// If the process exits due to a signal, the 'signal' argument in 'exit' will contain the signal name.

// To make this example runnable and testable, we might want to spawn a Node.js script
// or a command that is guaranteed to exist and produce some output.
// For now, the 'ls' example (or 'dir' for Windows) illustrates the concept.

// Let's add a more portable example: running another Node.js script.
// First, we need a script to run. Let's imagine a 'helper_script.js' in the same directory:
//
// helper_script.js content:
// console.log('Hello from helper script!');
// console.error('An error from helper script!');
// process.exit(42);

// We will create this helper script in a subsequent step.
// For now, let's write the code to spawn it.

console.log("\n--- Spawning a Node.js script ---");

// We'll use an inline script for simplicity first, then show how to fork a file.
const nodeVersion = spawn('node', ['--version']);

nodeVersion.stdout.on('data', (data) => {
    console.log(`Node.js version: ${data}`);
});

nodeVersion.stderr.on('data', (data) => {
    console.error(`stderr from node --version: ${data}`);
});

nodeVersion.on('close', (code) => {
    console.log(`node --version process exited with code ${code}`);
});

// Next, we'll cover exec(). 