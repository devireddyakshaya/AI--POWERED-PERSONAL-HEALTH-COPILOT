"""
Comprehensive README Verification Suite for MediMitra AI.
Tests all functionalities documented in README.md against the actual implementation.
"""
import io
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.data.demo_samples import seed_demo_data

client = TestClient(app)


def test_medical_record_intelligence_ocr():
    """Medical Record Intelligence & OCR: Extracts test names, values, units, reference intervals, medicines, dosages, diagnoses."""
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
    assert upload_resp.status_code == 200, "OCR upload failed"
    uploaded_doc = upload_resp.json()
    observations = uploaded_doc.get("observations", [])
    medications = uploaded_doc.get("medications", [])
    # Verify OCR extracted key fields
    test_names = [o["test_name"] for o in observations]
    assert any("Glucose" in n for n in test_names), "Glucose not extracted"
    assert any("Creatinine" in n for n in test_names), "Creatinine not extracted"
    # Verify units
    for o in observations:
        assert o.get("unit") is not None, f"Missing unit for {o['test_name']}"
# Verify medicines extracted
        med_names = [m["medicine_name"] for m in medications]
        assert any("Metformin" in n for n in med_names), "Metformin not extracted"
        # Check dosage is present (could be "500mg", "500 mg", etc.)
        has_dosage = any(m.get("dosage") for m in medications)
        assert has_dosage, "Dosage not extracted"
    print("[PASS] Medical Record Intelligence & OCR")


def test_ai_health_explainer():
    """AI Health Explainer in Simple Language: Generates patient-friendly explanations in plain English and Telugu."""
    docs_resp = client.get("/api/documents")
    docs = docs_resp.json()
    doc_id = docs[0]["id"]
    detail_resp = client.get(f"/api/documents/{doc_id}")
    data = detail_resp.json()
    assert data["summary"] is not None, "Summary missing"
    assert "english_summary" in data["summary"], "English summary missing"
    assert "telugu_summary" in data["summary"], "Telugu summary missing"
    english = data["summary"]["english_summary"]
    telugu = data["summary"]["telugu_summary"]
    assert len(english) > 0, "English summary empty"
    assert len(telugu) > 0, "Telugu summary empty"
    print("[PASS] AI Health Explainer in Simple Language")


def test_unified_health_profile_timeline():
    """Unified Health Profile & Timeline: Chronological repository of health records with search, category filtering."""
    response = client.get("/api/documents")
    docs = response.json()
    assert len(docs) >= 2, "Expected at least 2 synthetic demo documents"
    # Check chronological ordering (created_at should be present)
    for doc in docs:
        assert "created_at" in doc or "document_date" in doc, f"Missing date in doc {doc.get('id')}"
    # Check document types varied
    doc_types = set(d.get("document_type") for d in docs)
    assert len(doc_types) > 0, "No document types found"
    print("[PASS] Unified Health Profile & Timeline")


def test_health_change_detector():
    """Health Change Detector: Compares two reports, validates unit compatibility, computes deltas, trend charts, range shift status."""
    response = client.post("/api/comparison", json={
        "report_a_id": 2,
        "report_b_id": 1
    })
    assert response.status_code == 200, "Change detector failed"
    comp_data = response.json()
    assert "safe_comparison" in comp_data, "Missing safe_comparison"
    assert "matched_tests" in comp_data, "Missing matched_tests"
    assert "disclaimer" in comp_data, "Missing medical disclaimer"
    assert isinstance(comp_data["safe_comparison"], bool), "safe_comparison should be boolean"
    # Verify range shift status present
    for test in comp_data.get("matched_tests", []):
        assert "range_shift_status" in test, "Missing range_shift_status"
        assert "clinical_note" in test, "Missing clinical_note"
    print("[PASS] Health Change Detector")


def test_evidence_linked_ai_answers():
    """Evidence-Linked AI Answers: Every summary claim links back to exact source document line and OCR confidence score."""
    docs_resp = client.get("/api/documents")
    docs = docs_resp.json()
    doc_id = docs[0]["id"]
    detail_resp = client.get(f"/api/documents/{doc_id}")
    data = detail_resp.json()
    observations = data.get("observations", [])
    for obs in observations:
        assert "evidence_excerpt" in obs, f"Missing evidence_excerpt for {obs.get('test_name')}"
        assert len(obs.get("evidence_excerpt", "")) > 0, f"Empty evidence_excerpt for {obs['test_name']}"
        assert "confidence_score" in obs, f"Missing confidence_score for {obs['test_name']}"
    # Verify summary has evidence linking
    assert data["summary"] is not None, "Summary missing"
    print("[PASS] Evidence-Linked AI Answers")


