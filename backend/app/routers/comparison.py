"""
Health Change Detector comparison endpoint.
Compares two laboratory reports from the same patient with strict unit compatibility.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models import HealthDocument
from backend.app.schemas import ReportComparisonResponse
from backend.app.services.comparison_service import HealthChangeDetectorService

router = APIRouter(prefix="/comparison", tags=["Health Change Detector"])

class ComparisonPayload(BaseModel):
    report_a_id: int
    report_b_id: int

@router.post("", response_model=ReportComparisonResponse)
def compare_reports(payload: ComparisonPayload, db: Session = Depends(get_db)):
    """
    Compares two laboratory reports:
    - Matches compatible tests by identity and units
    - Calculates absolute change, percentage delta, and reference range shift
    - Flags incompatible units as unsafe comparisons
    - Strictly avoids claiming clinical recovery
    """
    doc_a = db.query(HealthDocument).filter(HealthDocument.id == payload.report_a_id).first()
    doc_b = db.query(HealthDocument).filter(HealthDocument.id == payload.report_b_id).first()

    if not doc_a or not doc_b:
        raise HTTPException(status_code=404, detail="One or both selected reports were not found.")

    if doc_a.patient_id != doc_b.patient_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot compare reports belonging to different patients."
        )

    # Order chronologically if dates are available
    date_a = doc_a.document_date or "2025-01-01"
    date_b = doc_b.document_date or "2026-01-01"
    older_doc, newer_doc = (doc_a, doc_b) if date_a <= date_b else (doc_b, doc_a)

    def doc_to_dict(d):
        return {
            "id": d.id,
            "document_date": d.document_date,
            "observations": [
                {
                    "test_name": o.test_name,
                    "original_value": o.original_value,
                    "user_corrected_value": o.user_corrected_value,
                    "standardized_value": o.standardized_value,
                    "unit": o.unit,
                    "reference_range_low": o.reference_range_low,
                    "reference_range_high": o.reference_range_high,
                    "reference_range_text": o.reference_range_text,
                    "interpretation": o.interpretation
                }
                for o in d.observations
            ]
        }

    return HealthChangeDetectorService.compare_reports(
        report_a=doc_to_dict(older_doc),
        report_b=doc_to_dict(newer_doc)
    )
