from fastapi import FastAPI
from .router import router

# Re-export the router for use in the main application
# No need to reference router.router since router is already the APIRouter object