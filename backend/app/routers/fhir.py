"""
ABDM / FHIR R4 Interoperability endpoints.
Exposes standardized FHIR JSON representations for demonstration of India ABDM readiness.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models import HealthDocument, PatientProfile
from backend.app.schemas import PatientProfileOut
from backend.app.services.fhir_service import FHIRConverterService

router = APIRouter(prefix="/fhir", tags=["ABDM / FHIR Interoperability"])


class PatientProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

@router.get("/patient", response_model=PatientProfileOut)
def get_patient_profile(db: Session = Depends(get_db)):
    """
    Returns the active patient profile. Returns 404 when no patient records exist.
    """
    patient = db.query(PatientProfile).order_by(PatientProfile.id.asc()).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="No patient profile available")

    doc_count = db.query(HealthDocument).filter(HealthDocument.patient_id == patient.id).count()

    return PatientProfileOut(
        id=patient.id,
        synthetic_abha_id=patient.synthetic_abha_id or "Local Record",
        full_name=patient.full_name,
        age=patient.age,
        gender=patient.gender,
        total_documents=doc_count,
        created_at=patient.created_at
    )

@router.patch("/patient", response_model=PatientProfileOut)
def update_patient_profile(
    payload: PatientProfileUpdate,
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Updates a patient profile (name, age, gender). When patient_id is supplied
    that specific patient is updated; otherwise the first patient is used.
    Used by onboarding and the patient switcher so the copilot addresses the
    correct person.
    """
    if patient_id is not None:
        patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    else:
        patient = db.query(PatientProfile).order_by(PatientProfile.id.asc()).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="No patient profile available to update")

    if payload.full_name is not None:
        patient.full_name = payload.full_name.strip()[:100] or patient.full_name
    if payload.age is not None:
        patient.age = max(0, min(130, payload.age))
    if payload.gender is not None:
        patient.gender = payload.gender.strip()[:20] or patient.gender
    db.commit()
    db.refresh(patient)

    doc_count = db.query(HealthDocument).filter(HealthDocument.patient_id == patient.id).count()
    return PatientProfileOut(
        id=patient.id,
        synthetic_abha_id=patient.synthetic_abha_id or "Local Record",
        full_name=patient.full_name,
        age=patient.age,
        gender=patient.gender,
        total_documents=doc_count,
        created_at=patient.created_at
    )


@router.get("/bundle/{document_id}")
def get_fhir_bundle(document_id: int, db: Session = Depends(get_db)):
    """
    Generates a standardized FHIR R4 Bundle for an uploaded medical document,
    including FHIR Patient, DiagnosticReport, Observation, and MedicationRequest resources.
    """
    doc = db.query(HealthDocument).filter(HealthDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    patient = doc.patient
    pat_dict = {
        "id": patient.id,
        "synthetic_abha_id": patient.synthetic_abha_id,
        "full_name": patient.full_name,
        "gender": patient.gender
    }

    doc_dict = {
        "id": doc.id,
        "document_type": doc.document_type,
        "document_date": doc.document_date
    }

    obs_dicts = [
        {
            "test_name": o.test_name,
            "standardized_code": o.standardized_code,
            "standardized_value": o.standardized_value,
            "original_value": o.original_value,
            "unit": o.unit,
            "reference_range_low": o.reference_range_low,
            "reference_range_high": o.reference_range_high,
            "reference_range_text": o.reference_range_text,
            "interpretation": o.interpretation
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

    bundle = FHIRConverterService.build_fhir_bundle(
        patient=pat_dict,
        document=doc_dict,
        observations=obs_dicts,
        medications=med_dicts
    )

    return bundle