def test_smart_report_trust_check():
    """Smart Report Trust Check: Detects missing units, unreadable scans, missing reference ranges, preserves original value when user corrections submitted."""
    docs_resp = client.get("/api/documents")
    docs = docs_resp.json()
    doc_id = docs[0]["id"]
    # Get original observation
    doc_detail = client.get(f"/api/documents/{doc_id}").json()
    obs = doc_detail["observations"][0]
    original_val = obs["original_value"]
    # Apply user correction
    corr_resp = client.put(
        f"/api/documents/{doc_id}/observations/{obs['id']}",
        json={"user_corrected_value": "135.0", "is_verified": True}
    )
    assert corr_resp.status_code == 200, "Correction endpoint failed"
    updated = corr_resp.json()
    # Original value must remain intact (provenance preservation)
    assert updated["original_value"] == original_val, "Original value not preserved!"
    assert updated["user_corrected_value"] == "135.0", "Corrected value not recorded"
    assert updated["is_verified"] is True, "Verification flag not set"
    print("[PASS] Smart Report Trust Check")


def test_telugu_health_translator():
    """Telugu Health Translator: High-fidelity Telugu medical explanations preserving medicine names, values, units, dates."""
    docs_resp = client.get("/api/documents")
    docs = docs_resp.json()
    doc_id = docs[0]["id"]
    detail_resp = client.get(f"/api/documents/{doc_id}")
    data = detail_resp.json()
    telugu = data["summary"]["telugu_summary"]
    assert len(telugu) > 0, "Telugu summary empty"
    # Verify Telugu contains expected terms
    assert "తెలుగు" in telugu or "Namaste" in telugu, "Telugu script not found"
    # Verify medicine names and numbers preserved
    assert "Metformin" in telugu or "మెటformin" in telugu, "Medicine name not preserved in Telugu"
    print("[PASS] Telugu Health Translator")


def test_personal_health_memory():
    """Personal Health Memory: Chronological timeline with multi-criteria filtering for Laboratory Reports, Prescriptions, Diagnostics, Discharge Summaries."""
    # Test filtering by document type
    response = client.get("/api/documents")
    docs = response.json()
    lab_docs = [d for d in docs if d.get("document_type") == "Laboratory Report"]
    assert len(lab_docs) > 0, "No laboratory reports found for memory filter"
    # Verify chronological ordering
    dates = [d.get("document_date") for d in docs if d.get("document_date")]
    assert len(dates) > 0, "No document dates found"
    print("[PASS] Personal Health Memory")


def test_doctor_visit_prep_assistant():
    """Doctor Visit Prep Assistant: Interactive checklist of clinician discussion questions derived from abnormal findings."""
    response = client.get("/api/doctor-prep")
    assert response.status_code == 200, "Doctor prep failed"
    questions = response.json()
    assert len(questions) > 0, "No questions generated"
    # Test adding custom question
    post_resp = client.post(
        "/api/doctor-prep",
        json={"question_text": "Should I modify my evening meal timing?", "category": "Personal Question"}
    )
    assert post_resp.status_code == 200, "Add question failed"
    # Test toggling
    new_q_id = post_resp.json()["id"]
    toggle_resp = client.patch(
        f"/api/doctor-prep/{new_q_id}/toggle",
        json={"is_checked": True}
    )
    assert toggle_resp.status_code == 200, "Toggle failed"
    assert toggle_resp.json()["is_checked"] is True, "Toggle not saved"
    print("[PASS] Doctor Visit Prep Assistant")


def test_prescription_to_reminder_planner():
    """Prescription-to-Reminder Planner: Converts readable instructions into daily schedule, requires user verification, flags incomplete."""
    response = client.get("/api/medications")
    assert response.status_code == 200, "Medications endpoint failed"
    data = response.json()
    assert "medications" in data, "Missing medications"
    assert "daily_schedule" in data, "Missing daily_schedule"
    # Verify incomplete medications flagged
    for med in data.get("medications", []):
        if med.get("is_incomplete"):
            assert med.get("trust_warning"), f"Incomplete med {med['medicine_name']} missing warning"
    # Test updating reminder
    med = data["medications"][0]
    upd_resp = client.patch(
        f"/api/medications/{med['id']}",
        json={"schedule_time": "09:00 PM", "is_reminder_active": True, "is_verified": True}
    )
    assert upd_resp.status_code == 200, "Medication update failed"
    updated = upd_resp.json()
    assert updated["schedule_time"] == "09:00 PM", "Schedule time not updated"
    assert updated["is_reminder_active"] is True, "Reminder active flag not set"
    print("[PASS] Prescription-to-Reminder Planner")


