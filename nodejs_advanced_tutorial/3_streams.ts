/**
 * Streams in Node.js
 * 
 * Streams are one of the fundamental concepts in Node.js that enable efficient handling of data flow.
 * They allow you to read data from a source or write data to a destination in chunks, sequentially,
 * without loading the entire data into memory at once. This is particularly useful for large files or network I/O.
 */

// Import required modules
import * as fs from 'node:fs';
import * as path from 'node:path';
import { Readable, Writable, Duplex, Transform, pipeline } from 'node:stream';
import { createGzip, createGunzip } from 'node:zlib'; // For a Transform stream example
import { fileURLToPath } from 'node:url';

console.log("--- Understanding Streams in Node.js ---");

// --- Types of Streams ---
// 1. Readable Streams: Abstract sources from which data can be consumed (e.g., fs.createReadStream, http.IncomingMessage).
// 2. Writable Streams: Abstract destinations to which data can be written (e.g., fs.createWriteStream, http.ClientRequest, process.stdout).
// 3. Duplex Streams: Both Readable and Writable (e.g., net.Socket, zlib streams).
// 4. Transform Streams: A type of Duplex stream where the output is computed based on the input (e.g., zlib.createGzip, crypto.createCipher).

// --- File Paths Definition ---
// In ES modules, __dirname is not available, so we need to construct it
const __filename = fileURLToPath(import.meta.url);
const baseDir = path.dirname(__filename); 
const sampleFilePath = path.join(baseDir, 'sample_input.txt');
const sampleOutputFilePath = path.join(baseDir, 'sample_output.txt'); // Used in Ex2
const compressedFilePath = path.join(baseDir, 'sample_output.txt.gz'); // Used in Ex3
const sampleOutputFromEventsPath = path.join(baseDir, 'sample_output_from_events_example.txt'); // New file for Ex1
const decompressedFilePathEx3 = path.join(baseDir, 'sample_decompressed.txt'); // For Ex3 decompression
const uppercaseOutputFilePathEx4 = path.join(baseDir, 'sample_uppercase_output.txt'); // New file for Ex4 output

// Create a dummy file for reading (if it doesn't exist, or ensure it has fresh content)
fs.writeFileSync(sampleFilePath, "Hello from streams!\nThis is line two.\nAnd a third line to make it a bit bigger.\nEnd of sample file.");

// --- Example 1: Reading from a Readable Stream (File) and Writing to a Writable Stream (demonstrating events & file output) ---
console.log("\n--- Example 1: Readable (File) to Writable (demonstrating events & file output) ---");

const readableFileStream_ex1 = fs.createReadStream(sampleFilePath, { encoding: 'utf8' });
// const writableConsoleStream = process.stdout; // process.stdout is a Writable stream // Kept for reference

console.log(`Attempting to read \`${sampleFilePath}\`. Event logs will show chunks. Also piping to \`${sampleOutputFromEventsPath}\` `);

readableFileStream_ex1.on('data', (chunk: Buffer | string) => {
    console.log(`READABLE_STREAM (data event - Ex1): Received chunk -> "${chunk.toString().replace(/\n/g, "\\n")}"`);
});

readableFileStream_ex1.on('end', () => {
    console.log("READABLE_STREAM (end event - Ex1): No more data to read from file.");
});

readableFileStream_ex1.on('error', (err: Error) => {
    console.error("READABLE_STREAM (error event - Ex1): Error reading file:", err);
});

// Also pipe to a file to demonstrate another way of consuming the stream
const writableToFileFromEvents = fs.createWriteStream(sampleOutputFromEventsPath);
// Note: Re-piping a stream that's already being consumed by .on('data') can be tricky.
// For this example, we'll create a new readable stream for the pipe for clarity,
// or ensure this pipe happens before .on('data') if an explicit order is needed.
// However, since readableFileStream_ex1 is fresh, this should be fine.
readableFileStream_ex1.pipe(writableToFileFromEvents);

writableToFileFromEvents.on('finish', () => {
    console.log(`WRITABLE_STREAM (finish event - Ex1): Data successfully piped to \`${sampleOutputFromEventsPath}\`.`);
});

writableToFileFromEvents.on('error', (err: Error) => {
    console.error(`WRITABLE_STREAM (error event - Ex1): Error writing to \`${sampleOutputFromEventsPath}\`:`, err);
});

// --- Example 2: Piping from Readable to Writable (File to File) ---
console.log("\n--- Example 2: Piping Readable (File) to Writable (File) ---");

const sourceStream_ex2 = fs.createReadStream(sampleFilePath);
const destinationStream_ex2 = fs.createWriteStream(sampleOutputFilePath);

console.log(`Piping from \`${sampleFilePath}\` to \`${sampleOutputFilePath}\`...`);

pipeline(sourceStream_ex2, destinationStream_ex2, (err?: Error | null) => {
    if (err) {
        console.error(`PIPELINE_ERROR (Ex2): Error piping to \`${sampleOutputFilePath}\`:`, err);
    } else {
        console.log(`PIPELINE_SUCCESS (Ex2): Data successfully piped to \`${sampleOutputFilePath}\`.`);
    }
});

// --- Example 3: Transform Stream (Gzipping and Gunzipping a file) ---
console.log("\n--- Example 3: Transform Stream (Gzipping and Gunzipping a file) ---");

const fileToCompress_ex3 = fs.createReadStream(sampleFilePath);
const gzipTransform_ex3 = createGzip();
const compressedOutput_ex3 = fs.createWriteStream(compressedFilePath);

console.log(`Compressing \`${sampleFilePath}\` to \`${compressedFilePath}\`...`);

