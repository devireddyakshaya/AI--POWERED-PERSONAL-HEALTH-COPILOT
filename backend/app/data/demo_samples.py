"""
Pre-seeded synthetic healthcare demo data for MediMitra AI.
Clearly labelled as synthetic demonstration data for hackathon evaluation.
Features compatible tests, dates, units, and reference ranges for instant report comparison.
"""
import json
import re
import uuid
from datetime import datetime
from sqlalchemy import func
from backend.app.models import (
    PatientProfile, HealthDocument, ExtractedObservation,
    ExtractedMedication, HealthSummary, DoctorQuestion
)
from backend.app.services.ai_service import AIService
from backend.app.services.doctor_prep_service import DoctorPrepService


def generate_local_abha() -> str:
    """Creates a clearly-marked local record identifier for real (non-demo) patients."""
    return f"HS-{uuid.uuid4().hex[:12].upper()} (Local Record)"


def normalize_patient_name(name) -> str:
    """
    Normalizes a patient name for exact matching only. Whitespace, punctuation
    and case are collapsed, but different names stay different: two patients are
    NEVER merged merely because their names are similar (e.g. "Ramesh Kumar" and
    "Ramesh Kumari" remain separate records).
    """
    if not name:
        return ""
    cleaned = re.sub(r"[^a-z0-9\s]", " ", str(name).lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def get_or_create_patient(
    db,
    full_name,
    age=None,
    gender=None,
    synthetic_abha_id=None,
    external_patient_id=None
) -> PatientProfile:
    """
    Resolves the patient a report belongs to and creates a new record when the
    person has not been seen before.

    Matching rules (ordered):
      1. A printed patient identifier (Patient ID / UHID / MRN) is the strongest
         signal and is matched first.
      2. Otherwise an EXACT normalized full-name match.
    A report without any name or identifier NEVER matches an existing patient, so
    it can never be silently attached to another person's record (e.g. the seeded
    demo profile). Similar-but-different names are never merged.
    """
    name = (full_name or "").strip()
    norm = normalize_patient_name(name)
    external = (external_patient_id or "").strip() or None

    existing = None
    if external:
        existing = (
            db.query(PatientProfile)
            .filter(PatientProfile.external_patient_id == external)
            .first()
        )
    if existing is None and norm:
        for candidate in db.query(PatientProfile).all():
            if normalize_patient_name(candidate.full_name) == norm:
                existing = candidate
                break

    if existing:
        changed = False
        if age and not existing.age:
            existing.age = age
            changed = True
        if gender and not existing.gender:
            existing.gender = gender
            changed = True
        if external and not existing.external_patient_id:
            existing.external_patient_id = external
            changed = True
        if changed:
            db.commit()
            db.refresh(existing)
        return existing

    patient = PatientProfile(
        full_name=name or "Not available",
        age=age,
        gender=gender,
        synthetic_abha_id=synthetic_abha_id or generate_local_abha(),
        external_patient_id=external
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

SYNTHETIC_PATIENT = {
    "full_name": "Ramesh Kumar",
    "age": 48,
    "gender": "Male",
    "synthetic_abha_id": "91-4582-9012-3456 (Synthetic Demo)",
    "external_patient_id": "AK-78291"
}

SYNTHETIC_DOCUMENTS = [
    {
        "file_name": "Aarogyam_Comprehensive_Panel_Oct2025.pdf",
        "file_type": "application/pdf",
        "file_size": 184520,
        "document_type": "Laboratory Report",
        "document_date": "2025-10-15",
        "laboratory_name": "Aarogyam Clinical Pathology & Diagnostic Labs",
        "trust_score": 92,
        "trust_warnings": [
            "Medication 'Multivitamin': Dosage strength and duration missing. Flagged for verification."
        ],
        "is_synthetic": True,
        "raw_text": """
================================================================================
AAROGYAM CLINICAL PATHOLOGY & DIAGNOSTIC LABS
NABH & NABL Accredited | Hyderabad, India
PATIENT REPORT (SYNTHETIC DEMONSTRATION DATA)
--------------------------------------------------------------------------------
Patient Name: Ramesh Kumar                 Age: 48 Yrs / Male
Patient ID: AK-78291                      Date of Collection: 2025-10-15
Ref. Doctor: Dr. S. Rao, MD (Medicine)   Report Status: Final
--------------------------------------------------------------------------------
TEST NAME                           RESULT   UNIT       REFERENCE INTERVAL
--------------------------------------------------------------------------------
Fasting Blood Glucose               142.0    mg/dL      70.0 - 99.0
HbA1c (Glycated Hemoglobin)         7.4      %          4.0 - 5.6
Total Cholesterol                   228.0    mg/dL      < 200.0
Triglycerides                       198.0    mg/dL      < 150.0
HDL Cholesterol                     38.0     mg/dL      > 40.0
Serum Creatinine                    1.05     mg/dL      0.7 - 1.3
Hemoglobin (Hb)                     14.2     g/dL       13.0 - 17.0
Total Leukocyte Count (WBC)         7200     /cumm      4000 - 11000
Platelet Count                      2.4      lakh/cumm  1.5 - 4.5
--------------------------------------------------------------------------------
ADVICE / PRESCRIPTIONS NOTED:
Rx:
1. Tab Metformin 500mg Once Daily after dinner for 3 months
2. Tab Multivitamin Daily
================================================================================
""",
        "observations": [
            {
                "test_name": "Fasting Blood Glucose",
                "standardized_code": "1558-6",
                "original_value": "142.0",
                "standardized_value": 142.0,
                "unit": "mg/dL",
                "reference_range_low": 70.0,
                "reference_range_high": 99.0,
                "reference_range_text": "70 - 99 mg/dL",
                "interpretation": "HIGH",
                "is_verified": True,
                "evidence_excerpt": "Fasting Blood Glucose 142.0 mg/dL 70.0 - 99.0",
                "page_number": 1,
                "confidence_score": 0.96
            },
            {
                "test_name": "HbA1c (Glycated Hemoglobin)",
                "standardized_code": "4548-4",
                "original_value": "7.4",
                "standardized_value": 7.4,
                "unit": "%",
                "reference_range_low": 4.0,
                "reference_range_high": 5.6,
                "reference_range_text": "4.0 - 5.6 %",
                "interpretation": "HIGH",
                "is_verified": True,
                "evidence_excerpt": "HbA1c (Glycated Hemoglobin) 7.4 % 4.0 - 5.6",
                "page_number": 1,
                "confidence_score": 0.97
            },
            {
                "test_name": "Total Cholesterol",
                "standardized_code": "2093-3",
                "original_value": "228.0",
                "standardized_value": 228.0,
                "unit": "mg/dL",
                "reference_range_low": 125.0,
                "reference_range_high": 200.0,
                "reference_range_text": "< 200 mg/dL",
                "interpretation": "HIGH",
                "is_verified": True,
                "evidence_excerpt": "Total Cholesterol 228.0 mg/dL < 200.0",
                "page_number": 1,
                "confidence_score": 0.95
            },
            {
                "test_name": "Triglycerides",
                "standardized_code": "2571-8",
                "original_value": "198.0",
                "standardized_value": 198.0,
                "unit": "mg/dL",
                "reference_range_low": 50.0,
                "reference_range_high": 150.0,
                "reference_range_text": "< 150 mg/dL",
                "interpretation": "HIGH",
                "is_verified": True,
                "evidence_excerpt": "Triglycerides 198.0 mg/dL < 150.0",
                "page_number": 1,
                "confidence_score": 0.94
            },
            {
                "test_name": "HDL Cholesterol",
                "standardized_code": "2085-9",
                "original_value": "38.0",
                "standardized_value": 38.0,
                "unit": "mg/dL",
                "reference_range_low": 40.0,
                "reference_range_high": 60.0,
                "reference_range_text": "> 40 mg/dL",
                "interpretation": "LOW",
                "is_verified": True,
                "evidence_excerpt": "HDL Cholesterol 38.0 mg/dL > 40.0",
                "page_number": 1,
                "confidence_score": 0.93
            },
            {
                "test_name": "Serum Creatinine",
                "standardized_code": "2160-0",
                "original_value": "1.05",
                "standardized_value": 1.05,
                "unit": "mg/dL",
                "reference_range_low": 0.7,
                "reference_range_high": 1.3,
                "reference_range_text": "0.7 - 1.3 mg/dL",
                "interpretation": "NORMAL",
                "is_verified": True,
                "evidence_excerpt": "Serum Creatinine 1.05 mg/dL 0.7 - 1.3",
                "page_number": 1,
                "confidence_score": 0.98
            },
            {
                "test_name": "Hemoglobin (Hb)",
                "standardized_code": "718-7",
                "original_value": "14.2",
                "standardized_value": 14.2,
                "unit": "g/dL",
                "reference_range_low": 13.0,
                "reference_range_high": 17.0,
                "reference_range_text": "13.0 - 17.0 g/dL",
                "interpretation": "NORMAL",
                "is_verified": True,
                "evidence_excerpt": "Hemoglobin (Hb) 14.2 g/dL 13.0 - 17.0",
                "page_number": 1,
                "confidence_score": 0.99
            }
        ],
        "medications": [
            {
                "medicine_name": "Metformin",
                "dosage": "500 mg",
                "frequency": "ONCE DAILY",
                "timing_instructions": "After dinner",
                "duration": "3 months",
                "is_incomplete": False,
                "trust_warning": None,
                "is_verified": True,
                "schedule_time": "08:30 PM",
                "is_reminder_active": True,
                "evidence_excerpt": "Tab Metformin 500mg Once Daily after dinner for 3 months"
            },
            {
                "medicine_name": "Multivitamin",
                "dosage": None,
                "frequency": "DAILY",
                "timing_instructions": "As directed",
                "duration": "Unspecified",
                "is_incomplete": True,
                "trust_warning": "Dosage strength and duration missing. Flagged for verification.",
                "is_verified": False,
                "schedule_time": "09:00 AM",
                "is_reminder_active": False,
                "evidence_excerpt": "Tab Multivitamin Daily"
            }
        ]
    },
    {
        "file_name": "Aarogyam_Metabolic_FollowUp_Jan2026.pdf",
        "file_type": "application/pdf",
        "file_size": 172340,
        "document_type": "Laboratory Report",
        "document_date": "2026-01-20",
        "laboratory_name": "Aarogyam Clinical Pathology & Diagnostic Labs",
        "trust_score": 96,
        "trust_warnings": [],
        "is_synthetic": True,
        "raw_text": """
================================================================================
AAROGYAM CLINICAL PATHOLOGY & DIAGNOSTIC LABS
NABH & NABL Accredited | Hyderabad, India
PATIENT REPORT (SYNTHETIC DEMONSTRATION DATA)
--------------------------------------------------------------------------------
Patient Name: Ramesh Kumar                 Age: 48 Yrs / Male
Patient ID: AK-78291                      Date of Collection: 2026-01-20
Ref. Doctor: Dr. S. Rao, MD (Medicine)   Report Status: Final (Follow-Up)
--------------------------------------------------------------------------------
TEST NAME                           RESULT   UNIT       REFERENCE INTERVAL
--------------------------------------------------------------------------------
Fasting Blood Glucose               118.0    mg/dL      70.0 - 99.0
HbA1c (Glycated Hemoglobin)         6.8      %          4.0 - 5.6
Total Cholesterol                   188.0    mg/dL      < 200.0
Triglycerides                       154.0    mg/dL      < 150.0
HDL Cholesterol                     43.0     mg/dL      > 40.0
Serum Creatinine                    0.96     mg/dL      0.7 - 1.3
Hemoglobin (Hb)                     14.4     g/dL       13.0 - 17.0
--------------------------------------------------------------------------------
ADVICE / PRESCRIPTIONS NOTED:
Rx:
1. Tab Metformin 500mg Once Daily after dinner
2. Tab Atorvastatin 10mg Once Daily at bedtime
================================================================================
""",
        "observations": [
            {
                "test_name": "Fasting Blood Glucose",
                "standardized_code": "1558-6",
                "original_value": "118.0",
                "standardized_value": 118.0,
                "unit": "mg/dL",
                "reference_range_low": 70.0,
                "reference_range_high": 99.0,
                "reference_range_text": "70 - 99 mg/dL",
                "interpretation": "HIGH",
                "is_verified": True,
                "evidence_excerpt": "Fasting Blood Glucose 118.0 mg/dL 70.0 - 99.0",
                "page_number": 1,
                "confidence_score": 0.98
            },
            {
                "test_name": "HbA1c (Glycated Hemoglobin)",
                "standardized_code": "4548-4",
                "original_value": "6.8",
                "standardized_value": 6.8,
                "unit": "%",
                "reference_range_low": 4.0,
                "reference_range_high": 5.6,
                "reference_range_text": "4.0 - 5.6 %",
                "interpretation": "HIGH",
                "is_verified": True,
                "evidence_excerpt": "HbA1c (Glycated Hemoglobin) 6.8 % 4.0 - 5.6",
                "page_number": 1,
                "confidence_score": 0.98
            },
            {
                "test_name": "Total Cholesterol",
                "standardized_code": "2093-3",
                "original_value": "188.0",
                "standardized_value": 188.0,
                "unit": "mg/dL",
                "reference_range_low": 125.0,
                "reference_range_high": 200.0,
                "reference_range_text": "< 200 mg/dL",
                "interpretation": "NORMAL",
                "is_verified": True,
                "evidence_excerpt": "Total Cholesterol 188.0 mg/dL < 200.0",
                "page_number": 1,
                "confidence_score": 0.98
            },
            {
                "test_name": "Triglycerides",
                "standardized_code": "2571-8",
                "original_value": "154.0",
                "standardized_value": 154.0,
                "unit": "mg/dL",
                "reference_range_low": 50.0,
                "reference_range_high": 150.0,
                "reference_range_text": "< 150 mg/dL",
                "interpretation": "HIGH",
                "is_verified": True,
                "evidence_excerpt": "Triglycerides 154.0 mg/dL < 150.0",
                "page_number": 1,
                "confidence_score": 0.97
            },
            {
                "test_name": "HDL Cholesterol",
                "standardized_code": "2085-9",
                "original_value": "43.0",
                "standardized_value": 43.0,
                "unit": "mg/dL",
                "reference_range_low": 40.0,
                "reference_range_high": 60.0,
                "reference_range_text": "> 40 mg/dL",
                "interpretation": "NORMAL",
                "is_verified": True,
                "evidence_excerpt": "HDL Cholesterol 43.0 mg/dL > 40.0",
                "page_number": 1,
                "confidence_score": 0.97
            },
            {
                "test_name": "Serum Creatinine",
                "standardized_code": "2160-0",
                "original_value": "0.96",
                "standardized_value": 0.96,
                "unit": "mg/dL",
                "reference_range_low": 0.7,
                "reference_range_high": 1.3,
                "reference_range_text": "0.7 - 1.3 mg/dL",
                "interpretation": "NORMAL",
                "is_verified": True,
                "evidence_excerpt": "Serum Creatinine 0.96 mg/dL 0.7 - 1.3",
                "page_number": 1,
                "confidence_score": 0.99
            },
            {
                "test_name": "Hemoglobin (Hb)",
                "standardized_code": "718-7",
                "original_value": "14.4",
                "standardized_value": 14.4,
                "unit": "g/dL",
                "reference_range_low": 13.0,
                "reference_range_high": 17.0,
                "reference_range_text": "13.0 - 17.0 g/dL",
                "interpretation": "NORMAL",
                "is_verified": True,
                "evidence_excerpt": "Hemoglobin (Hb) 14.4 g/dL 13.0 - 17.0",
                "page_number": 1,
                "confidence_score": 0.99
            }
        ],
        "medications": [
            {
                "medicine_name": "Metformin",
                "dosage": "500 mg",
                "frequency": "ONCE DAILY",
                "timing_instructions": "After dinner",
                "duration": "Ongoing",
                "is_incomplete": False,
                "trust_warning": None,
                "is_verified": True,
                "schedule_time": "08:30 PM",
                "is_reminder_active": True,
                "evidence_excerpt": "Tab Metformin 500mg Once Daily after dinner"
            },
            {
                "medicine_name": "Atorvastatin",
                "dosage": "10 mg",
                "frequency": "ONCE DAILY",
                "timing_instructions": "At bedtime",
                "duration": "Ongoing",
                "is_incomplete": False,
                "trust_warning": None,
                "is_verified": True,
                "schedule_time": "09:30 PM",
                "is_reminder_active": True,
                "evidence_excerpt": "Tab Atorvastatin 10mg Once Daily at bedtime"
            }
        ]
    }
]

def seed_demo_data(db):
    """
    Populates SQLite database with initial synthetic patient and demo laboratory records
    if the database is currently empty.
    """
    existing_patient = db.query(PatientProfile).first()
    if existing_patient:
        return existing_patient

    patient = PatientProfile(
        full_name=SYNTHETIC_PATIENT["full_name"],
        age=SYNTHETIC_PATIENT["age"],
        gender=SYNTHETIC_PATIENT["gender"],
        synthetic_abha_id=SYNTHETIC_PATIENT["synthetic_abha_id"],
        external_patient_id=SYNTHETIC_PATIENT.get("external_patient_id")
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    for doc_data in SYNTHETIC_DOCUMENTS:
        doc = HealthDocument(
            patient_id=patient.id,
            file_name=doc_data["file_name"],
            file_type=doc_data["file_type"],
            file_size=doc_data["file_size"],
            document_type=doc_data["document_type"],
            specialty=doc_data.get("specialty", "General Medicine"),
            document_date=doc_data["document_date"],
            laboratory_name=doc_data["laboratory_name"],
            raw_text=doc_data["raw_text"],
            page_count=1,
            trust_score=doc_data["trust_score"],
            trust_warnings=json.dumps(doc_data["trust_warnings"]),
            is_synthetic=True
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Observations
        for obs_d in doc_data["observations"]:
            obs = ExtractedObservation(
                document_id=doc.id,
                test_name=obs_d["test_name"],
                standardized_code=obs_d.get("standardized_code"),
                original_value=obs_d["original_value"],
                standardized_value=obs_d["standardized_value"],
                unit=obs_d["unit"],
                reference_range_low=obs_d["reference_range_low"],
                reference_range_high=obs_d["reference_range_high"],
                reference_range_text=obs_d["reference_range_text"],
                interpretation=obs_d["interpretation"],
                is_verified=obs_d["is_verified"],
                evidence_excerpt=obs_d["evidence_excerpt"],
                page_number=obs_d["page_number"],
                confidence_score=obs_d["confidence_score"]
            )
            db.add(obs)

        # Medications
        for med_d in doc_data["medications"]:
            med = ExtractedMedication(
                document_id=doc.id,
                medicine_name=med_d["medicine_name"],
                dosage=med_d["dosage"],
                frequency=med_d["frequency"],
                timing_instructions=med_d["timing_instructions"],
                duration=med_d["duration"],
                is_incomplete=med_d["is_incomplete"],
                trust_warning=med_d["trust_warning"],
                is_verified=med_d["is_verified"],
                schedule_time=med_d["schedule_time"],
                is_reminder_active=med_d["is_reminder_active"],
                evidence_excerpt=med_d["evidence_excerpt"]
            )
            db.add(med)

        db.commit()

        # Generate and save HealthSummary
        summary_dict = AIService.generate_health_summary(
            patient_name=patient.full_name,
            document_type=doc.document_type,
            document_date=doc.document_date,
            observations=doc_data["observations"],
            medications=doc_data["medications"],
            raw_text=doc.raw_text
        )

        summary = HealthSummary(
            document_id=doc.id,
            english_summary=summary_dict["english_summary"],
            telugu_summary=summary_dict["telugu_summary"],
            key_findings=json.dumps(summary_dict.get("key_findings", [])),
            questions_for_doctor=json.dumps(summary_dict.get("questions_for_doctor", [])),
            uncertainty_notes=summary_dict.get("uncertainty_notes"),
            is_demo_generated=True
        )
        db.add(summary)

        # Generate Doctor Questions
        doc_questions = DoctorPrepService.generate_questions_for_document(
            observations=doc_data["observations"],
            medications=doc_data["medications"],
            doc_date=doc.document_date
        )
        for q in doc_questions:
            dq = DoctorQuestion(
                patient_id=patient.id,
                source_document_id=doc.id,
                question_text=q["question_text"],
                context_note=q["context_note"],
                category=q["category"]
            )
            db.add(dq)

        db.commit()

    return patient
