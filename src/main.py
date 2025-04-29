from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import sys
import os
from typing import List
from pathlib import Path
from contextlib import asynccontextmanager

# Add the parent directory to the sys.path if not already there
# This allows the app to run both with `python -m src.main` and directly with uvicorn main:app
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import database functions - use absolute imports to work in all contexts
try:
    # Try direct imports first (this works when running with "uvicorn main:app")
    from database import get_db
    from auth.router import router as auth_router
    from itinerary.router import router as itinerary_router
    from destination.router import router as destination_router
    from accommodation.router import router as accommodation_router
    from activity.router import router as activity_router
    from transfer.router import router as transfer_router
    from mcp.server import router as mcp_router
except ImportError:
    # If direct imports fail, try with src prefix
    # This works when running with "python -m src.main" or from Docker
    from src.database import get_db
    from src.auth.router import router as auth_router
    from src.itinerary.router import router as itinerary_router
    from src.destination.router import router as destination_router
    from src.accommodation.router import router as accommodation_router
    from src.activity.router import router as activity_router
    from src.transfer.router import router as transfer_router
    from src.mcp.server import router as mcp_router

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Starting up the API server...")
    
    yield  # This is where the app runs
    
    print("Shutting down the API server...")

# Create FastAPI app instance with lifespan
app = FastAPI(
    title="Itinerary API",
    description="API for managing travel itineraries",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth_router)
app.include_router(itinerary_router)
app.include_router(destination_router)
app.include_router(accommodation_router)
app.include_router(activity_router)
app.include_router(transfer_router)
app.include_router(mcp_router)  # Include the MCP router

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Itinerary API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the application directly when script is executed
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)