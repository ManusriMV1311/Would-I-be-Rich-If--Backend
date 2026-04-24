from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health
from app.routers import simulation

app = FastAPI()

# ✅ ADD THIS BLOCK (CORS FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://would-i-be-rich-if.vercel.app", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api")
app.include_router(simulation.router, prefix="/api")