"""
MediMitra AI — Comprehensive AI & Telugu Agent
Validates Gemini API flow, deterministic demo mode, bilingual summaries,
medical safety rules, Telugu translation integrity, and multilingual support.
"""

import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.ai_service import AIService, is_demo_mode
from backend.app.services.telugu_service import TeluguHealthTranslator
from backend.app.services.multilingual_service import MultilingualHealthExplainer

from backend.app.database import Base, engine, SessionLocal
from backend.app.data.demo_samples import seed_demo_data
from fastapi.testclient import TestClient
from backend.app.main import app


def run_all_tests():
    """Run comprehensive AI & Telugu validation tests and return detailed results."""
    results = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "tests": [],
        "passed": 0,
        "failed": 0,
        "total": 0,
    }

    # Seed demo data
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    seed_demo_data(db)
    db.close()

    global client
    client = TestClient(app)

    # =====================================================
    # 1. AI Service Tests
    # =====================================================
    print("=" * 70)
    print("1. AI SERVICE VALIDATION")
    print("=" * 70)

    # 1a. Test generate_health_summary
    print("\n[1a] Testing AIService.generate_health_summary()...")
    ai_pass, ai_bug = test_ai_service_generate()
    results["tests"].append({
        "name": "AIService.generate_health_summary()",
        "passed": ai_pass,
        "bug": ai_bug,
    })
    print(f"  >> {'PASS' if ai_pass else f'FAIL - {ai_bug}'}")

    # 1b. Deterministic vs Gemini mode
    print("\n[1b] Validating deterministic vs Gemini API modes...")
    mode_pass, mode_bug = test_deterministic_vs_gemini_mode()
    results["tests"].append({
        "name": "Deterministic vs Gemini Mode",
        "passed": mode_pass,
        "bug": mode_bug,
    })
    print(f"  >> {'PASS' if mode_pass else f'FAIL - {mode_bug}'}")

    # 1c. Medical safety rules
    print("\n[1c] Validating medical safety rules in AI output...")
    safety_pass, safety_bug = test_medical_safety_rules()
    results["tests"].append({
        "name": "Medical Safety Rules",
        "passed": safety_pass,
        "bug": safety_bug,
    })
    print(f"  >> {'PASS' if safety_pass else f'FAIL - {safety_bug}'}")

    # =====================================================
    # 2. Telugu Service Tests
    # =====================================================
    print("\n" + "=" * 70)
    print("2. TELUGU SERVICE VALIDATION")
    print("=" * 70)

    # 2a. Telugu translator
    print("\n[2a] Testing TeluguHealthTranslator.generate_telugu_summary()...")
    te_pass, te_bug = test_telugu_translator()
    results["tests"].append({
        "name": "TeluguHealthTranslator.generate_telugu_summary()",
        "passed": te_pass,
        "bug": te_bug,
    })
    print(f"  >> {'PASS' if te_pass else f'FAIL - {te_bug}'}")

    # 2b. Telugu translation integrity
    print("\n[2b] Testing Telugu translation integrity...")
    integrity_pass, integrity_bug = test_telugu_translation_integrity()
    results["tests"].append({
        "name": "Telugu Translation Integrity",
        "passed": integrity_pass,
        "bug": integrity_bug,
    })
    print(f"  >> {'PASS' if integrity_pass else f'FAIL - {integrity_bug}'}")

    # =====================================================
    # 3. Multilingual Service Tests
    # =====================================================
    print("\n" + "=" * 70)
    print("3. MULTILINGUAL SUPPORT VALIDATION")
    print("=" * 70)

    # 3a. Multilingual all languages
    print("\n[3a] Testing MultilingualHealthExplainer.build() for all languages...")
    multi_pass, multi_bug = test_multilingual_all_languages()
    results["tests"].append({
        "name": "MultilingualHealthExplainer.build() for en, te, hi, ta, kn, ml",
        "passed": multi_pass,
        "bug": multi_bug,
    })
    print(f"  >> {'PASS' if multi_pass else f'FAIL - {multi_bug}'}")

    # =====================================================
    # 4. API Endpoint Tests
    # =====================================================
    print("\n" + "=" * 70)
    print("4. API ENDPOINT VALIDATION")
    print("=" * 70)

    # 4a. /api/voice/ask
    print("\n[4a] Testing /api/voice/ask endpoint...")
    voice_pass, voice_bug = test_voice_ask_endpoint()
    results["tests"].append({
        "name": "/api/voice/ask endpoint",
        "passed": voice_pass,
        "bug": voice_bug,
    })
    print(f"  >> {'PASS' if voice_pass else f'FAIL - {voice_bug}'}")

    # 4b. /api/documents
    print("\n[4b] Testing /api/documents endpoint...")
    docs_pass, docs_bug = test_documents_endpoint()
    results["tests"].append({
        "name": "/api/documents endpoint",
        "passed": docs_pass,
        "bug": docs_bug,
    })
    print(f"  >> {'PASS' if docs_pass else f'FAIL - {docs_bug}'}")

    # =====================================================
    # 5. Summary
    # =====================================================
    print("\n" + "=" * 70)
    print("COMPREHENSIVE RESULTS SUMMARY")
    print("=" * 70)

    for t in results["tests"]:
        if t["passed"]:
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1

    print(f"  Total Tests: {results['total']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")
    if results["total"] > 0:
        print(f"  Success Rate: {results['passed'] / results['total'] * 100:.1f}%")
    else:
        print("  Success Rate: N/A")

    if results["failed"] > 0:
        print(f"\n  Failed Tests:")
        for t in results["tests"]:
            if not t["passed"]:
                print(f"    - {t['name']}: {t['bug']}")
    else:
        print("\n  All tests PASSED!")

    print("\n" + "=" * 70)
    if results["failed"] == 0:
        print("ALL TESTS PASSED - MediMitra AI is healthy!")
    else:
        print(f"SOME TESTS FAILED - {results['failed']} issues need attention")
    print("=" * 70)

    return results


