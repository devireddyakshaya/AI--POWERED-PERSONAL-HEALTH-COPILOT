"""
Patient profile management routes.
Lists the patients known to this local instance so the app can scope every
report, observation, medication and question to the correct person.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import PatientProfile
from backend.app.schemas import PatientProfileOut

router = APIRouter(prefix="/patients", tags=["Patients"])


def _to_out(patient: PatientProfile) -> PatientProfileOut:
    return PatientProfileOut(
        id=patient.id,
        synthetic_abha_id=patient.synthetic_abha_id or "Local Record",
        full_name=patient.full_name,
        age=patient.age,
        gender=patient.gender,
        total_documents=len(patient.documents),
        created_at=patient.created_at
    )


@router.get("", response_model=List[PatientProfileOut])
def list_patients(db: Session = Depends(get_db)):
    """Returns every patient profile stored in the local database."""
    patients = db.query(PatientProfile).order_by(PatientProfile.created_at.asc(), PatientProfile.id.asc()).all()
    return [_to_out(p) for p in patients]


@router.get("/{patient_id}", response_model=PatientProfileOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return _to_out(patient)


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Permanently deletes a patient and all their associated records."""
    patient = db.query(PatientProfile).filter(PatientProfile.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"success": True, "message": f"Patient {patient_id} and all related records were deleted."}
