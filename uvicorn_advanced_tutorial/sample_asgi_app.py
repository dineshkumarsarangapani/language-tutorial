# sample_asgi_app.py

from fastapi import FastAPI

app = FastAPI(title="Sample ASGI App for Uvicorn Testing")

@app.get("/")
async def read_root():
    return {"message": "Hello from Sample ASGI App!"}

@app.get("/info")
async def app_info():
    return {"app_name": app.title, "version": "1.0.0"}

# This file can be served by Uvicorn, e.g.:
# uvicorn uvicorn_advanced_tutorial.sample_asgi_app:app --port 8001 