# =============================================================
# Test Implementation
# =============================================================

def test_ai_service_generate():
    """Test AIService.generate_health_summary() with sample observations and medications."""
    try:
        observations = [
            {"test_name": "Fasting Blood Glucose", "original_value": "142.0", "unit": "mg/dL",
             "reference_range_text": "70 - 99 mg/dL", "interpretation": "HIGH"},
            {"test_name": "HbA1c (Glycated Hemoglobin)", "original_value": "7.4", "unit": "%",
             "reference_range_text": "4.0 - 5.6 %", "interpretation": "HIGH"},
            {"test_name": "Serum Creatinine", "original_value": "1.05", "unit": "mg/dL",
             "reference_range_text": "0.7 - 1.3 mg/dL", "interpretation": "NORMAL"},
        ]
        medications = [{"medicine_name": "Metformin", "dosage": "500 mg", "frequency": "ONCE DAILY",
                       "timing_instructions": "After dinner"}]

        summary = AIService.generate_health_summary(
            patient_name="Ramesh Kumar", document_type="Laboratory Report",
            document_date="2025-10-15", observations=observations, medications=medications)

        assert "english_summary" in summary, "English summary missing"
        assert "telugu_summary" in summary, "Telugu summary missing"
        assert "key_findings" in summary, "Key findings missing"
        assert "questions_for_doctor" in summary, "Questions for doctor missing"
        assert "uncertainty_notes" in summary, "Uncertainty notes missing"
        assert "is_demo_generated" in summary, "is_demo_generated missing"

        assert len(summary["english_summary"]) > 0, "English summary empty"
        assert len(summary["telugu_summary"]) > 0, "Telugu summary empty"
        assert len(summary["key_findings"]) > 0, "Key findings empty"
        assert len(summary["questions_for_doctor"]) > 0, "Questions for doctor empty"
        assert len(summary["uncertainty_notes"]) > 0, "Uncertainty notes empty"
        assert "Metformin" in summary["english_summary"], "Medicine name not in English summary"

        return True, None
    except Exception as e:
        return False, str(e)


