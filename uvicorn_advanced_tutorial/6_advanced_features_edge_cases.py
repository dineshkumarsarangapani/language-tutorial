# 6. Uvicorn: Advanced Features & Edge Cases (Conceptual)

# This section covers some of Uvicorn's more advanced command-line options and deployment
# considerations that might be relevant in specific scenarios.

# We'll use `uvicorn_advanced_tutorial.sample_asgi_app:app` conceptually for command-line examples.

print("--- 1. Event Loop Implementation (`--loop`) ---")
print("Uvicorn can use different event loop implementations. The primary ones are:")
print("- `asyncio`: The default Python standard library event loop.")
print("- `uvloop`: A fast, drop-in replacement for the asyncio event loop, built on libuv (the same library Node.js uses). " \
      "It often provides significant performance improvements, especially for I/O-bound applications.")

print("\n# Installation for uvloop:")
print("# pip install uvloop")

print("\n# How Uvicorn chooses the loop:")
print("- If `uvloop` is installed, Uvicorn will typically use it by default.")
print("- You can explicitly specify the loop using the `--loop` option:")

print("\n# Example: Explicitly using asyncio loop (run from project root):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8000 --loop asyncio")

print("\n# Example: Explicitly using uvloop (if installed):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8001 --loop uvloop")

print("\n# Example: Auto-detection (uvloop will be preferred if installed):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8002 --loop auto")

print("\nConsiderations for `--loop`:")
print("- Performance: `uvloop` is generally recommended for production if your platform supports it (Linux, macOS).\n" \
      "  Windows support for uvloop can be more limited or require WSL.")
print("- Compatibility: Ensure `uvloop` is compatible with all other asyncio libraries you are using.")


print("\n\n--- 2. HTTP Protocol Implementation (`--http`) ---")
print("Uvicorn uses HTTP protocol parsing libraries to handle raw HTTP requests.")
print("- `httptools`: A fast HTTP parser written in C, often providing better performance.\n" \
      "  It's also used by `uvloop`.")
print("- `h11`: A pure-Python HTTP/1.1 implementation, more portable but potentially slower than `httptools`.")

print("\n# Installation for httptools:")
print("# pip install httptools")

print("\n# How Uvicorn chooses the HTTP toolkit:")
print("- If `httptools` is installed, Uvicorn usually prefers it.")
print("- You can explicitly specify the HTTP toolkit using the `--http` option:")

print("\n# Example: Explicitly using h11 (run from project root):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8000 --http h11")

print("\n# Example: Explicitly using httptools (if installed):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8001 --http httptools")

print("\n# Example: Auto-detection (httptools preferred if installed):")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8002 --http auto")

print("\n`uvicorn[standard]` (`pip install uvicorn[standard]`) installs Uvicorn with `uvloop` and `httptools`,\n" \
      "  which is generally recommended for performance on supported platforms.")


print("\n\n--- 3. WebSockets Proxying Considerations ---")
print("If Uvicorn is running behind a reverse proxy (like Nginx) that also handles WebSockets:")
print("- Ensure the reverse proxy is correctly configured to upgrade WebSocket connections and pass them through.\n" \
      "  This involves setting headers like `Upgrade` and `Connection`.")
print("- Nginx configuration for WebSockets often includes:")
print("  ```nginx")
print("  location /ws {")
print("      proxy_pass http://127.0.0.1:8000; # Your Uvicorn backend")
print("      proxy_http_version 1.1;")
print("      proxy_set_header Upgrade $http_upgrade;")
print("      proxy_set_header Connection \"Upgrade\";")
print("      proxy_set_header Host $host;")
print("      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;")
print("      proxy_set_header X-Forwarded-Proto $scheme;")
print("  }")
print("  ```")
print("- Uvicorn's `--ws` option (e.g., `auto`, `none`, `wsproto`, `websockets`) controls which WebSocket implementation Uvicorn uses.\n" \
      "  `auto` is default and usually works well. `wsproto` is often preferred if available.")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --ws wsproto")
print("- If you experience issues with WebSockets through a proxy, check proxy timeouts and buffer settings.")


print("\n\n--- 4. Unix Domain Sockets (`--uds`) ---")
print("Instead of binding to a TCP host and port, Uvicorn can listen on a Unix domain socket.")
print("This is useful for inter-process communication on the same machine, often when Uvicorn is run behind a reverse proxy like Nginx on the same host.")
print("- Potentially slightly faster than TCP loopback due to less network stack overhead.")
print("- Socket file is created on the filesystem.")

print("\n# Example: Running Uvicorn with a Unix domain socket:")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --uds /tmp/uvicorn_app.sock")

print("\n# Nginx configuration to proxy to a Unix domain socket:")
nginx_uds_config_example = """
  ```nginx
  upstream uvicorn_backend {
      server unix:/tmp/uvicorn_app.sock;
  }
  server {
      listen 80;
      # ... other server config ...
      location / {
          proxy_pass http://uvicorn_backend;
          # ... other proxy settings ...
      }
  }
  ```
"""
print(nginx_uds_config_example)
print("- Ensure Uvicorn process has write permissions for the socket path and Nginx has read/write permissions.")


print("\n\n--- 5. File Descriptor Passing / Socket Activation (Advanced) ---")
print("This is a more advanced deployment technique, often used with systemd socket activation on Linux.")
print("- Systemd (or another init system) can create the listening socket(s) before Uvicorn starts.")
print("- Uvicorn is then started and passed the file descriptor(s) of these pre-opened sockets.")
print("- Benefits: Enables socket-based activation (Uvicorn only starts when a connection arrives on the socket),\n" \
      "  facilitates non-privileged Uvicorn processes using privileged ports (ports < 1024), and can help with zero-downtime restarts if managed carefully by the init system.")

print("\n# Uvicorn CLI option: `--fd <integer>`")
print("# Example (conceptual, depends on systemd or similar setup):")
print("# Assume systemd has opened a socket and passed its FD as, e.g., FD 3 (standard for socket activation often starts at 3)")
print("# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --fd 3")

print("\nWhen using Gunicorn with Uvicorn workers, Gunicorn typically handles socket creation and passes it to Uvicorn workers, abstracting some of this away.")


print("\n--- Key Takeaways for Advanced Features & Edge Cases ---")
print("- `--loop uvloop` and `--http httptools` (often via `uvicorn[standard]`) can provide significant performance boosts.")
print("- For WebSockets behind a proxy, ensure the proxy is correctly configured for WebSocket pass-through.")
print("- Unix Domain Sockets (`--uds`) offer an alternative to TCP for local inter-process communication with a reverse proxy.")
print("- File Descriptor Passing (`--fd`) is an advanced technique for integration with init systems like systemd.")
print("- Always consult the official Uvicorn documentation for the most up-to-date and detailed information on these features.") 