/**
 * Security Best Practices in Node.js Applications
 * 
 * This tutorial covers:
 * - Common vulnerabilities (XSS, SQL Injection, CSRF, etc.)
 * - Input validation and sanitization
 * - Managing dependencies and security updates
 * - Securely handling secrets and environment variables
 */

// Import required modules
import * as crypto from 'node:crypto';
import type * as http from 'node:http';
import type * as fs from 'node:fs';
import { URL } from 'node:url';

// -----------------------------------------------------------------
// 1. COMMON VULNERABILITIES AND MITIGATIONS
// -----------------------------------------------------------------

console.log('===== COMMON VULNERABILITIES AND MITIGATIONS =====');

/**
 * 1. Cross-Site Scripting (XSS)
 * 
 * XSS occurs when untrusted data is included in a web page
 * without proper validation or escaping, allowing attackers to
 * inject client-side scripts.
 */

// Vulnerable example (DO NOT USE IN PRODUCTION):
function vulnerableXSSExample(userInput: string): string {
  // DANGEROUS: Directly including user input in HTML
  return `<div>${userInput}</div>`;
}

// Safer approach:
function sanitizedXSSExample(userInput: string): string {
  // Escape HTML special characters
  const escaped = userInput
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
  
  return `<div>${escaped}</div>`;
}

// Demonstration
const maliciousInput = '<script>alert("XSS Attack!")</script>';
console.log('Vulnerable XSS output:', vulnerableXSSExample(maliciousInput));
console.log('Sanitized XSS output:', sanitizedXSSExample(maliciousInput));

/**
 * 2. SQL Injection
 * 
 * SQL Injection occurs when untrusted data is used to construct
 * SQL queries without proper parameterization.
 */

// Vulnerable example (DO NOT USE IN PRODUCTION):
function vulnerableSQLExample(username: string): string {
  // DANGEROUS: String concatenation in SQL queries
  return `SELECT * FROM users WHERE username = '${username}'`;
}

// Safer approach using parameterized queries:
// In practice, you would use your database driver's parameterized query support
function safeSQLExample(username: string): string {
  // This is a simplified example - in real code, you'd use your DB library's parameterization
  return {
    text: 'SELECT * FROM users WHERE username = $1',
    values: [username]
  } as unknown as string; // Type casting just for demonstration
}

// Demonstration
const maliciousSQLInput = "admin' OR 1=1--";
console.log('Vulnerable SQL query:', vulnerableSQLExample(maliciousSQLInput));
console.log('Safe parameterized query:', safeSQLExample(maliciousSQLInput));

/**
 * 3. Cross-Site Request Forgery (CSRF)
 * 
 * CSRF tricks the victim into submitting a malicious request.
 * Requires anti-CSRF tokens or SameSite cookies.
 */

console.log('\nCSRF Protection:');
console.log('1. Use anti-CSRF tokens for state-changing operations');
console.log('2. Set SameSite attribute on cookies');
console.log('3. Verify Origin/Referer headers when processing requests');
console.log('4. Use proper CORS configuration');

// -----------------------------------------------------------------
// 2. INPUT VALIDATION AND SANITIZATION
// -----------------------------------------------------------------

console.log('\n===== INPUT VALIDATION AND SANITIZATION =====');

/**
 * Always validate and sanitize all user input:
 * - Validate format, type, length, range, etc.
 * - Use schema validation libraries (like Joi, Yup, Zod, etc.)
 * - Sanitize input where needed
 */

// Simple validation examples
// In real apps, use a validation library like Joi, Yup, Zod, etc.