def test_deterministic_vs_gemini_mode():
    """Validate deterministic vs Gemini API modes."""
    try:
        from backend.app.config import GEMINI_API_KEY, is_demo_mode as cfg_is_demo_mode
        assert cfg_is_demo_mode() == True, "is_demo_mode() should return True without API key"
        assert (GEMINI_API_KEY or "") == "" or (GEMINI_API_KEY or "") == "your_gemini_api_key_here", \
            "Expected no API key in test environment"

        observations = [{"test_name": "Fasting Blood Glucose", "original_value": "142.0", "unit": "mg/dL",
                         "reference_range_text": "70 - 99 mg/dL", "interpretation": "HIGH"}]
        medications = [{"medicine_name": "Metformin", "dosage": "500 mg", "frequency": "ONCE DAILY",
                       "timing_instructions": "After dinner"}]

        summary = AIService.generate_health_summary(
            patient_name="Test User", document_type="Laboratory Report",
            document_date="2026-01-15", observations=observations, medications=medications)

        assert summary.get("is_demo_generated") == True, \
            f"Expected is_demo_generated=True, got {summary.get('is_demo_generated')}"
        assert "english_summary" in summary, "English summary missing in demo mode"
        assert "telugu_summary" in summary, "Telugu summary missing in demo mode"
        assert len(summary["english_summary"]) > 0, "English summary empty in demo mode"
        assert len(summary["telugu_summary"]) > 0, "Telugu summary empty in demo mode"

        return True, None
    except Exception as e:
        return False, str(e)


def test_medical_safety_rules():
    """Validate that AI service adheres to all 7 strict medical safety rules."""
    try:
        observations = [{"test_name": "Fasting Blood Glucose", "original_value": "142.0", "unit": "mg/dL",
                         "reference_range_text": "70 - 99 mg/dL", "interpretation": "HIGH"}]
        medications = [{"medicine_name": "Metformin", "dosage": "500 mg", "frequency": "ONCE DAILY",
                       "timing_instructions": "After dinner"}]

        summary = AIService.generate_health_summary(
            patient_name="Test User", document_type="Laboratory Report",
            document_date="2026-01-15", observations=observations, medications=medications)

        unc = summary["uncertainty_notes"].lower()
        safety = 0
        total = 7

        # Rule 1: INFORMATIONAL ONLY
        if "informational" in unc or "not a substitute" in unc:
            safety += 1
        elif "This summary is not a substitute" in summary["english_summary"]:
            safety += 1

        # Rule 2: NEVER DIAGNOSE
        eng = summary["english_summary"]
        diag = ["you have diabetes", "you have hypertension", "you have chronic kidney disease"]
        if not any(p in eng.lower() for p in diag):
            safety += 1

        # Rule 3: NEVER PRESCRIBE OR CHANGE DOSES
        if "change dose" not in eng.lower() and "change dosage" not in eng.lower():
            safety += 1

        # Rule 4: USE REFERENCE RANGES
        if "reference range" in eng.lower() or "reference interval" in eng.lower():
            safety += 1

        # Rule 5: EXPLAIN MEDICAL TERMS
        if "explained" in eng.lower() or "laboratory" in eng.lower():
            safety += 1

        # Rule 6: TELUGU EXPLANATION
        tel = summary["telugu_summary"]
        if len(tel) > 0 and "Metformin" in tel:
            safety += 1

        # Rule 7: EVIDENCE LINKING
        if len(summary["key_findings"]) > 0:
            for f in summary["key_findings"]:
                if "evidence_excerpt" in f:
                    safety += 1
                    break

        passed = safety == total
        bug = None if passed else f"{safety}/{total} safety rules passed"
        return passed, bug
    except Exception as e:
        return False, str(e)


