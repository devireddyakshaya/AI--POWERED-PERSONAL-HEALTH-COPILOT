import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.ai_service import AIService


def test_detects_nvidia_api_keys():
    assert AIService._uses_nvidia_api("nvapi-test-key") is True
    assert AIService._uses_nvidia_api("AIza-test-key") is False


def test_builds_nvidia_payload():
    payload = AIService._build_nvidia_payload("Demo User", "Lab Report", "2026-01-01", [{"test_name": "HbA1c", "original_value": "7.4"}], [])
    assert payload["model"]
    assert payload["messages"][0]["role"] == "system"
    assert "Lab Report" in payload["messages"][1]["content"]