pipeline(fileToCompress_ex3, gzipTransform_ex3, compressedOutput_ex3, (err?: Error | null) => {
    if (err) {
        console.error('PIPELINE_ERROR (Ex3 Gzip): Gzip compression pipeline failed.', err);
    } else {
        console.log(`PIPELINE_SUCCESS (Ex3 Gzip): Gzip compression successful. Output: \`${compressedFilePath}\``);

        // Now, let's decompress it to verify
        console.log(`\nAttempting to decompress \`${compressedFilePath}\` to \`${decompressedFilePathEx3}\`...`);
        const compressedInput_ex3 = fs.createReadStream(compressedFilePath);
        const gunzipTransform_ex3 = createGunzip();
        const decompressedOutput_ex3 = fs.createWriteStream(decompressedFilePathEx3);

        pipeline(compressedInput_ex3, gunzipTransform_ex3, decompressedOutput_ex3, (decompressErr?: Error | null) => {
            if (decompressErr) {
                console.error('PIPELINE_ERROR (Ex3 Gunzip): Gunzip decompression failed.', decompressErr);
            } else {
                console.log(`PIPELINE_SUCCESS (Ex3 Gunzip): Gunzip decompression successful. Output: \`${decompressedFilePathEx3}\``);
                // You can verify by reading both sampleFilePath and decompressedFilePathEx3 and comparing contents.
            }
        });
    }
});

// --- Example 4: Creating a Custom Transform Stream (Uppercasing to File) ---
console.log("\n--- Example 4: Custom Transform Stream (Uppercasing to File) ---");

class UppercaseTransform_ex4 extends Transform {
    _transform(chunk: Buffer, encoding: BufferEncoding, callback: (error?: Error | null, data?: Buffer | string) => void): void {
        try {
            const uppercasedChunk = chunk.toString().toUpperCase();
            // console.log(`CUSTOM_TRANSFORM (Ex4): Transforming chunk to uppercase.`); // Optional: can be verbose
            callback(null, uppercasedChunk);
        } catch (error) {
            callback(error as Error);
        }
    }
}

const readableForTransform_ex4 = fs.createReadStream(sampleFilePath, { encoding: 'utf8' });
const uppercaseTransformer_ex4 = new UppercaseTransform_ex4();
const writableToFileForTransform_ex4 = fs.createWriteStream(uppercaseOutputFilePathEx4);

console.log(`Piping file through custom UppercaseTransform_ex4 to \`${uppercaseOutputFilePathEx4}\`...`);

pipeline(readableForTransform_ex4, uppercaseTransformer_ex4, writableToFileForTransform_ex4, (err_ex4?: Error | null) => {
    if (err_ex4) {
        console.error(`PIPELINE_ERROR (Ex4 Uppercase): Failed to write to \`${uppercaseOutputFilePathEx4}\`.`, err_ex4);
    } else {
        console.log(`PIPELINE_SUCCESS (Ex4 Uppercase): Successfully transformed and wrote to \`${uppercaseOutputFilePathEx4}\`.`);
    }
});

// --- Backpressure ---
// When a Readable stream produces data faster than a Writable stream can consume it,
// data can buffer in memory. Backpressure is a mechanism where the Writable stream
// signals the Readable stream to pause producing data (`readable.pause()`) when its internal
// buffer is full, and resume (`readable.resume()`) when it's ready for more.
// The `pipe()` method handles backpressure automatically.
// If you are manually reading with `.on('data')` and writing with `.write()`, you need to manage backpressure yourself
// by checking the return value of `writable.write()` and listening for the `'drain'` event.
console.log("\n--- Backpressure (Conceptual) ---");
console.log("- `pipe()` handles backpressure automatically.");
console.log("- If manually using `readable.on('data')` and `writable.write()`, check `writable.write()` return value.");
console.log("  If it returns false, pause the readable stream and wait for the `'drain'` event on the writable stream.");

// --- Key Takeaways ---
// - Streams are powerful for handling large amounts of data efficiently.
// - Four types: Readable, Writable, Duplex, Transform.
// - `pipe()` is the easiest way to connect streams and handles backpressure.
// - `pipeline()` is a utility for piping multiple streams with better error handling.
// - Listen for events like `data`, `end`, `error`, `finish`, `drain` to manage stream lifecycle.
// - Custom Transform streams allow for on-the-fly data modification in a streaming fashion.

// Cleanup dummy files (optional, for tidiness after demo)
// Ensure this runs after all stream operations, possibly with a delay or a more robust mechanism
// For a simple script, a timeout might be okay, but for robust apps, use async/await with promises from stream events.
setTimeout(() => {
    try {
        console.log("\nAttempting to clean up sample files...");
        if(fs.existsSync(sampleFilePath)) fs.unlinkSync(sampleFilePath);
        if(fs.existsSync(sampleOutputFilePath)) fs.unlinkSync(sampleOutputFilePath);
        if(fs.existsSync(compressedFilePath)) fs.unlinkSync(compressedFilePath);
        if(fs.existsSync(sampleOutputFromEventsPath)) fs.unlinkSync(sampleOutputFromEventsPath);
        if(fs.existsSync(decompressedFilePathEx3)) fs.unlinkSync(decompressedFilePathEx3);
        if(fs.existsSync(uppercaseOutputFilePathEx4)) fs.unlinkSync(uppercaseOutputFilePathEx4);
        console.log("Cleaned up sample files (if they existed).");
    } catch (err) {
        console.error("Cleanup error:", err);
    }
}, 5000); // Increased delay to allow async operations to complete

/**
 * To compile and run:
 * 1. Ensure you have @types/node: npm install --save-dev @types/node
 * 2. Compile: tsc 3_streams.ts
 * 3. Run: node 3_streams.js
 * (If your tsconfig.json specifies an outDir, run `node <yourOutDir>/3_streams.js`)
 */