"""
MediMitra AI — FastAPI Main Application Entrypoint.
HacXLerate 2026 | Round 1 | Team TEKSQUADS
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import engine, SessionLocal, Base, run_lightweight_migrations
from backend.app.data.demo_samples import seed_demo_data
from backend.app.routers import (
    health, documents, analysis, comparison,
    doctor_prep, medications, fhir, voice, patients
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MediMitra")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    logger.info("Initializing MediMitra AI SQLite database...")
    Base.metadata.create_all(bind=engine)
    run_lightweight_migrations()
    
    # Auto-seed synthetic demonstration records
    db = SessionLocal()
    try:
        seed_demo_data(db)
        logger.info("Pre-seeded synthetic healthcare demo records successfully.")
    except Exception as e:
        logger.error(f"Error seeding demo records: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title="MediMitra AI — Personal Health Copilot API",
    description="Backend API for medical record intelligence, OCR, plain-language and Telugu explanations, change detection, and ABDM/FHIR interoperability.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler: prevents internal paths or stack traces leaking
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An internal processing error occurred.",
            "detail": "Please check your document formatting or retry the operation.",
            "safe_code": "INTERNAL_SERVER_ERROR"
        }
    )

# Register API Routers
app.include_router(health.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(comparison.router, prefix="/api")
app.include_router(doctor_prep.router, prefix="/api")
app.include_router(medications.router, prefix="/api")
app.include_router(fhir.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(patients.router, prefix="/api")

from pathlib import Path
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse

STANDALONE_HTML = Path(__file__).resolve().parent.parent.parent / "frontend" / "standalone.html"

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    accept_header = request.headers.get("accept", "")
    if "application/json" in accept_header and "text/html" not in accept_header:
        return JSONResponse({
            "project": "MediMitra AI",
            "tagline": "Your Health Records. Clearly Understood.",
            "status": "online",
            "docs_url": "/docs",
            "app_url": "/app",
            "team": "TEKSQUADS",
            "hackathon": "HacXLerate 2026"
        })
    if STANDALONE_HTML.exists():
        return FileResponse(STANDALONE_HTML)
    return HTMLResponse("<h1>MediMitra AI — Online</h1>")

@app.get("/app", response_class=HTMLResponse)
def serve_app():
    if STANDALONE_HTML.exists():
        return FileResponse(STANDALONE_HTML)
    return HTMLResponse("<h1>MediMitra AI — Standalone</h1>")


if __name__ == "__main__":
    import uvicorn
    from backend.app.config import BACKEND_HOST, BACKEND_PORT
    uvicorn.run("backend.app.main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
