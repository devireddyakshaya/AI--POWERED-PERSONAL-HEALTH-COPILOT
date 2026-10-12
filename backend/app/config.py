"""
Configuration settings for MediMitra AI backend.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if present
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'MediMitra.db'}")
EPHEMERAL_PROCESSING_ONLY = os.getenv("EPHEMERAL_PROCESSING_ONLY", "true").lower() in ("true", "1", "yes")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")

# Directory for ephemeral or temporary file processing
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

def is_demo_mode() -> bool:
    """
    Returns True if no Gemini API key is configured or if APP_ENV is explicitly 'demo'.
    Enables automatic fallback to deterministic synthetic medical intelligence engine.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        return True
    return APP_ENV == "demo"
