/**
 * Performance Optimization & Profiling in Node.js
 * 
 * This tutorial covers:
 * - Identifying performance bottlenecks (CPU, memory)
 * - Using Node.js built-in profiler (--prof) and Chrome DevTools
 * - Memory leak detection and management
 * - Caching strategies
 */

// Import required modules
import * as fs from 'node:fs';
import * as crypto from 'node:crypto';
import * as http from 'node:http';

// -----------------------------------------------------------------
// 1. IDENTIFYING PERFORMANCE BOTTLENECKS
// -----------------------------------------------------------------

console.log('===== PERFORMANCE BOTTLENECK IDENTIFICATION =====');

// Example of a CPU-intensive operation
function cpuIntensiveTask() {
  console.log('Running CPU-intensive task...');
  
  console.time('hashingOperation');
  // Generate a large number of hashes (CPU intensive)
  for (let i = 0; i < 100000; i++) {
    crypto.createHash('sha256').update(`data-${i}`).digest('hex');
  }
  console.timeEnd('hashingOperation');
}

// Example of memory-intensive operation
function memoryIntensiveTask() {
  console.log('Running memory-intensive task...');
  
  console.time('memoryOperation');
  const largeArray: number[] = [];
  // Fill a large array (memory intensive)
  for (let i = 0; i < 1000000; i++) {
    largeArray.push(i);
  }
  console.timeEnd('memoryOperation');
  
  // Clean up to avoid memory leaks
  // (In real scenarios, you might not be able to clean up so easily)
  console.log(`Array size: ${largeArray.length}`);
  // Let the array be garbage collected
}

// Use console.time/timeEnd for basic performance measurement
cpuIntensiveTask();
memoryIntensiveTask();

// -----------------------------------------------------------------
// 2. USING BUILT-IN PROFILERS
// -----------------------------------------------------------------

console.log('\n===== PROFILING TECHNIQUES =====');

/**
 * Node.js has built-in profiling capabilities:
 * 
 * 1. CPU Profiling with --prof flag:
 *    Run: node --prof your-script.js
 *    Then process the isolate log with:
 *    node --prof-process isolate-0xnnnnnnnnnnnn-v8.log > processed.txt
 * 
 * 2. Using Inspector Protocol and Chrome DevTools:
 *    Run: node --inspect your-script.js
 *    Then open Chrome and navigate to chrome://inspect
 * 
 * Below is an example function we could profile:
 */

function functionToProfile() {
  // CPU-intensive work
  let result = 0;
  for (let i = 0; i < 1000000; i++) {
    result += Math.sqrt(i);
  }
  return result;
}

console.log('Function result:', functionToProfile());
console.log('To profile this function:');
console.log('1. Run: node --prof 9_performance_optimization.js');
console.log('2. Process log: node --prof-process isolate-0xnnnnnnnnnnnn-v8.log > profile.txt');
console.log('3. Alternatively use: node --inspect 9_performance_optimization.js');

// -----------------------------------------------------------------
// 3. MEMORY LEAK DETECTION
// -----------------------------------------------------------------

console.log('\n===== MEMORY LEAK DETECTION =====');

/**
 * Common causes of memory leaks in Node.js:
 * 1. Global variables
 * 2. Closures capturing large variables
 * 3. Event listeners not being removed
 * 4. Improper handling of timers (setTimeout/setInterval)
 * 5. Circular references that can't be garbage collected
 */

// Example of a potential memory leak with closures and timers
function demonstrateMemoryLeak() {
  const potentialLeak = {
    bigData: new Array(10000).fill('potential memory leak data')
  };
  
  // This holds a reference to potentialLeak, preventing garbage collection
  const timer = setInterval(() => {
    console.log(`Referencing large object: ${potentialLeak.bigData.length} items`);
    // In a real app, this timer might never be cleared
  }, 5000);
  
  // To prevent the actual leak in this example, we'll clear the interval
  console.log('In real applications, you would need to:');
  console.log('1. Clear timers when components are destroyed');
  console.log('2. Remove event listeners when they\'re no longer needed');
  console.log('3. Be cautious with closures capturing large objects');
  
  // Let's simulate fixing the leak
  setTimeout(() => {
    clearInterval(timer);
    console.log('Timer cleared, allowing garbage collection');
  }, 5500);
}

demonstrateMemoryLeak();

// Track memory usage
function logMemoryUsage() {
  const memoryUsage = process.memoryUsage();
  console.log({
    rss: `${Math.round(memoryUsage.rss / 1024 / 1024)} MB`, // Resident Set Size - total memory allocated
    heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)} MB`, // V8's memory usage
    heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)} MB`, // Actual memory used
    external: `${Math.round(memoryUsage.external / 1024 / 1024)} MB` // Memory used by C++ objects bound to JS
  });
}