// Example validator for an email
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Example validator for a URL
function validateURL(urlString: string): boolean {
  try {
    // Using built-in URL parser to validate
    const url = new URL(urlString);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

// Demonstration
console.log('Email validation:');
console.log('Valid email:', validateEmail('user@example.com'));
console.log('Invalid email:', validateEmail('not-an-email'));

console.log('\nURL validation:');
console.log('Valid URL:', validateURL('https://example.com'));
console.log('Invalid URL:', validateURL('not-a-url'));

// -----------------------------------------------------------------
// 3. MANAGING DEPENDENCIES AND SECURITY UPDATES
// -----------------------------------------------------------------

console.log('\n===== MANAGING DEPENDENCIES AND SECURITY UPDATES =====');

/**
 * Dependency management best practices:
 * 1. Regularly update dependencies
 * 2. Use npm audit to find vulnerabilities
 * 3. Pin dependency versions
 * 4. Use lockfiles (package-lock.json, yarn.lock)
 * 5. Consider using tools like Snyk or Dependabot
 */

console.log('To check for vulnerabilities in your dependencies:');
console.log('$ npm audit');
console.log('$ npm audit fix');

console.log('\nTo update packages to non-breaking versions:');
console.log('$ npm update');

console.log('\nTo check outdated packages:');
console.log('$ npm outdated');

// -----------------------------------------------------------------
// 4. SECURELY HANDLING SECRETS AND ENVIRONMENT VARIABLES
// -----------------------------------------------------------------

console.log('\n===== SECURELY HANDLING SECRETS AND ENVIRONMENT VARIABLES =====');

/**
 * Best practices for handling secrets:
 * 1. Never hard-code secrets in source code
 * 2. Use environment variables or a secret management service
 * 3. Don't log sensitive information
 * 4. Be careful about including secrets in error messages
 */

// Example of loading environment variables
function getConfig() {
  // In a real application, use a library like dotenv to load from .env files
  return {
    dbConnectionString: process.env.DB_CONNECTION_STRING || 'default-connection-string',
    apiKey: process.env.API_KEY || 'default-api-key',
    // NEVER provide real default values for secrets in production code
  };
}

// Example of creating a secure random token
function generateSecureToken(length = 32): string {
  return crypto.randomBytes(length).toString('hex');
}

console.log('Secure random token:', generateSecureToken());

// -----------------------------------------------------------------
// 5. HASHING AND ENCRYPTION
// -----------------------------------------------------------------

console.log('\n===== HASHING AND ENCRYPTION =====');

/**
 * Password hashing best practices:
 * 1. Always use a strong, specialized password hashing function
 * 2. Include a unique salt for each user
 * 3. Use sufficient iterations/work factor
 */

// Example of secure password hashing (using Node's crypto module)
// In real applications, use a specialized library like bcrypt, argon2, or scrypt
function hashPassword(password: string): { hash: string, salt: string } {
  // Generate a random salt
  const salt = crypto.randomBytes(16).toString('hex');
  
  // Hash the password with the salt using PBKDF2
  // In a real application, use a higher iterations count (at least 10000)
  const hash = crypto.pbkdf2Sync(
    password, 
    salt, 
    1000, // iterations (use higher in production)
    64,   // key length
    'sha512'
  ).toString('hex');
  
  return { hash, salt };
}

// Verify a password against a stored hash
function verifyPassword(password: string, storedHash: string, storedSalt: string): boolean {
  const hash = crypto.pbkdf2Sync(
    password,
    storedSalt,
    1000, // Must match the iterations used during hashing
    64,   // key length
    'sha512'
  ).toString('hex');
  
  return hash === storedHash;
}

// Demonstration
const password = 'secure-user-password';
const { hash, salt } = hashPassword(password);

console.log('Password hashing:');
console.log('Original password:', password);
console.log('Generated hash:', hash);
console.log('Generated salt:', salt);

console.log('\nPassword verification:');
console.log('Correct password:', verifyPassword(password, hash, salt));
console.log('Incorrect password:', verifyPassword('wrong-password', hash, salt));

// -----------------------------------------------------------------
// 6. SECURE HTTP HEADERS
// -----------------------------------------------------------------

console.log('\n===== SECURE HTTP HEADERS =====');

/**
 * Important security headers to include in HTTP responses:
 * 1. Content-Security-Policy (CSP)
 * 2. X-Content-Type-Options
 * 3. X-Frame-Options
 * 4. Strict-Transport-Security (HSTS)
 * 5. X-XSS-Protection
 */

// Example of setting secure headers in an HTTP server
function setSecureHeaders(res: http.ServerResponse): void {
  // Content Security Policy - restricts which resources can be loaded
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self'; object-src 'none'"
  );
  
  // Prevents browsers from MIME-sniffing a response away from the declared content-type
  res.setHeader('X-Content-Type-Options', 'nosniff');
  
  // Prevents your page from being displayed in an iframe
  res.setHeader('X-Frame-Options', 'DENY');
  
  // HTTP Strict Transport Security - forces HTTPS
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  
  // Additional protection against XSS attacks
  res.setHeader('X-XSS-Protection', '1; mode=block');
}

// Example minimal server with secure headers
/*
const secureServer = http.createServer((req, res) => {
  // Set security headers
  setSecureHeaders(res);
  
  // Handle request
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Secure Node.js Server');
});

// secureServer.listen(3000, () => {
//   console.log('Secure server running on port 3000');
// });
*/

// -----------------------------------------------------------------
// SECURITY BEST PRACTICES SUMMARY
// -----------------------------------------------------------------

console.log('\n===== SECURITY BEST PRACTICES SUMMARY =====');
console.log('1. Validate and sanitize all user input');
console.log('2. Use parameterized queries for database operations');
console.log('3. Keep dependencies updated and regularly audit them');
console.log('4. Store secrets securely (environment variables, secret managers)');
console.log('5. Implement proper authentication and authorization');
console.log('6. Use HTTPS for all production traffic');
console.log('7. Set secure HTTP headers');
console.log('8. Hash passwords using strong algorithms (bcrypt, argon2)');
console.log('9. Implement proper session management');
console.log('10. Define and use a Content Security Policy');
console.log('11. Employ the principle of least privilege');
console.log('12. Implement rate limiting to prevent brute-force attacks');

/**
 * To run this file:
 * 
 * 1. Compile the TypeScript:
 *    tsc 10_security_best_practices.ts
 * 
 * 2. Run the JavaScript:
 *    node 10_security_best_practices.js
 */ 