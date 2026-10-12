"""
AI Health Explanation and Telugu translation routes for MediMitra AI.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import HealthDocument, HealthSummary
from backend.app.schemas import HealthSummaryOut
from backend.app.services.ai_service import AIService
from backend.app.services.multilingual_service import MultilingualHealthExplainer

router = APIRouter(prefix="/analysis", tags=["AI Explainer"])


@router.get("/languages")
def list_supported_languages():
    """Returns the languages supported by the multilingual health explainer."""
    return {"languages": MultilingualHealthExplainer.supported_languages()}


@router.get("/explain/{document_id}")
def explain_document(document_id: int, language: str = "en", db: Session = Depends(get_db)):
    """
    Returns a concise, localized, evidence-based explanation of a report in the
    requested language (en, te, hi, ta, kn, ml). Uses only values present in the
    uploaded report - no invented data. Ideal for the voice assistant readout.
    """
    doc = db.query(HealthDocument).filter(HealthDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    obs_dicts = [
        {
            "test_name": o.test_name,
            "original_value": o.user_corrected_value or o.original_value,
            "unit": o.unit,
            "reference_range_text": o.reference_range_text,
            "interpretation": o.interpretation,
            "confidence_score": o.confidence_score,
            "evidence_excerpt": o.evidence_excerpt
        }
        for o in doc.observations
    ]

    med_dicts = [
        {
            "medicine_name": m.medicine_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "timing_instructions": m.timing_instructions
        }
        for m in doc.medications
    ]

    return MultilingualHealthExplainer.build(
        language=language,
        patient_name=doc.patient.full_name if doc.patient else "Patient",
        document_type=doc.document_type,
        document_date=doc.document_date or "",
        observations=obs_dicts,
        medications=med_dicts
    )

@router.get("/summary/{document_id}", response_model=HealthSummaryOut)
def get_document_summary(document_id: int, db: Session = Depends(get_db)):
    """
    Fetches the plain English and Telugu summary with key evidence findings.
    """
    summary = db.query(HealthSummary).filter(HealthSummary.document_id == document_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Health summary not found for this document")

    return HealthSummaryOut(
        id=summary.id,
        document_id=summary.document_id,
        english_summary=summary.english_summary,
        telugu_summary=summary.telugu_summary,
        key_findings=summary.get_findings(),
        questions_for_doctor=summary.get_questions(),
        uncertainty_notes=summary.uncertainty_notes,
        is_demo_generated=summary.is_demo_generated,
        created_at=summary.created_at
    )

@router.post("/regenerate/{document_id}", response_model=HealthSummaryOut)
def regenerate_summary(document_id: int, db: Session = Depends(get_db)):
    """
    Regenerates the AI summary and Telugu translation using current observations.
    """
    doc = db.query(HealthDocument).filter(HealthDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    obs_dicts = [
        {
            "test_name": o.test_name,
            "original_value": o.user_corrected_value or o.original_value,
            "unit": o.unit,
            "reference_range_text": o.reference_range_text,
            "interpretation": o.interpretation,
            "confidence_score": o.confidence_score,
            "evidence_excerpt": o.evidence_excerpt
        }
        for o in doc.observations
    ]

    med_dicts = [
        {
            "medicine_name": m.medicine_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "timing_instructions": m.timing_instructions
        }
        for m in doc.medications
    ]

    new_sum = AIService.generate_health_summary(
        patient_name=doc.patient.full_name,
        document_type=doc.document_type,
        document_date=doc.document_date or "Current",
        observations=obs_dicts,
        medications=med_dicts,
        raw_text=doc.raw_text or ""
    )

    summary = db.query(HealthSummary).filter(HealthSummary.document_id == document_id).first()
    if not summary:
        import json
        summary = HealthSummary(
            document_id=doc.id,
            english_summary=new_sum["english_summary"],
            telugu_summary=new_sum["telugu_summary"],
            key_findings=json.dumps(new_sum.get("key_findings", [])),
            questions_for_doctor=json.dumps(new_sum.get("questions_for_doctor", [])),
            uncertainty_notes=new_sum.get("uncertainty_notes"),
            is_demo_generated=new_sum.get("is_demo_generated", False)
        )
        db.add(summary)
    else:
        import json
        summary.english_summary = new_sum["english_summary"]
        summary.telugu_summary = new_sum["telugu_summary"]
        summary.key_findings = json.dumps(new_sum.get("key_findings", []))
        summary.questions_for_doctor = json.dumps(new_sum.get("questions_for_doctor", []))
        summary.uncertainty_notes = new_sum.get("uncertainty_notes")
        summary.is_demo_generated = new_sum.get("is_demo_generated", False)

    db.commit()
    db.refresh(summary)

    return HealthSummaryOut(
        id=summary.id,
        document_id=summary.document_id,
        english_summary=summary.english_summary,
        telugu_summary=summary.telugu_summary,
        key_findings=summary.get_findings(),
        questions_for_doctor=summary.get_questions(),
        uncertainty_notes=summary.uncertainty_notes,
        is_demo_generated=summary.is_demo_generated,
        created_at=summary.created_at
    )
