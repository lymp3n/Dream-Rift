"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.api.routes import (
    character,
    combat,
    inventory,
    crafting,
    market,
    location,
    skills
)
from backend.src.api.routes import combat_enhanced

app = FastAPI(
    title="Dreamforge API",
    description="API for Dreamforge: Эхо Бездны MMORPG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(character.router, prefix="/api")
app.include_router(combat.router, prefix="/api")
app.include_router(combat_enhanced.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(crafting.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(location.router, prefix="/api")
app.include_router(skills.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Dreamforge: Эхо Бездны API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}