def test_telugu_translator():
    """Test TeluguHealthTranslator.generate_telugu_summary()."""
    try:
        observations = [
            {"test_name": "Fasting Blood Glucose", "original_value": "142.0", "unit": "mg/dL",
             "reference_range_text": "70 - 99 mg/dL", "interpretation": "HIGH"},
            {"test_name": "Serum Creatinine", "original_value": "1.05", "unit": "mg/dL",
             "reference_range_text": "0.7 - 1.3 mg/dL", "interpretation": "NORMAL"},
        ]
        medications = [{"medicine_name": "Metformin", "dosage": "500 mg", "frequency": "ONCE DAILY",
                       "timing_instructions": "After dinner"}]

        english_summary = (
            "Hello Test User, here is an easy-to-understand breakdown of your Laboratory Report. "
            "Key Findings Requiring Attention:\n• Fasting Blood Glucose: Your level is 142.0 mg/dL, which is higher "
            "than the reference interval provided (70 - 99 mg/dL). This indicates a value outside normal laboratory "
            "limits that your clinician will evaluate.\n\nNormal Findings: Serum Creatinine (1.05 mg/dL) are "
            "all within standard laboratory reference ranges.\n\nPrescriptions Recorded:\n• Metformin (500 mg): "
            "ONCE DAILY - After dinner.\n\nNote: Test results must always be interpreted in the context of your "
            "complete medical history, symptoms, and prior trends. Please discuss these findings with your healthcare provider."
        )

        telugu = TeluguHealthTranslator.generate_telugu_summary(
            patient_name="Test User", observations=observations, medications=medications, english_summary=english_summary)

        assert len(telugu) > 0, "Telugu summary empty"
        has_telugu = any(0x0C00 <= ord(c) <= 0x0C7F for c in telugu)
        assert has_telugu, "Telugu script not found in summary"
        assert "Metformin" in telugu, "Medicine name not preserved in Telugu"
        assert "142.0" in telugu, "Value not preserved in Telugu"
        assert "mg/dL" in telugu, "Unit not preserved in Telugu"
        assert "70 - 99" in telugu, "Reference range not preserved in Telugu"
        assert "⚠️" in telugu or "గమనిక" in telugu, "Telugu disclaimer not present"

        return True, None
    except Exception as e:
        return False, str(e)


def test_telugu_translation_integrity():
    """Test that medicine names, numerical values, units, and dates are preserved unchanged in Telugu output."""
    try:
        observations = [{"test_name": "Fasting Blood Glucose", "original_value": "142.0", "unit": "mg/dL",
                         "reference_range_text": "70 - 99 mg/dL", "interpretation": "HIGH"}]
        medications = [{"medicine_name": "Metformin", "dosage": "500 mg", "frequency": "ONCE DAILY",
                       "timing_instructions": "After dinner"}]

        english_summary = "Hello Test User, here is an easy-to-understand breakdown of your Laboratory Report."

        telugu = TeluguHealthTranslator.generate_telugu_summary(
            patient_name="Ramesh Kumar", observations=observations, medications=medications, english_summary=english_summary)

        assert "Metformin" in telugu, "Medicine name 'Metformin' not preserved in Telugu"
        assert "142.0" in telugu, "Numerical value '142.0' not preserved in Telugu"
        assert "mg/dL" in telugu, "Unit 'mg/dL' not preserved in Telugu"
        assert "70 - 99 mg/dL" in telugu or "70 - 99" in telugu, "Reference range not preserved in Telugu"

        return True, None
    except Exception as e:
        return False, str(e)


