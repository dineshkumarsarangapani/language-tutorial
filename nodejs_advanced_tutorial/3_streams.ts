// 3. Streams in Node.js\n\n// Streams are one of the fundamental concepts in Node.js that enable efficient handling of data flow.\n// They allow you to read data from a source or write data to a destination in chunks, sequentially,\n// without loading the entire data into memory at once. This is particularly useful for large files or network I/O.\n\n// To run this example, ensure you have Node.js types installed for better editor support:\n// npm install --save-dev @types/node\n\nimport * as fs from 'node:fs';
import * as path from 'node:path';
import { Readable, Writable, Duplex, Transform, pipeline } from 'node:stream';
import { createGzip, createGunzip } from 'node:zlib'; // For a Transform stream example

console.log("--- Understanding Streams in Node.js ---");

// --- Types of Streams ---\n// 1. Readable Streams: Abstract sources from which data can be consumed (e.g., fs.createReadStream, http.IncomingMessage).\n// 2. Writable Streams: Abstract destinations to which data can be written (e.g., fs.createWriteStream, http.ClientRequest, process.stdout).\n// 3. Duplex Streams: Both Readable and Writable (e.g., net.Socket, zlib streams).\n// 4. Transform Streams: A type of Duplex stream where the output is computed based on the input (e.g., zlib.createGzip, crypto.createCipher).\n

// --- File Paths Definition ---\nconst baseDir = __dirname; // Assuming a flat structure for simplicity, adjust if examples are in subdirs\nconst sampleFilePath = path.join(baseDir, 'sample_input.txt');\nconst sampleOutputFilePath = path.join(baseDir, 'sample_output.txt'); // Used in Ex2\nconst compressedFilePath = path.join(baseDir, 'sample_output.txt.gz'); // Used in Ex3\nconst sampleOutputFromEventsPath = path.join(baseDir, 'sample_output_from_events_example.txt'); // New file for Ex1\nconst decompressedFilePathEx3 = path.join(baseDir, 'sample_decompressed.txt'); // For Ex3 decompression\nconst uppercaseOutputFilePathEx4 = path.join(baseDir, 'sample_uppercase_output.txt'); // New file for Ex4 output\n

// Create a dummy file for reading (if it doesn't exist, or ensure it has fresh content)\nfs.writeFileSync(sampleFilePath, "Hello from streams!\nThis is line two.\nAnd a third line to make it a bit bigger.\nEnd of sample file.");

// --- Example 1: Reading from a Readable Stream (File) and Writing to a Writable Stream (demonstrating events & file output) ---
console.log("\\n--- Example 1: Readable (File) to Writable (demonstrating events & file output) ---");

const readableFileStream_ex1 = fs.createReadStream(sampleFilePath, { encoding: 'utf8' });
// const writableConsoleStream = process.stdout; // process.stdout is a Writable stream // Kept for reference

console.log(`Attempting to read \`${sampleFilePath}\`. Event logs will show chunks. Also piping to \`${sampleOutputFromEventsPath}\` `);

readableFileStream_ex1.on('data', (chunk) => {
    console.log(`READABLE_STREAM (data event - Ex1): Received chunk -> "${chunk.toString().replace(/\n/g, "\\\\n")}"`);
});

readableFileStream_ex1.on('end', () => {
    console.log("READABLE_STREAM (end event - Ex1): No more data to read from file.");
});

readableFileStream_ex1.on('error', (err) => {
    console.error("READABLE_STREAM (error event - Ex1): Error reading file:", err);
});

