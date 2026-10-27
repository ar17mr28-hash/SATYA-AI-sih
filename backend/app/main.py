import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.database import engine, Base, SessionLocal
from .services.seed import seed_database
from .api import (
    auth, applications, documents, compliance, reviews, reports, analytics, notifications, demo
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-seed on startup if needed
try:
    seed_database()
except Exception as e:
    print(f"Startup seed notice: {e}")

app = FastAPI(
    title="VerifyAI API",
    description="Intelligent Document Authentication & Regulatory Compliance Platform - SIH 2026 (Problem Statement: SIH26261)",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(demo.router, prefix="/api")

from fastapi.staticfiles import StaticFiles

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "verifyai-backend"}

# Mount Frontend Static Build if present
dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "platform": "VerifyAI",
            "subtitle": "Intelligent Document Authentication & Regulatory Compliance Platform",
            "problem_statement": "SIH26261",
            "organization": "All India Council for Technical Education (AICTE)",
            "version": "1.0.0",
            "status": "online",
            "docs_url": "/docs"
        }