def test_multilingual_all_languages():
    """Test MultilingualHealthExplainer.build() for all supported languages: en, te, hi, ta, kn, ml."""
    try:
        observations = [
            {"test_name": "Fasting Blood Glucose", "original_value": "142.0", "unit": "mg/dL",
             "reference_range_text": "70 - 99 mg/dL", "interpretation": "HIGH"},
            {"test_name": "Serum Creatinine", "original_value": "1.05", "unit": "mg/dL",
             "reference_range_text": "0.7 - 1.3 mg/dL", "interpretation": "NORMAL"},
        ]
        medications = [{"medicine_name": "Metformin", "dosage": "500 mg", "frequency": "ONCE DAILY",
                       "timing_instructions": "After dinner"}]

        supported = MultilingualHealthExplainer.supported_languages()
        assert "en" in supported, "English not in supported languages"
        assert "te" in supported, "Telugu not in supported languages"
        assert "hi" in supported, "Hindi not in supported languages"
        assert "ta" in supported, "Tamil not in supported languages"
        assert "kn" in supported, "Kannada not in supported languages"
        assert "ml" in supported, "Malayalam not in supported languages"

        for lang in ["en", "te", "hi", "ta", "kn", "ml"]:
            result = MultilingualHealthExplainer.build(
                language=lang, patient_name="Test User",
                document_type="Laboratory Report", document_date="2026-01-15",
                observations=observations, medications=medications)

            assert "language" in result, f"Language key missing for {lang}"
            assert "summary" in result, f"Summary missing for {lang}"
            assert "key_findings" in result, f"Key findings missing for {lang}"
            assert "questions_for_doctor" in result, f"Questions missing for {lang}"
            assert "uncertainty_notes" in result, f"Uncertainty notes missing for {lang}"
            assert result["language"] == lang, f"Expected language {lang}, got {result['language']}"
            assert len(result["summary"]) > 0, f"Summary empty for {lang}"
            assert len(result["key_findings"]) > 0, f"Key findings empty for {lang}"
            assert len(result["questions_for_doctor"]) > 0, f"Questions empty for {lang}"

            # Language-specific greeting validation
            summary_lang = result["summary"]
            if lang == "en":
                assert "Hello" in summary_lang, "English greeting missing"
            elif lang == "te":
                assert "నమస్కారం" in summary_lang or "Namaste" in summary_lang, "Telugu greeting missing"
            elif lang == "hi":
                assert "नमस्ते" in summary_lang, "Hindi greeting missing"
            elif lang == "ta":
                assert "வணக்கம்" in summary_lang, "Tamil greeting missing"
            elif lang == "kn":
                assert "ನಮಸ್ಕಾರ" in summary_lang, "Kannada greeting missing"
            elif lang == "ml":
                assert "നമസ്കാരം" in summary_lang, "Malayalam greeting missing"

            # Numerical value preserved
            assert "142" in summary_lang or "142.0" in summary_lang, f"Numerical value not preserved in {lang}"

        return True, None
    except Exception as e:
        return False, str(e)


def test_voice_ask_endpoint():
    """Test /api/voice/ask endpoint."""
    try:
        docs_resp = client.get("/api/documents")
        docs = docs_resp.json()
        if len(docs) == 0:
            return False, "No documents found"
        doc_id = docs[0]["id"]

        # English
        resp = client.post("/api/voice/ask", json={"query": "read my report summary", "language": "en", "document_id": doc_id})
        assert resp.status_code == 200, f"voice/ask failed with status {resp.status_code}"
        data = resp.json()
        assert "answer" in data and len(data["answer"]) > 0, "Answer missing/empty"

        # Telugu
        resp_te = client.post("/api/voice/ask", json={"query": "read my report summary", "language": "te", "document_id": doc_id})
        assert resp_te.status_code == 200, f"voice/ask Telugu failed with status {resp_te.status_code}"
        assert "answer" in resp_te.json(), "Answer missing from voice/ask Telugu"

        # Without document
        resp_no = client.post("/api/voice/ask", json={"query": "what is my report?", "language": "en"})
        assert resp_no.status_code == 200, "voice/ask without document failed"
        assert "answer" in resp_no.json(), "Answer missing when no document"

        # Specific test query
        resp_g = client.post("/api/voice/ask", json={"query": "what is my fasting blood glucose?", "language": "en", "document_id": doc_id})
        assert resp_g.status_code == 200, "voice/ask glucose query failed"
        assert "Glucose" in resp_g.json()["answer"], "Glucose not in answer"

        # Medicine query
        resp_m = client.post("/api/voice/ask", json={"query": "show my medicines", "language": "en", "document_id": doc_id})
        assert resp_m.status_code == 200, "voice/ask medicines failed"
        assert "medicine" in resp_m.json()["answer"].lower() or "Medicines" in resp_m.json()["answer"], "Medicines not in answer"

        return True, None
    except Exception as e:
        return False, str(e)


def test_documents_endpoint():
    """Test /api/documents endpoint."""
    try:
        resp = client.get("/api/documents")
        assert resp.status_code == 200, f"documents endpoint failed with status {resp.status_code}"
        data = resp.json()
        assert len(data) >= 1, "Expected at least 1 document"
        for doc in data:
            assert "id" in doc, "Document missing id"
            assert "file_name" in doc, "Document missing file_name"
            assert "observation_count" in doc and doc["observation_count"] > 0, "Document missing observation count"
            assert "medication_count" in doc and doc["medication_count"] > 0, "Document missing medication count"
        return True, None
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    run_all_tests()