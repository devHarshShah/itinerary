from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from typing import List
from contextlib import asynccontextmanager

# Import database functions
from database import get_db  # Removed init_db
# Import routers
from auth.router import router as auth_router
from itinerary.router import router as itinerary_router

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Starting up the API server...")
    # init_db() removed - we'll use Alembic for migrations instead
    
    yield  # This is where the app runs
    
    # Code to run on shutdown
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

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Itinerary API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Database dependency
def get_db_session():
    with get_db() as db:
        yield db

# Run the application directly when script is executed
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)