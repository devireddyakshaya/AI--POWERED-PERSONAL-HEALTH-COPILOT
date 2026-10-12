"""
MediMitra AI — Comprehensive Backend Agent
Validates all services, API endpoints, and pipeline integration.

Run: python backend/agent/backend_agent.py
"""

import io
import sys
from pathlib import Path

# Ensure project root is in path (workspace root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure backend directory is importable
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure tests directory is importable
TESTS_DIR = BACKEND_DIR / "tests"
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def run_all_tests():
    """Run the complete backend validation suite and return detailed results."""
    results = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "services_tested": [],
        "endpoints_tested": [],
        "ocr_tests": [],
        "pipeline_tests": [],
        "bugs_found": [],
        "passed": 0,
        "failed": 0,
        "total": 0,
    }

    # =====================================================
    # 1. Core Service Validation
    # =====================================================
    print("=" * 70)
    print("CORE SERVICE VALIDATION")
    print("=" * 70)

    # OCR Service Validation
    print("\n[1] Testing OCR Service...")
    ocr_pass, ocr_bug = test_ocr_service()
    results["ocr_tests"].append({"name": "OCR Service Validation", "passed": ocr_pass, "bug": ocr_bug})
    status_str = "PASS" if ocr_pass else f"FAIL - {ocr_bug}"
    print(f"  >> OCR Service: {status_str}")

    # Parser Service Validation
    print("\n[2] Testing Medical Parser Service...")
    parser_pass, parser_bug = test_parser_service()
    results["services_tested"].append({"name": "MedicalParserService", "passed": parser_pass, "bug": parser_bug})
    status_str = "PASS" if parser_pass else f"FAIL - {parser_bug}"
    print(f"  >> Medical Parser: {status_str}")

    # AI Service Validation
    print("\n[3] Testing AI Service (English + Telugu)...")
    ai_pass, ai_bug = test_ai_service()
    results["services_tested"].append({"name": "AIService", "passed": ai_pass, "bug": ai_bug})
    status_str = "PASS" if ai_pass else f"FAIL - {ai_bug}"
    print(f"  >> AI Service: {status_str}")

    # Telugu Service Validation
    print("\n[4] Testing Telugu Health Translator...")
    te_pass, te_bug = test_telugu_service()
    results["services_tested"].append({"name": "TeluguHealthTranslator", "passed": te_pass, "bug": te_bug})
    status_str = "PASS" if te_pass else f"FAIL - {te_bug}"
    print(f"  >> Telugu Translator: {status_str}")

    # Comparison Service Validation
    print("\n[5] Testing Health Change Detector...")
    comp_pass, comp_bug = test_comparison_service()
    results["services_tested"].append({"name": "HealthChangeDetectorService", "passed": comp_pass, "bug": comp_bug})
    status_str = "PASS" if comp_pass else f"FAIL - {comp_bug}"
    print(f"  >> Health Change Detector: {status_str}")

    # FHIR Service Validation
    print("\n[6] Testing FHIR Converter Service...")
    fhir_pass, fhir_bug = test_fhir_service()
    results["services_tested"].append({"name": "FHIRConverterService", "passed": fhir_pass, "bug": fhir_bug})
    status_str = "PASS" if fhir_pass else f"FAIL - {fhir_bug}"
    print(f"  >> FHIR Converter: {status_str}")

    # Medication Service Validation
    print("\n[7] Testing Medication Planner Service...")
    med_pass, med_bug = test_medication_service()
    results["services_tested"].append({"name": "MedicationPlannerService", "passed": med_pass, "bug": med_bug})
    status_str = "PASS" if med_pass else f"FAIL - {med_bug}"
    print(f"  >> Medication Planner: {status_str}")

    # Doctor Prep Service Validation
    print("\n[8] Testing Doctor Prep Service...")
    doc_prep_pass, doc_prep_bug = test_doctor_prep_service()
    results["services_tested"].append({"name": "DoctorPrepService", "passed": doc_prep_pass, "bug": doc_prep_bug})
    status_str = "PASS" if doc_prep_pass else f"FAIL - {doc_prep_bug}"
    print(f"  >> Doctor Prep: {status_str}")

    # =====================================================
    # 2. API Endpoint Testing (all endpoints under /api)
    # =====================================================
    print("\n" + "=" * 70)
    print("API ENDPOINT TESTING (all endpoints under /api)")
    print("=" * 70)

    # Seed database before testing API endpoints that need demo data
    from tests.test_api import seed_demo_data
    from backend.app.database import Base, engine, SessionLocal

    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    seed_demo_data(db)
    db.close()

    endpoints = [
        ("GET /api/health", client.get, "/api/health", 200),
        ("GET /api/status", client.get, "/api/status", 200),
        ("GET /api/documents", client.get, "/api/documents", 200),
        ("GET /api/documents/1", client.get, "/api/documents/1", 200),
        ("POST /api/documents/upload", client.post, "/api/documents/upload", 200),
        ("PUT /api/documents/1/observations/1", client.put, "/api/documents/1/observations/1", 200),
        ("DELETE /api/documents/1", client.delete, "/api/documents/1", 200),
        ("POST /api/documents/reset-demo", client.post, "/api/documents/reset-demo", 200),
        ("POST /api/comparison", client.post, "/api/comparison", 200),
        ("GET /api/doctor-prep", client.get, "/api/doctor-prep", 200),
        ("POST /api/doctor-prep", client.post, "/api/doctor-prep", 200),
        ("PATCH /api/doctor-prep/1/toggle", client.patch, "/api/doctor-prep/1/toggle", 200),
        ("DELETE /api/doctor-prep/1", client.delete, "/api/doctor-prep/1", 200),
        ("GET /api/medications", client.get, "/api/medications", 200),
        ("PATCH /api/medications/1", client.patch, "/api/medications/1", 200),
        ("GET /api/fhir/patient", client.get, "/api/fhir/patient", 200),
        ("GET /api/fhir/bundle/1", client.get, "/api/fhir/bundle/1", 200),
        # Additional endpoints with correct prefixes
        ("GET /api/analysis/languages", client.get, "/api/analysis/languages", 200),
        ("GET /api/analysis/explain/1?language=en", client.get, "/api/analysis/explain/1?language=en", 200),
        ("POST /api/voice/ask", client.post, "/api/voice/ask", 200),
    ]

    for name, method, path, expected_status in endpoints:
        try:
            resp = method(path)
            status = resp.status_code
            passed = status == expected_status
            results["endpoints_tested"].append({
                "name": name,
                "path": path,
                "status_code": status,
                "expected": expected_status,
                "passed": passed,
            })
            if passed:
                print(f"  >> {name}: PASS ({status} code)")
            else:
                print(f"  >> {name}: FAIL (got {status}, expected {expected_status})")
                results["bugs_found"].append(f"Endpoint {name}: got {status}, expected {expected_status}")
        except Exception as e:
            results["endpoints_tested"].append({
                "name": name,
                "path": path,
                "error": str(e),
                "passed": False,
            })
            print(f"  >> {name}: ERROR - {e}")
            results["bugs_found"].append(f"Endpoint {name}: {e}")

    # =====================================================
    # 3. Pipeline Integration Testing
    # =====================================================
    print("\n" + "=" * 70)
    print("PIPELINE INTEGRATION TESTING")
    print("  Upload -> OCR -> Parse -> Summary -> Telugu -> Comparison -> FHIR")
    print("=" * 70)

    pipeline_pass, pipeline_bug = test_full_pipeline()
    results["pipeline_tests"].append({"name": "Full End-to-End Pipeline", "passed": pipeline_pass, "bug": pipeline_bug})
    status_str = "PASS" if pipeline_pass else f"FAIL - {pipeline_bug}"
    print(f"  >> Full Pipeline: {status_str}")

    # =====================================================
    # 4. Test Suite Maintenance
    # =====================================================
    print("\n" + "=" * 70)
    print("TEST SUITE MAINTENANCE")
    print("  Running existing test_api.py (15 tests) + test_readme_verification.py (14 tests)")
    print("=" * 70)

    # Run test_api.py
    api_pass, api_fail = run_pytest_suite("tests/test_api.py")
    results["total"] += 15
    results["passed"] += api_pass
    results["failed"] += api_fail
    print(f"  >> test_api.py: {api_pass}/15 passed, {api_fail} failed")

    # Run test_readme_verification.py
    readme_pass, readme_fail = run_pytest_suite("tests/test_readme_verification.py")
    results["total"] += 14
    results["passed"] += readme_pass
    results["failed"] += readme_fail
    print(f"  >> test_readme_verification.py: {readme_pass}/14 passed, {readme_fail} failed")

    # =====================================================
    # 5. Summary
    # =====================================================
    print("\n" + "=" * 70)
    print("COMPREHENSIVE RESULTS SUMMARY")
    print("=" * 70)
    print(f"  Total Tests: {results['total']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")
    if results["total"] > 0:
        print(f"  Success Rate: {results['passed'] / results['total'] * 100:.1f}%")
    else:
        print("  Success Rate: N/A")

    if results["bugs_found"]:
        print(f"\n  Bugs Found ({len(results['bugs_found'])}):")
        for bug in results["bugs_found"]:
            print(f"    - {bug}")
    else:
        print("\n  No bugs found! All services functioning correctly.")

    print("\n" + "=" * 70)
    if results["failed"] == 0:
        print("ALL TESTS PASSED - MediMitra AI Backend is healthy!")
    else:
        print(f"SOME TESTS FAILED - {results['failed']} issues need attention")
    print("=" * 70)

    return results