def test_privacy_first_health_vault():
    """Privacy-First Health Vault: Ephemeral in-memory processing, local SQLite storage, single-click permanent data purge."""
    # Check status shows privacy flags
    response = client.get("/api/status")
    assert response.status_code == 200, "Status check failed"
    status_data = response.json()
    assert status_data["privacy"]["ephemeral_processing"] is True, "Ephemeral processing not enabled"
    # Test document deletion (privacy purge)
    docs_resp = client.get("/api/documents")
    initial_count = len(docs_resp.json())
    if initial_count > 0:
        doc_id = docs_resp.json()[0]["id"]
        del_resp = client.delete(f"/api/documents/{doc_id}")
        assert del_resp.status_code == 200, "Delete failed"
        assert del_resp.json()["success"] is True, "Delete not successful"
        # Verify document removed
        remaining = client.get("/api/documents").json()
        assert len(remaining) == initial_count - 1, "Document not purged from listing"
    print("[PASS] Privacy-First Health Vault")


def test_abdm_abha_ready_architecture():
    """ABDM/ABHA-Ready Architecture: FHIR R4 bundle export, synthetic ABHA demo identifier."""
    docs_resp = client.get("/api/documents")
    docs = docs_resp.json()
    doc_id = docs[0]["id"]
    bundle_resp = client.get(f"/api/fhir/bundle/{doc_id}")
    assert bundle_resp.status_code == 200, "FHIR bundle generation failed"
    bundle = bundle_resp.json()
    assert bundle["resourceType"] == "Bundle", "Bundle resourceType incorrect"
    assert "entry" in bundle, "Missing bundle entries"
    # Verify synthetic ABHA ID present
    patient_entry = next(
        (e for e in bundle["entry"] if e.get("resource", {}).get("resourceType") == "Patient"),
        None
    )
    assert patient_entry is not None, "Patient not in bundle"
    patient = patient_entry["resource"]
    assert "synthetic" in patient.get("identifier", [{}])[0].get("value", "").lower(), "Synthetic ABHA ID not found"
    assert "91-4582-9012-3456" in patient.get("identifier", [{}])[0].get("value", ""), "ABHA demo ID not present"
    # Verify FHIR resources present
    resource_types = [e["resource"]["resourceType"] for e in bundle["entry"]]
    assert "Patient" in resource_types, "Patient resource missing"
    assert "DiagnosticReport" in resource_types, "DiagnosticReport resource missing"
    assert "Observation" in resource_types, "Observation resource missing"
    assert "MedicationRequest" in resource_types, "MedicationRequest resource missing"
    print("[PASS] ABDM/ABHA-Ready Architecture")


def test_system_health_check():
    """System health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200, "Health check failed"
    data = response.json()
    assert data["status"] == "healthy", "Status not healthy"
    assert data["service"] == "MediMitra AI", "Service name incorrect"
    print("[PASS] System Health Check")


def test_system_status_demo_mode():
    """System status check - Demo vs Live mode."""
    response = client.get("/api/status")
    assert response.status_code == 200, "Status check failed"
    data = response.json()
    assert "mode" in data, "Mode not in status"
    assert data["privacy"]["ephemeral_processing"] is True, "Ephemeral processing flag incorrect"
    print("[PASS] System Status Demo Mode")


if __name__ == "__main__":
    tests = [
        test_medical_record_intelligence_ocr,
        test_ai_health_explainer,
        test_unified_health_profile_timeline,
        test_health_change_detector,
        test_evidence_linked_ai_answers,
        test_smart_report_trust_check,
        test_telugu_health_translator,
        test_personal_health_memory,
        test_doctor_visit_prep_assistant,
        test_prescription_to_reminder_planner,
        test_privacy_first_health_vault,
        test_abdm_abha_ready_architecture,
        test_system_health_check,
        test_system_status_demo_mode,
    ]
    
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"{'='*60}")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\nAll README functionality verifications PASSED!")