// Log memory usage periodically
console.log('\nTracking memory usage:');
logMemoryUsage();
setTimeout(logMemoryUsage, 6000); // After our memory leak simulation

// -----------------------------------------------------------------
// 4. CACHING STRATEGIES
// -----------------------------------------------------------------

console.log('\n===== CACHING STRATEGIES =====');

// Simple in-memory cache implementation
class SimpleCache<T> {
  private cache: Map<string, { data: T, expiresAt: number }>;
  
  constructor() {
    this.cache = new Map();
  }
  
  get(key: string): T | null {
    const item = this.cache.get(key);
    
    // Check if item exists and is not expired
    if (item && item.expiresAt > Date.now()) {
      console.log(`Cache hit for key: ${key}`);
      return item.data;
    }
    
    // Remove expired item if it exists
    if (item) {
      console.log(`Cache expired for key: ${key}`);
      this.cache.delete(key);
    } else {
      console.log(`Cache miss for key: ${key}`);
    }
    
    return null;
  }
  
  set(key: string, data: T, ttlMs: number): void {
    console.log(`Setting cache for key: ${key} with TTL: ${ttlMs}ms`);
    this.cache.set(key, {
      data,
      expiresAt: Date.now() + ttlMs
    });
  }
  
  // For demonstration: get cache stats
  getStats(): { size: number, keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

// Define an interface for our data structure
interface CachedData {
  id: string;
  name: string;
  data: string;
  timestamp: number;
}

// Simulated expensive data retrieval function
function fetchDataExpensive(id: string): Promise<CachedData> {
  console.log(`Performing expensive data fetch for id: ${id}`);
  return new Promise(resolve => {
    // Simulate network or computation delay
    setTimeout(() => {
      resolve({
        id,
        name: `Item ${id}`,
        data: `Large data for ${id}...`,
        timestamp: Date.now()
      });
    }, 1000);
  });
}

// Create our cache
const dataCache = new SimpleCache<CachedData>();

// Function that uses the cache
async function fetchDataWithCache(id: string): Promise<CachedData> {
  // Try to get from cache first
  const cachedData = dataCache.get(id);
  if (cachedData) {
    return cachedData;
  }
  
  // If not in cache, fetch the expensive way
  const data = await fetchDataExpensive(id);
  
  // Store in cache for 30 seconds
  dataCache.set(id, data, 30 * 1000);
  
  return data;
}

// Demo of the caching system
async function demonstrateCaching() {
  console.log('First request for item "123" - should be a cache miss:');
  await fetchDataWithCache('123');
  
  console.log('\nSecond request for item "123" - should be a cache hit:');
  await fetchDataWithCache('123');
  
  console.log('\nRequest for new item "456" - should be a cache miss:');
  await fetchDataWithCache('456');
  
  console.log('\nCache stats:', dataCache.getStats());
  
  console.log('\nWaiting for cache to expire...');
  await new Promise(resolve => setTimeout(resolve, 31 * 1000));
  
  console.log('\nAfter expiration, request for "123" - should be a cache miss:');
  await fetchDataWithCache('123');
}

// Run the caching demonstration (commented to avoid long execution)
// demonstrateCaching();
console.log('To run the full caching demo, uncomment the demonstrateCaching() call');

// -----------------------------------------------------------------
// PERFORMANCE BEST PRACTICES SUMMARY
// -----------------------------------------------------------------

console.log('\n===== PERFORMANCE BEST PRACTICES =====');
console.log('1. Use asynchronous APIs whenever possible');
console.log('2. Implement appropriate caching strategies for expensive operations');
console.log('3. Optimize your code for the V8 engine (use modern JS features)');
console.log('4. Leverage worker threads for CPU-intensive tasks');
console.log('5. Implement proper error handling to prevent memory leaks');
console.log('6. Profile your application regularly to catch performance issues early');
console.log('7. Use streaming for large data processing');
console.log('8. Optimize database queries and prefer pagination');
console.log('9. Implement connection pooling for databases and external services');
console.log('10. Consider using PM2 or other process managers for cluster mode');

/**
 * To run this file:
 * 
 * 1. Compile the TypeScript:
 *    tsc 9_performance_optimization.ts
 * 
 * 2. Run the JavaScript:
 *    node 9_performance_optimization.js
 * 
 * 3. For CPU profiling:
 *    node --prof 9_performance_optimization.js
 *    node --prof-process isolate-0xnnnnnnnnnnnn-v8.log > profile.txt
 * 
 * 4. For memory profiling:
 *    node --inspect 9_performance_optimization.js
 *    (Then open Chrome DevTools)
 */ 