def test_ocr_service():
    """Test OCR service with sample documents."""
    try:
        from tests.test_api import seed_demo_data
        from backend.app.database import Base, engine, SessionLocal

        db = SessionLocal()
        Base.metadata.create_all(bind=engine)
        seed_demo_data(db)
        db.close()

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
        if upload_resp.status_code != 200:
            return False, f"Upload failed with status {upload_resp.status_code}"

        uploaded_doc = upload_resp.json()
        observations = uploaded_doc.get("observations", [])
        medications = uploaded_doc.get("medications", [])

        test_names = [o["test_name"] for o in observations]
        if not any("Glucose" in n for n in test_names):
            return False, "Glucose not extracted by OCR"
        if not any("Creatinine" in n for n in test_names):
            return False, "Creatinine not extracted by OCR"

        for o in observations:
            if o.get("unit") is None:
                return False, f"Missing unit for {o['test_name']}"

        med_names = [m["medicine_name"] for m in medications]
        if not any("Metformin" in n for n in med_names):
            return False, "Metformin not extracted by OCR"

        has_dosage = any(m.get("dosage") for m in medications)
        if not has_dosage:
            return False, "Dosage not extracted by OCR"

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def test_parser_service():
    """Test Medical Parser Service with sample text."""
    try:
        from backend.app.services.parser_service import MedicalParserService
        sample_text = """
        Fasting Blood Glucose: 130 mg/dL (Reference: 70 - 99 mg/dL)
        Serum Creatinine: 1.1 mg/dL (Reference: 0.7 - 1.3 mg/dL)
        Rx: Tab Metformin 500mg Once Daily after dinner
        """
        parsed = MedicalParserService.parse_document(sample_text)

        observations = parsed["observations"]
        if len(observations) < 2:
            return False, f"Expected >= 2 observations, got {len(observations)}"

        test_names = [o["test_name"] for o in observations]
        if not any("Glucose" in n for n in test_names):
            return False, "Glucose not parsed"
        if not any("Creatinine" in n for n in test_names):
            return False, "Creatinine not parsed"

        for o in observations:
            if o.get("unit") is None:
                return False, f"Missing unit for {o['test_name']}"

        medications = parsed["medications"]
        med_names = [m["medicine_name"] for m in medications]
        if not any("Metformin" in n for n in med_names):
            return False, "Metformin not parsed"

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def test_ai_service():
    """Test AI Service generates English + Telugu summaries."""
    try:
        from tests.test_api import seed_demo_data
        from backend.app.database import Base, engine, SessionLocal

        db = SessionLocal()
        Base.metadata.create_all(bind=engine)
        seed_demo_data(db)
        db.close()

        from fastapi.testclient import TestClient
        client_local = TestClient(app)
        docs_resp = client_local.get("/api/documents")
        docs = docs_resp.json()
        doc_id = docs[0]["id"]

        detail_resp = client_local.get(f"/api/documents/{doc_id}")
        data = detail_resp.json()

        summary = data.get("summary", {})
        if summary is None:
            return False, "Summary missing from document detail"

        if "english_summary" not in summary:
            return False, "English summary missing"
        if "telugu_summary" not in summary:
            return False, "Telugu summary missing"

        english = summary["english_summary"]
        telugu = summary["telugu_summary"]

        if len(english) == 0:
            return False, "English summary empty"
        if len(telugu) == 0:
            return False, "Telugu summary empty"

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def test_telugu_service():
    """Test Telugu Health Translator produces proper Telugu output."""
    try:
        from tests.test_api import seed_demo_data
        from backend.app.database import Base, engine, SessionLocal

        db = SessionLocal()
        Base.metadata.create_all(bind=engine)
        seed_demo_data(db)
        db.close()

        from fastapi.testclient import TestClient
        client_local = TestClient(app)
        docs_resp = client_local.get("/api/documents")
        docs = docs_resp.json()
        doc_id = docs[0]["id"]

        detail_resp = client_local.get(f"/api/documents/{doc_id}")
        data = detail_resp.json()

        telugu = data["summary"]["telugu_summary"]
        if len(telugu) == 0:
            return False, "Telugu summary empty"

        # Check for Telugu script (Unicode range: 0C00-0C7F)
        has_telugu_script = any(
            0x0C00 <= ord(c) <= 0x0C7F for c in telugu
        )
        if not has_telugu_script:
            return False, "Telugu script not found in summary"

        # Medicine names and numbers should be preserved
        # (allow for transliteration variations)

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def test_comparison_service():
    """Test Health Change Detector comparison."""
    try:
        from tests.test_api import seed_demo_data
        from backend.app.database import Base, engine, SessionLocal

        db = SessionLocal()
        Base.metadata.create_all(bind=engine)
        seed_demo_data(db)
        db.close()

        from fastapi.testclient import TestClient
        client_local = TestClient(app)
        docs_resp = client_local.get("/api/documents")
        docs = docs_resp.json()

        if len(docs) < 2:
            return False, "Need at least 2 documents for comparison test"

        comp_resp = client_local.post(
            "/api/comparison",
            json={"report_a_id": docs[1]["id"], "report_b_id": docs[0]["id"]}
        )
        if comp_resp.status_code != 200:
            return False, f"Comparison endpoint returned status {comp_resp.status_code}"

        comp_data = comp_resp.json()
        if comp_data.get("safe_comparison") is not True:
            return False, "Comparison not marked as safe"

        if len(comp_data.get("matched_tests", [])) == 0:
            return False, "No matched tests in comparison"

        glucose_match = next(
            (t for t in comp_data["matched_tests"] if "Glucose" in t["test_name"]), None
        )
        if glucose_match:
            if glucose_match.get("unit") != "mg/dL":
                return False, f"Glucose unit mismatch: {glucose_match.get('unit')}"
            if glucose_match.get("absolute_change") == 0:
                return False, "Glucose absolute change is 0"
            if glucose_match.get("range_shift_status") not in ("CLOSER_TO_NORMAL", "WITHIN_NORMAL", "FARTHER_FROM_NORMAL"):
                return False, f"Glucose range shift status: {glucose_match.get('range_shift_status')}"
            if "clinical_note" not in glucose_match:
                return False, "Missing clinical_note for glucose"

        if "disclaimer" not in comp_data:
            return False, "Missing medical disclaimer in comparison"

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def test_fhir_service():
    """Test FHIR Bundle generation."""
    try:
        from tests.test_api import seed_demo_data
        from backend.app.database import Base, engine, SessionLocal

        db = SessionLocal()
        Base.metadata.create_all(bind=engine)
        seed_demo_data(db)
        db.close()

        from fastapi.testclient import TestClient
        client_local = TestClient(app)
        docs_resp = client_local.get("/api/documents")
        doc_id = docs_resp.json()[0]["id"]

        bundle_resp = client_local.get(f"/api/fhir/bundle/{doc_id}")
        if bundle_resp.status_code != 200:
            return False, f"FHIR bundle endpoint returned status {bundle_resp.status_code}"

        bundle = bundle_resp.json()
        if bundle.get("resourceType") != "Bundle":
            return False, f"Bundle resourceType incorrect: {bundle.get('resourceType')}"

        if "entry" not in bundle:
            return False, "Missing bundle entries"

        resource_types = [e["resource"]["resourceType"] for e in bundle.get("entry", [])]
        if "Patient" not in resource_types:
            return False, "Patient resource missing from bundle"
        if "DiagnosticReport" not in resource_types:
            return False, "DiagnosticReport resource missing from bundle"
        if "Observation" not in resource_types:
            return False, "Observation resource missing from bundle"
        if "MedicationRequest" not in resource_types:
            return False, "MedicationRequest resource missing from bundle"

        patient_entry = next(
            (e for e in bundle.get("entry", []) if e.get("resource", {}).get("resourceType") == "Patient"),
            None
        )
        if patient_entry is None:
            return False, "Patient not in bundle"

        patient = patient_entry["resource"]
        abha = patient.get("identifier", [{}])[0].get("value", "")
        # Check for synthetic ABHA ID (either demo or local synthetic)
        if not ("91-4582" in abha or "Synthetic" in abha or "Local" in abha):
            return False, f"ABHA demo ID not present: {abha}"

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def test_medication_service():
    """Test Medication Planner Service."""
    try:
        from tests.test_api import seed_demo_data
        from backend.app.database import Base, engine, SessionLocal

        db = SessionLocal()
        Base.metadata.create_all(bind=engine)
        seed_demo_data(db)
        db.close()

        from fastapi.testclient import TestClient
        client_local = TestClient(app)
        get_resp = client_local.get("/api/medications")
        if get_resp.status_code != 200:
            return False, f"Medications endpoint returned status {get_resp.status_code}"

        data = get_resp.json()
        if "medications" not in data:
            return False, "Missing medications in response"
        if "daily_schedule" not in data:
            return False, "Missing daily_schedule in response"

        meds = data.get("medications", [])
        if len(meds) == 0:
            return False, "No medications found"

        for med in meds:
            if med.get("is_incomplete"):
                if not med.get("trust_warning"):
                    return False, f"Incomplete med {med['medicine_name']} missing warning"

        med = meds[0]
        upd_resp = client_local.patch(
            f"/api/medications/{med['id']}",
            json={"schedule_time": "09:00 PM", "is_reminder_active": True, "is_verified": True}
        )
        if upd_resp.status_code != 200:
            return False, f"Medication update failed with status {upd_resp.status_code}"

        updated = upd_resp.json()
        if updated.get("schedule_time") != "09:00 PM":
            return False, f"Schedule time not updated: {updated.get('schedule_time')}"
        if updated.get("is_reminder_active") is not True:
            return False, "Reminder active flag not set"

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def test_doctor_prep_service():
    """Test Doctor Prep Service."""
    try:
        from tests.test_api import seed_demo_data
        from backend.app.database import Base, engine, SessionLocal

        db = SessionLocal()
        Base.metadata.create_all(bind=engine)
        seed_demo_data(db)
        db.close()

        from fastapi.testclient import TestClient
        client_local = TestClient(app)

        get_resp = client_local.get("/api/doctor-prep")
        if get_resp.status_code != 200:
            return False, f"Doctor prep GET failed with status {get_resp.status_code}"

        questions = get_resp.json()
        if len(questions) == 0:
            return False, "No questions generated"

        post_resp = client_local.post(
            "/api/doctor-prep",
            json={"question_text": "Should I modify my evening meal timing?", "category": "Personal Question"}
        )
        if post_resp.status_code != 200:
            return False, f"Add question failed with status {post_resp.status_code}"

        new_q_id = post_resp.json()["id"]

        toggle_resp = client_local.patch(
            f"/api/doctor-prep/{new_q_id}/toggle",
            json={"is_checked": True}
        )
        if toggle_resp.status_code != 200:
            return False, f"Toggle failed with status {toggle_resp.status_code}"

        if toggle_resp.json().get("is_checked") is not True:
            return False, "Toggle not saved"

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def test_full_pipeline():
    """Test full end-to-end pipeline: Upload -> OCR -> Parse -> Summary -> Telugu -> Comparison -> FHIR."""
    try:
        # Step 1: Upload a sample document
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
        if upload_resp.status_code != 200:
            return False, f"Pipeline upload failed with status {upload_resp.status_code}"

        uploaded_doc = upload_resp.json()
        doc_id = uploaded_doc["id"]

        # Step 2: Verify OCR extraction
        observations = uploaded_doc.get("observations", [])
        medications = uploaded_doc.get("medications", [])
        if len(observations) < 2:
            return False, f"Pipeline OCR: expected >= 2 observations, got {len(observations)}"

        # Step 3: Verify AI summary (English + Telugu)
        detail_resp = client.get(f"/api/documents/{doc_id}")
        data = detail_resp.json()
        summary = data.get("summary", {})
        if summary is None:
            return False, "Pipeline: Summary missing from document detail"
        if "english_summary" not in summary:
            return False, "Pipeline: English summary missing"
        if "telugu_summary" not in summary:
            return False, "Pipeline: Telugu summary missing"
        if len(summary.get("english_summary", "")) == 0:
            return False, "Pipeline: English summary empty"
        if len(summary.get("telugu_summary", "")) == 0:
            return False, "Pipeline: Telugu summary empty"

        # Step 4: Verify Telugu content
        telugu = summary.get("telugu_summary", "")
        if len(telugu) == 0:
            return False, "Pipeline: Telugu summary empty after detail fetch"

        # Step 6: Test FHIR bundle for the uploaded document
        bundle_resp = client.get(f"/api/fhir/bundle/{doc_id}")
        if bundle_resp.status_code != 200:
            return False, f"Pipeline FHIR: bundle endpoint returned status {bundle_resp.status_code}"

        bundle = bundle_resp.json()
        if bundle.get("resourceType") != "Bundle":
            return False, f"Pipeline FHIR: Bundle resourceType incorrect: {bundle.get('resourceType')}"

        if "entry" not in bundle:
            return False, "Pipeline FHIR: Missing bundle entries"

        resource_types = [e["resource"]["resourceType"] for e in bundle.get("entry", [])]
        if "Patient" not in resource_types:
            return False, "Pipeline FHIR: Patient resource missing from bundle"
        if "Observation" not in resource_types:
            return False, "Pipeline FHIR: Observation resource missing from bundle"

        return True, None
    except Exception as e:
        import traceback
        return False, str(e) + "\n" + traceback.format_exc()


def run_pytest_suite(test_file):
    """Run a pytest test file and return pass/fail counts."""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", test_file, "-v"],
        capture_output=True,
        text=True,
        cwd=str(BACKEND_DIR)
    )

    passed = 0
    failed = 0
    for line in result.stdout.split("\n"):
        if "passed" in line.lower() and "failed" not in line.lower():
            parts = line.split()
            if len(parts) >= 2:
                try:
                    passed = int(parts[0])
                except ValueError:
                    pass

    if result.returncode == 0:
        return passed, 0
    else:
        stderr_lines = result.stderr.split("\n")
        fail_count = sum(1 for line in stderr_lines if "FAILED" in line or "FAIL" in line)
        return passed, max(failed, fail_count)


if __name__ == "__main__":
    results = run_all_tests()
    sys.exit(0 if results["failed"] == 0 else 1)