// Also pipe to a file to demonstrate another way of consuming the stream
const writableToFileFromEvents = fs.createWriteStream(sampleOutputFromEventsPath);
// Note: Re-piping a stream that's already being consumed by .on('data') can be tricky.\n// For this example, we'll create a new readable stream for the pipe for clarity,\n// or ensure this pipe happens before .on('data') if an explicit order is needed.\n// However, since readableFileStream_ex1 is fresh, this should be fine.\nreadableFileStream_ex1.pipe(writableToFileFromEvents);\n\nwritableToFileFromEvents.on('finish', () => {\n    console.log(`WRITABLE_STREAM (finish event - Ex1): Data successfully piped to \`${sampleOutputFromEventsPath}\`.`);\n});\nwritableToFileFromEvents.on('error', (err) => {\n    console.error(`WRITABLE_STREAM (error event - Ex1): Error writing to \`${sampleOutputFromEventsPath}\`:`, err);\n});\n\n// --- Example 2: Piping from Readable to Writable (File to File) ---
console.log("\\n--- Example 2: Piping Readable (File) to Writable (File) ---");

const sourceStream_ex2 = fs.createReadStream(sampleFilePath);\nconst destinationStream_ex2 = fs.createWriteStream(sampleOutputFilePath);\n\nconsole.log(`Piping from \`${sampleFilePath}\` to \`${sampleOutputFilePath}\`...`);

pipeline(sourceStream_ex2, destinationStream_ex2, (err) => {\n    if (err) {\n        console.error(`PIPELINE_ERROR (Ex2): Error piping to \`${sampleOutputFilePath}\`:`, err);\n    } else {\n        console.log(`PIPELINE_SUCCESS (Ex2): Data successfully piped to \`${sampleOutputFilePath}\`.`);\n    }\n});\n\n// --- Example 3: Transform Stream (Gzipping and Gunzipping a file) ---
console.log("\\n--- Example 3: Transform Stream (Gzipping and Gunzipping a file) ---");

const fileToCompress_ex3 = fs.createReadStream(sampleFilePath);\nconst gzipTransform_ex3 = createGzip();\nconst compressedOutput_ex3 = fs.createWriteStream(compressedFilePath);\n\nconsole.log(`Compressing \`${sampleFilePath}\` to \`${compressedFilePath}\`...`);

