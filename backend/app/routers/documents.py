"""
Document management, file upload, OCR pipeline, and observation review endpoints.
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import (
    PatientProfile, HealthDocument, ExtractedObservation,
    ExtractedMedication, HealthSummary, DoctorQuestion, ReportComparison
)
from backend.app.schemas import (
    DocumentSummaryOut, DocumentDetailOut, ObservationOut, ObservationCorrection
)
from backend.app.services.ocr_service import OCRService
from backend.app.services.parser_service import MedicalParserService
from backend.app.services.ai_service import AIService
from backend.app.services.doctor_prep_service import DoctorPrepService
from backend.app.data.demo_samples import seed_demo_data, get_or_create_patient

router = APIRouter(prefix="/documents", tags=["Documents & OCR"])

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".txt"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB limit for safety


@router.get("", response_model=List[DocumentSummaryOut])
def list_documents(patient_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Returns uploaded medical documents in chronological order.
    When patient_id is supplied, only that patient's documents are returned so
    one patient's records are never mixed with another's.
    """
    query = db.query(HealthDocument)
    if patient_id is not None:
        query = query.filter(HealthDocument.patient_id == patient_id)
    docs = query.order_by(HealthDocument.document_date.desc(), HealthDocument.created_at.desc()).all()
    
    results = []
    for d in docs:
        results.append(DocumentSummaryOut(
            id=d.id,
            patient_id=d.patient_id,
            file_name=d.file_name,
            file_type=d.file_type,
            file_size=d.file_size,
            document_type=d.document_type,
            specialty=d.specialty,
            document_date=d.document_date,
            laboratory_name=d.laboratory_name,
            page_count=d.page_count,
            trust_score=d.trust_score,
            trust_warnings=d.get_warnings_list(),
            is_synthetic=d.is_synthetic,
            created_at=d.created_at,
            observation_count=len(d.observations),
            medication_count=len(d.medications)
        ))
    return results


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Returns full details of a specific document including observations,
    medications, trust checks, and AI summary.
    """
    doc = db.query(HealthDocument).filter(HealthDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    summary_out = None
    if doc.summary:
        summary_out = {
            "id": doc.summary.id,
            "document_id": doc.summary.document_id,
            "english_summary": doc.summary.english_summary,
            "telugu_summary": doc.summary.telugu_summary,
            "key_findings": doc.summary.get_findings(),
            "questions_for_doctor": doc.summary.get_questions(),
            "uncertainty_notes": doc.summary.uncertainty_notes,
            "is_demo_generated": doc.summary.is_demo_generated,
            "created_at": doc.summary.created_at
        }

    return DocumentDetailOut(
        id=doc.id,
        patient_id=doc.patient_id,
        file_name=doc.file_name,
        file_type=doc.file_type,
        file_size=doc.file_size,
        document_type=doc.document_type,
        specialty=doc.specialty,
        document_date=doc.document_date,
        laboratory_name=doc.laboratory_name,
        raw_text=doc.raw_text,
        page_count=doc.page_count,
        trust_score=doc.trust_score,
        trust_warnings=doc.get_warnings_list(),
        is_synthetic=doc.is_synthetic,
        created_at=doc.created_at,
        observations=doc.observations,
        medications=doc.medications,
        summary=summary_out
    )


@router.post("/upload", response_model=DocumentDetailOut)
async def upload_document(
    file: UploadFile = File(...),
    document_type_override: Optional[str] = Form(None),
    patient_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Uploads a PDF or image medical document, executes the OCR and extraction pipeline,
    generates plain English and Telugu summaries with evidence linking, and saves structured records.
    """
    # 1. Validation
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum permitted limit (15MB)."
        )

    ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS and "pdf" not in (file.content_type or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: PDF, JPG, JPEG, PNG."
        )

    # 2. OCR & Text Extraction
    ocr_result = OCRService.extract_from_file(
        file_bytes=file_bytes,
        file_name=file.filename,
        content_type=file.content_type or "application/octet-stream"
    )

    raw_text = ocr_result.get("raw_text", "")
    page_count = ocr_result.get("page_count", 1)
    ocr_warnings = ocr_result.get("trust_warnings", [])

    # 3. Medical Entity Parsing
    parsed = MedicalParserService.parse_document(raw_text)
    meta = parsed["metadata"]
    doc_type = document_type_override or meta["document_type"]

    # Attach the report to the correct patient. When the caller explicitly
    # selects a patient, use that profile; otherwise create/find one from the
    # report itself rather than a single shared demo profile.
    patient = None
    if patient_id is not None:
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if patient is None:
        patient = get_or_create_patient(
            db,
            meta.get("patient_name"),
            age=meta.get("patient_age"),
            gender=meta.get("patient_gender")
        )

    combined_warnings = ocr_warnings + parsed["trust_warnings"]
    final_trust_score = max(25, parsed["trust_score"] - (len(ocr_warnings) * 10))

    # 4. Save Document Record
    doc = HealthDocument(
        patient_id=patient.id,
        file_name=file.filename,
        file_type=file.content_type or "application/pdf",
        file_size=len(file_bytes),
        document_type=doc_type,
        specialty=meta.get("specialty", "General Medicine"),
        document_date=meta.get("document_date"),
        laboratory_name=meta.get("laboratory_name"),
        raw_text=raw_text,
        page_count=page_count,
        trust_score=final_trust_score,
        trust_warnings=json.dumps(combined_warnings),
        is_synthetic=False
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 5. Save Extracted Observations
    for obs_data in parsed["observations"]:
        obs = ExtractedObservation(
            document_id=doc.id,
            test_name=obs_data["test_name"],
            standardized_code=obs_data.get("standardized_code"),
            original_value=obs_data["original_value"],
            standardized_value=obs_data.get("standardized_value"),
            unit=obs_data.get("unit"),
            reference_range_low=obs_data.get("reference_range_low"),
            reference_range_high=obs_data.get("reference_range_high"),
            reference_range_text=obs_data.get("reference_range_text"),
            interpretation=obs_data.get("interpretation", "UNCERTAIN"),
            is_verified=False,
            evidence_excerpt=obs_data.get("evidence_excerpt"),
            page_number=1,
            confidence_score=obs_data.get("confidence_score", 0.90),
            trust_notes=obs_data.get("trust_notes")
        )
        db.add(obs)

    # 6. Save Extracted Medications
    for med_data in parsed["medications"]:
        med = ExtractedMedication(
            document_id=doc.id,
            medicine_name=med_data["medicine_name"],
            dosage=med_data.get("dosage"),
            frequency=med_data.get("frequency"),
            timing_instructions=med_data.get("timing_instructions"),
            duration=med_data.get("duration"),
            is_incomplete=med_data.get("is_incomplete", False),
            trust_warning=med_data.get("trust_warning"),
            is_verified=False,
            schedule_time=med_data.get("schedule_time", "08:00 AM"),
            is_reminder_active=False,
            evidence_excerpt=med_data.get("evidence_excerpt")
        )
        db.add(med)

    db.commit()

    # 7. Generate AI Explanations & Doctor Prep Questions
    summary_dict = AIService.generate_health_summary(
        patient_name=patient.full_name,
        document_type=doc.document_type,
        document_date=doc.document_date,
        observations=parsed["observations"],
        medications=parsed["medications"],
        raw_text=raw_text
    )

    summary = HealthSummary(
        document_id=doc.id,
        english_summary=summary_dict["english_summary"],
        telugu_summary=summary_dict["telugu_summary"],
        key_findings=json.dumps(summary_dict.get("key_findings", [])),
        questions_for_doctor=json.dumps(summary_dict.get("questions_for_doctor", [])),
        uncertainty_notes=summary_dict.get("uncertainty_notes"),
        is_demo_generated=summary_dict.get("is_demo_generated", False)
    )
    db.add(summary)

    doc_questions = DoctorPrepService.generate_questions_for_document(
        observations=parsed["observations"],
        medications=parsed["medications"],
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
    db.refresh(doc)

    return get_document(doc.id, db)


@router.put("/{document_id}/observations/{observation_id}", response_model=ObservationOut)
def correct_observation(
    document_id: int,
    observation_id: int,
    payload: ObservationCorrection,
    db: Session = Depends(get_db)
):
    """
    Smart Report Trust Check: Allows user to record a manual correction.
    Preserves the original extracted value and records the corrected value separately.
    """
    obs = db.query(ExtractedObservation).filter(
        ExtractedObservation.id == observation_id,
        ExtractedObservation.document_id == document_id
    ).first()

    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")

    obs.user_corrected_value = payload.user_corrected_value
    obs.is_verified = True

    try:
        obs.standardized_value = float(payload.user_corrected_value)
        # Re-evaluate interpretation based on new value
        if obs.reference_range_low is not None and obs.reference_range_high is not None:
            if obs.standardized_value > obs.reference_range_high:
                obs.interpretation = "HIGH"
            elif obs.standardized_value < obs.reference_range_low:
                obs.interpretation = "LOW"
            else:
                obs.interpretation = "NORMAL"
    except Exception:
        pass

    db.commit()
    db.refresh(obs)
    return obs


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Privacy-First Vault: Permanently deletes a medical document and all related
    extracted observations, medications, summaries, and questions.
    """
    doc = db.query(HealthDocument).filter(HealthDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Also delete associated doctor questions
    db.query(DoctorQuestion).filter(DoctorQuestion.source_document_id == document_id).delete()

    db.delete(doc)
    db.commit()

    return {
        "success": True,
        "message": f"Document ID {document_id} and all associated extracted data were permanently purged."
    }


@router.post("/clear-all")
def clear_all_records(db: Session = Depends(get_db)):
    """
    Privacy-First Vault: Permanently deletes ALL medical data (documents, observations,
    medications, summaries, comparisons, doctor questions and patient profiles).
    Unlike /reset-demo, this does NOT restore any synthetic demo records.
    """
    db.query(DoctorQuestion).delete()
    db.query(ReportComparison).delete()
    db.query(ExtractedObservation).delete()
    db.query(ExtractedMedication).delete()
    db.query(HealthSummary).delete()
    db.query(HealthDocument).delete()
    db.query(PatientProfile).delete()
    db.commit()

    return {
        "success": True,
        "message": "All medical records were permanently deleted. No demo data was restored."
    }


@router.post("/reset-demo")
def reset_demo_database(db: Session = Depends(get_db)):
    """
    Resets the database and restores clean synthetic demo records.
    """
    db.query(DoctorQuestion).delete()
    db.query(ReportComparison).delete()
    db.query(ExtractedObservation).delete()
    db.query(ExtractedMedication).delete()
    db.query(HealthSummary).delete()
    db.query(HealthDocument).delete()
    db.query(PatientProfile).delete()
    db.commit()

    patient = seed_demo_data(db)
    return {
        "success": True,
        "message": "Database reset to clean synthetic demo state.",
        "patient_name": patient.full_name
    }
