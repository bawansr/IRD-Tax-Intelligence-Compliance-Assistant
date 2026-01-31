"""
Main entry point for the IRD Tax Assistant API.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router

# 1. Initialize the API Application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered assistant for Sri Lanka Inland Revenue Department documents.",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI endpoint
    redoc_url="/redoc"      # ReDoc endpoint
)

# 2. CORS Middleware (Crucial for Frontend Integration)
# This allows your React/Streamlit frontend to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # In production, replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],    # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],    # Allows all headers
)

# 3. Register Routes
# All endpoints in routes.py will be prefixed with /api/v1
app.include_router(router, prefix="/api/v1")

# 4. Root Endpoint (Health Check)
@app.get("/")
async def root():
    """
    Root endpoint to verify the server is running.
    """
    return {
        "message": "Welcome to the IRD Tax Assistant API",
        "status": "running",
        "documentation": "/docs",
        "health_check": "/api/v1/health"
    }

# 5. Server Execution
# This block runs when you execute 'python app/main.py' directly
if __name__ == "__main__":
    print(f"🚀 Starting server at http://{settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True  # Auto-restarts server when code changes
    )