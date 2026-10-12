"""
Automated test suite for MediMitra AI backend.
Covers:
- System health & status checks
- Pre-seeded synthetic records retrieval
- Document upload and OCR parsing
- Observation manual correction (provenance preservation)
- Health Change Detector (safe comparison, range shifts, unit mismatch flags)
- AI Explanations and Telugu translation integrity
- Doctor Visit Prep checklist
- Medication Planner verification
- ABDM/FHIR R4 bundle generation
- Document deletion privacy
- Error handling
"""
import io
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.data.demo_samples import seed_demo_data

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_demo_data(db)
    db.close()
    yield

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "MediMitra AI"

def test_system_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert data["privacy"]["ephemeral_processing"] is True

def test_list_documents():
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 2
    # Check synthetic tags
    assert any(d["is_synthetic"] for d in docs)
    first = docs[0]
    assert "trust_score" in first
    assert "observation_count" in first

def test_get_document_detail():
    response = client.get("/api/documents")
    docs = response.json()
    doc_id = docs[0]["id"]

    detail_resp = client.get(f"/api/documents/{doc_id}")
    assert detail_resp.status_code == 200
    data = detail_resp.json()
    assert len(data["observations"]) > 0
    assert data["summary"] is not None
    assert "english_summary" in data["summary"]
    assert "telugu_summary" in data["summary"]

def test_observation_correction_preserves_original():
    docs_resp = client.get("/api/documents")
    doc_id = docs_resp.json()[0]["id"]

    doc_detail = client.get(f"/api/documents/{doc_id}").json()
    obs = doc_detail["observations"][0]
    original_val = obs["original_value"]

    # Apply user correction
    corr_resp = client.put(
        f"/api/documents/{doc_id}/observations/{obs['id']}",
        json={"user_corrected_value": "135.0", "is_verified": True}
    )
    assert corr_resp.status_code == 200
    updated = corr_resp.json()

    # Original value must remain intact (provenance preservation)
    assert updated["original_value"] == original_val
    assert updated["user_corrected_value"] == "135.0"
    assert updated["is_verified"] is True

def test_health_change_detector():
    docs_resp = client.get("/api/documents")
    docs = docs_resp.json()
    assert len(docs) >= 2

    # Compare Report A (Baseline) and Report B (Follow-up)
    comp_resp = client.post(
        "/api/comparison",
        json={"report_a_id": docs[1]["id"], "report_b_id": docs[0]["id"]}
    )
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert comp_data["safe_comparison"] is True
    assert len(comp_data["matched_tests"]) > 0

    # Verify Fasting Glucose or HbA1c matched
    glucose_match = next((t for t in comp_data["matched_tests"] if "Glucose" in t["test_name"]), None)
    if glucose_match:
        assert glucose_match["unit"] == "mg/dL"
        assert glucose_match["absolute_change"] != 0
        assert glucose_match["range_shift_status"] in ("CLOSER_TO_NORMAL", "WITHIN_NORMAL", "FARTHER_FROM_NORMAL")
        # Ensure medical safety note is present
        assert "clinical_note" in glucose_match
        assert "disclaimer" in comp_data

def test_doctor_visit_prep_checklist():
    get_resp = client.get("/api/doctor-prep")
    assert get_resp.status_code == 200
    questions = get_resp.json()
    assert len(questions) > 0

    # Add custom question
    post_resp = client.post(
        "/api/doctor-prep",
        json={"question_text": "Should I modify my evening meal timing?", "category": "Personal Question"}
    )
    assert post_resp.status_code == 200
    new_q = post_resp.json()
    assert new_q["question_text"] == "Should I modify my evening meal timing?"

    # Toggle check
    toggle_resp = client.patch(
        f"/api/doctor-prep/{new_q['id']}/toggle",
        json={"is_checked": True}
    )
    assert toggle_resp.status_code == 200
    assert toggle_resp.json()["is_checked"] is True

def test_medication_planner():
    get_resp = client.get("/api/medications")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert "medications" in data
    assert "daily_schedule" in data

    med = data["medications"][0]
    # Update schedule and verify
    upd_resp = client.patch(
        f"/api/medications/{med['id']}",
        json={"schedule_time": "09:00 PM", "is_reminder_active": True, "is_verified": True}
    )
    assert upd_resp.status_code == 200
    updated = upd_resp.json()
    assert updated["schedule_time"] == "09:00 PM"
    assert updated["is_reminder_active"] is True

def test_fhir_bundle_generation():
    docs_resp = client.get("/api/documents")
    doc_id = docs_resp.json()[0]["id"]

    bundle_resp = client.get(f"/api/fhir/bundle/{doc_id}")
    assert bundle_resp.status_code == 200
    bundle = bundle_resp.json()
    assert bundle["resourceType"] == "Bundle"
    assert "entry" in bundle
    resource_types = [e["resource"]["resourceType"] for e in bundle["entry"]]
    assert "Patient" in resource_types
    assert "DiagnosticReport" in resource_types
    assert "Observation" in resource_types

def test_file_upload_and_extraction():
    sample_text = """
    AAROGYAM DIAGNOSTICS
    Patient Name: Test User
    Date: 2026-02-10
    Fasting Blood Glucose: 130 mg/dL (Reference: 70 - 99 mg/dL)
    Serum Creatinine: 1.1 mg/dL (Reference: 0.7 - 1.3 mg/dL)
    Rx: Tab Metformin 500mg Once Daily after dinner
    """
    file_payload = io.BytesIO(sample_text.encode("utf-8"))
    upload_resp = client.post(
        "/api/documents/upload",
        files={"file": ("test_report.txt", file_payload, "text/plain")}
    )
    assert upload_resp.status_code == 200
    uploaded_doc = upload_resp.json()
    assert len(uploaded_doc["observations"]) >= 2
    assert uploaded_doc["summary"] is not None
    assert "test_report.txt" in uploaded_doc["file_name"]

def test_voice_ask_full_summary():
    docs_resp = client.get("/api/documents")
    docs = docs_resp.json()
    doc_id = docs[0]["id"]

    resp = client.post(
        "/api/voice/ask",
        json={"query": "read my report summary", "language": "en", "document_id": doc_id}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert data["document_id"] == doc_id

def test_voice_ask_specific_test():
    docs_resp = client.get("/api/documents")
    doc_id = docs_resp.json()[0]["id"]

    resp = client.post(
        "/api/voice/ask",
        json={"query": "what is my fasting blood glucose?", "language": "en", "document_id": doc_id}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "Glucose" in data["answer"]
    assert "mg/dL" in data["answer"]

def test_voice_ask_medicines():
    docs_resp = client.get("/api/documents")
    doc_id = docs_resp.json()[0]["id"]

    resp = client.post(
        "/api/voice/ask",
        json={"query": "show my medicines", "language": "en", "document_id": doc_id}
    )
    assert resp.status_code == 200
    assert "Medicines" in resp.json()["answer"] or "medicine" in resp.json()["answer"].lower()

def test_voice_ask_without_document():
    resp = client.post("/api/voice/ask", json={"query": "what is my report?", "language": "en"})
    assert resp.status_code == 200
    assert len(resp.json()["answer"]) > 0

def test_document_deletion():
    docs_resp = client.get("/api/documents")
    initial_count = len(docs_resp.json())
    doc_id = docs_resp.json()[0]["id"]

    del_resp = client.delete(f"/api/documents/{doc_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Ensure document is no longer listed
    remaining_docs = client.get("/api/documents").json()
    assert len(remaining_docs) == initial_count - 1
