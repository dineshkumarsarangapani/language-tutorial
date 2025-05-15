# 3. Uvicorn: HTTPS/SSL and HTTP/2

# Serving your application over HTTPS is crucial for security in production.
# Uvicorn has built-in support for SSL/TLS termination.
# HTTP/2 can also offer performance benefits.

# We'll use `uvicorn_advanced_tutorial.sample_asgi_app:app` for command-line examples.

print("--- 1. Configuring SSL/TLS directly with Uvicorn ---")
print("Uvicorn can terminate SSL/TLS connections if you provide it with a key file and a certificate file.")
print("This is suitable for development or simple deployments, but for production, a reverse proxy is often preferred.")

print("\n# Prerequisites for SSL:")
print("- You need an SSL key file (e.g., `key.pem`) and a certificate file (e.g., `cert.pem`).")
print("- For local development, you can generate self-signed certificates using tools like OpenSSL or `mkcert`.")
print("  Example using mkcert (install mkcert first):")
print("    # mkcert localhost 127.0.0.1 ::1")
print("    # This will create `localhost+2.pem` (certificate) and `localhost+2-key.pem` (key).")

print("\n# Example: Running Uvicorn with SSL (run from project root, assuming key/cert files are present):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8001 --ssl-keyfile ./localhost+2-key.pem --ssl-certfile ./localhost+2.pem")
print("  # Replace `./localhost+2-key.pem` and `./localhost+2.pem` with your actual file paths.")
print("  # Your browser will likely show a warning for self-signed certificates.")

print("\nOther SSL-related options:")
print("- `--ssl-keyfile-password TEXT`: Password for the SSL key file, if encrypted.")
print("- `--ssl-version INTEGER`: SSL version to use (e.g., `2` for TLSv1.2). See Python's `ssl` module constants.")
print("- `--ssl-ciphers TEXT`: Ciphers to use (e.g., 'HIGH:!aNULL:!eNULL:!EXPORT:!SSLV2:!MD5:!RC4').")
print("- `--ssl-ca-certs TEXT`: Path to a CA certificate bundle for client certificate validation (mTLS).")
print("- `--ssl-cert-reqs INTEGER`: Whether client certificate is required (0=none, 1=optional, 2=required).")

print("\nUsing Environment Variables for SSL:")
print("# export UVICORN_SSL_KEYFILE=./localhost+2-key.pem")
print("# export UVICORN_SSL_CERTFILE=./localhost+2.pem")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8001")


print("\n\n--- 2. HTTP/2 with Uvicorn ---")
print("Uvicorn supports HTTP/2 if the underlying HTTP toolkit and Python's SSL module capabilities allow.")
print("- To enable HTTP/2, you typically need to be serving over HTTPS.")
print("- The `h2` library (`pip install h2`) is required for HTTP/2 support by some HTTP toolkits Uvicorn might use (like `httptools`).")
print("- Uvicorn with `httptools` and `uvloop` often provides good HTTP/2 support.")

print("\n# Example: Running with potential for HTTP/2 (requires SSL and appropriate libraries):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8001 --ssl-keyfile ./localhost+2-key.pem --ssl-certfile ./localhost+2.pem --http httptools")
print("  # Browsers supporting HTTP/2 (most modern ones) will attempt to negotiate it over HTTPS.")
print("  # You can verify using browser developer tools (Network tab, look for protocol h2).")

print("\nConsiderations for HTTP/2:")
print("- Performance benefits: Multiplexing, header compression, server push (though server push is less commonly implemented by ASGI servers directly).")
print("- Complexity: HTTP/2 is more complex than HTTP/1.1.")
print("- ALPN (Application-Layer Protocol Negotiation): Browsers use ALPN over TLS to negotiate HTTP/2. " \
      "This needs to be supported by your Python SSL module and OpenSSL version.")


print("\n\n--- 3. Using a Reverse Proxy (e.g., Nginx, Traefik, Caddy) for SSL/TLS Termination ---")
print("In production, it's a very common and often recommended practice to terminate SSL/TLS at a reverse proxy layer rather than directly in Uvicorn.")

print("\nHow it works:")
print("1. Client connects to Reverse Proxy (e.g., Nginx) via HTTPS (port 443)." )
print("2. Reverse Proxy handles the SSL/TLS handshake, decrypts the request.")
print("3. Reverse Proxy forwards the decrypted HTTP request to Uvicorn (running on a local, non-HTTPS port, e.g., 8000)." )
print("4. Uvicorn processes the request and sends an HTTP response back to the Reverse Proxy.")
print("5. Reverse Proxy encrypts the response and sends it back to the client over HTTPS.")

print("\nBenefits:")
print("- Centralized SSL Management: Manage all your SSL certificates in one place (the proxy)." )
print("- Security: The proxy can handle SSL vulnerabilities and updates independently of your application server.")
print("- Performance: Dedicated proxies are often highly optimized for SSL/TLS operations.")
print("- Load Balancing: Proxies can also act as load balancers if you have multiple Uvicorn instances.")
print("- Static File Serving: Proxies are efficient at serving static files.")
print("- Other Features: Request/response manipulation, caching, rate limiting, etc.")

print("\nUvicorn configuration when behind a reverse proxy:")
print("- Run Uvicorn on HTTP (e.g., `uvicorn myapp:app --host 127.0.0.1 --port 8000`).")
print("- Configure the reverse proxy to forward requests to Uvicorn's host and port.")
print("- Ensure the proxy sets appropriate headers like `X-Forwarded-For` and `X-Forwarded-Proto`, " \
      "and configure Uvicorn or your ASGI app to trust these headers (e.g., using Uvicorn's `--proxy-headers` flag or FastAPI's `ProxyHeadersMiddleware`).")

print("\n# Example: Uvicorn with --proxy-headers behind a reverse proxy:")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8000 --proxy-headers --forwarded-allow-ips=\'127.0.0.1,172.17.0.1\'")
print("  # `forwarded-allow-ips` should list your trusted proxy IP(s). Use `*` with caution.")

print("\n--- Key Takeaways for HTTPS/SSL & HTTP/2 ---")
print("- Uvicorn can serve HTTPS directly, useful for development or simple setups.")
print("- For production, using a reverse proxy for SSL termination is generally more robust and flexible.")
print("- HTTP/2 is often negotiated automatically over HTTPS if supported by Uvicorn's HTTP toolkit and client.")
print("- Always prioritize security: keep certificates updated and use strong SSL configurations.") 