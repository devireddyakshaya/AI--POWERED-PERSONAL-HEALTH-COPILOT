"""
Health check and system status routes for MediMitra AI.
"""
from fastapi import APIRouter
from backend.app.config import is_demo_mode, APP_ENV, EPHEMERAL_PROCESSING_ONLY

router = APIRouter(tags=["Health & Status"])

@router.get("/health")
def health_check():
    """Returns application health status."""
    return {
        "status": "healthy",
        "service": "MediMitra AI",
        "version": "1.0.0",
        "team": "TEKSQUADS",
        "hackathon": "HacXLerate 2026"
    }

@router.get("/status")
def system_status():
    """Returns current runtime environment, AI mode, and privacy configuration."""
    demo_active = is_demo_mode()
    return {
        "mode": "DEMO_MODE" if demo_active else "LIVE_AI_MODE",
        "is_demo_mode": demo_active,
        "environment": APP_ENV,
        "privacy": {
            "ephemeral_processing": EPHEMERAL_PROCESSING_ONLY,
            "local_database": "SQLite (Privacy-First)",
            "external_ai_logging": False
        },
        "capabilities": {
            "pdf_extraction": True,
            "ocr_processing": True,
            "telugu_translation": True,
            "multilingual_explanations": True,
            "supported_languages": ["en", "te", "hi", "ta", "kn", "ml"],
            "health_change_detector": True,
            "evidence_linking": True,
            "abdm_fhir_export": True,
            "voice_assistant": True
        }
    }
