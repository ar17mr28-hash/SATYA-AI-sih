import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.database import engine, Base, SessionLocal
from .services.seed import seed_database
from .api import (
    auth, applications, documents, compliance, reviews, reports, analytics, notifications, demo, verification
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-seed on startup if needed
try:
    seed_database()
except Exception as e:
    print(f"Startup seed notice: {e}")

from .services.auth import validate_production_security_config

# Validate environment secrets at startup
validate_production_security_config()

from .middleware.security import SecurityHeadersMiddleware

app = FastAPI(
    title="VerifyAI API",
    description="Intelligent Document Authentication & Regulatory Compliance Platform - SIH 2026 (Problem Statement: SIH26261)",
    version="2.0.0"
)

# Enforce Security Headers and Payload Size limits
app.add_middleware(SecurityHeadersMiddleware)

# Environment-specific CORS policy (OWASP: Never combine wildcard origins with credentials)
env_name = os.getenv("ENVIRONMENT", "development").lower()
raw_origins = os.getenv("ALLOWED_ORIGINS", "")

if env_name == "production":
    if raw_origins:
        cors_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    else:
        cors_origins = ["https://verifyai.gov.in"]
else:
    cors_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    if raw_origins:
        cors_origins.extend([o.strip() for o in raw_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
app.include_router(verification.router, prefix="/api")

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