pipeline(fileToCompress_ex3, gzipTransform_ex3, compressedOutput_ex3, (err) => {\n    if (err) {\n        console.error('PIPELINE_ERROR (Ex3 Gzip): Gzip compression pipeline failed.', err);\n    } else {\n        console.log(`PIPELINE_SUCCESS (Ex3 Gzip): Gzip compression successful. Output: \`${compressedFilePath}\``);\n\n        // Now, let's decompress it to verify\n        console.log(`\\nAttempting to decompress \`${compressedFilePath}\` to \`${decompressedFilePathEx3}\`...`);
        const compressedInput_ex3 = fs.createReadStream(compressedFilePath);\n        const gunzipTransform_ex3 = createGunzip();\n        const decompressedOutput_ex3 = fs.createWriteStream(decompressedFilePathEx3);\n\n        pipeline(compressedInput_ex3, gunzipTransform_ex3, decompressedOutput_ex3, (decompressErr) => {\n            if (decompressErr) {\n                console.error('PIPELINE_ERROR (Ex3 Gunzip): Gunzip decompression failed.', decompressErr);\n            } else {\n                console.log(`PIPELINE_SUCCESS (Ex3 Gunzip): Gunzip decompression successful. Output: \`${decompressedFilePathEx3}\``);\n                // You can verify by reading both sampleFilePath and decompressedFilePathEx3 and comparing contents.\n            }\n        });\n    }\n});\n\n// --- Example 4: Creating a Custom Transform Stream (Uppercasing to File) ---
console.log("\\n--- Example 4: Custom Transform Stream (Uppercasing to File) ---");

class UppercaseTransform_ex4 extends Transform {\n    constructor(options?: import('stream').TransformOptions) {\n        super(options);\n    }\n\n    _transform(chunk: any, encoding: BufferEncoding, callback: (error?: Error | null, data?: any) => void): void {\n        try {\n            const uppercasedChunk = chunk.toString().toUpperCase();\n            // console.log(`CUSTOM_TRANSFORM (Ex4): Transforming chunk to uppercase.`); // Optional: can be verbose\n            callback(null, uppercasedChunk);\n        } catch (error: any) {\n            callback(error);\n        }\n    }\n}\n\nconst readableForTransform_ex4 = fs.createReadStream(sampleFilePath, { encoding: 'utf8' });\nconst uppercaseTransformer_ex4 = new UppercaseTransform_ex4();\nconst writableToFileForTransform_ex4 = fs.createWriteStream(uppercaseOutputFilePathEx4);\n\nconsole.log(`Piping file through custom UppercaseTransform_ex4 to \`${uppercaseOutputFilePathEx4}\`...`);
pipeline(readableForTransform_ex4, uppercaseTransformer_ex4, writableToFileForTransform_ex4, (err_ex4) => { // Corrected arrow function parameter
    if (err_ex4) {\n        console.error(`PIPELINE_ERROR (Ex4 Uppercase): Failed to write to \`${uppercaseOutputFilePathEx4}\`.`, err_ex4);\n    } else {\n        console.log(`PIPELINE_SUCCESS (Ex4 Uppercase): Successfully transformed and wrote to \`${uppercaseOutputFilePathEx4}\`.`);\n    }\n});\n\n// --- Backpressure ---\n// When a Readable stream produces data faster than a Writable stream can consume it,\n// data can buffer in memory. Backpressure is a mechanism where the Writable stream\n// signals the Readable stream to pause producing data (`readable.pause()`) when its internal\n// buffer is full, and resume (`readable.resume()`) when it\'s ready for more.\n// The `pipe()` method handles backpressure automatically.\n// If you are manually reading with `.on(\'data\')` and writing with `.write()`, you need to manage backpressure yourself\n// by checking the return value of `writable.write()` and listening for the `\'drain\'` event.\nconsole.log("\\n--- Backpressure (Conceptual) ---");
console.log("- `pipe()` handles backpressure automatically.");
console.log("- If manually using `readable.on(\'data\')` and `writable.write()`, check `writable.write()` return value.");
console.log("  If it returns false, pause the readable stream and wait for the `\'drain\'` event on the writable stream.");

// --- Key Takeaways ---\n// - Streams are powerful for handling large amounts of data efficiently.\n// - Four types: Readable, Writable, Duplex, Transform.\n// - `pipe()` is the easiest way to connect streams and handles backpressure.\n// - `pipeline()` is a utility for piping multiple streams with better error handling.\n// - Listen for events like `data`, `end`, `error`, `finish`, `drain` to manage stream lifecycle.\n// - Custom Transform streams allow for on-the-fly data modification in a streaming fashion.\n

// Cleanup dummy files (optional, for tidiness after demo)\n// Ensure this runs after all stream operations, possibly with a delay or a more robust mechanism\n// For a simple script, a timeout might be okay, but for robust apps, use async/await with promises from stream events.\nsetTimeout(() => {\n    try {\n        console.log("\\nAttempting to clean up sample files...");\n        if(fs.existsSync(sampleFilePath)) fs.unlinkSync(sampleFilePath);\n        if(fs.existsSync(sampleOutputFilePath)) fs.unlinkSync(sampleOutputFilePath);\n        if(fs.existsSync(compressedFilePath)) fs.unlinkSync(compressedFilePath);\n        if(fs.existsSync(sampleOutputFromEventsPath)) fs.unlinkSync(sampleOutputFromEventsPath);\n        if(fs.existsSync(decompressedFilePathEx3)) fs.unlinkSync(decompressedFilePathEx3);\n        if(fs.existsSync(uppercaseOutputFilePathEx4)) fs.unlinkSync(uppercaseOutputFilePathEx4);\n        console.log("Cleaned up sample files (if they existed).");\n    } catch (err) {\n        console.error("Cleanup error:", err);\n    }\n}, 5000); // Increased delay to allow async operations to complete

// To compile and run:\n// 1. Ensure you have @types/node: npm install --save-dev @types/node\n// 2. Compile: tsc 3_streams.ts\n// 3. Run: node 3_streams.js\n// (If your tsconfig.json specifies an outDir, run `node <yourOutDir>/3_streams.js`) 