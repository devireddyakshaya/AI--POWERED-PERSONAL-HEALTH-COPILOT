"""
Doctor Visit Prep Assistant routes.
Provides interactive checklist of clinician questions generated from test findings.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models import DoctorQuestion, PatientProfile, HealthDocument
from backend.app.schemas import DoctorQuestionOut, DoctorQuestionCreate
from backend.app.services.doctor_prep_service import DoctorPrepService
from backend.app.data.demo_samples import get_or_create_patient

router = APIRouter(prefix="/doctor-prep", tags=["Doctor Visit Prep"])

class ToggleStatus(BaseModel):
    is_checked: bool

@router.get("", response_model=List[DoctorQuestionOut])
def get_doctor_questions(patient_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Returns clinician discussion questions for a patient. When patient_id is
    supplied, only that patient's questions are returned.
    """
    query = db.query(DoctorQuestion)
    if patient_id is not None:
        query = query.filter(DoctorQuestion.patient_id == patient_id)
    questions = query.order_by(DoctorQuestion.is_checked.asc(), DoctorQuestion.id.desc()).all()
    return questions

@router.post("", response_model=DoctorQuestionOut)
def create_custom_question(payload: DoctorQuestionCreate, db: Session = Depends(get_db)):
    """
    Allows patient to add their own custom questions to the checklist.
    """
    patient = None
    if payload.patient_id is not None:
        patient = db.query(PatientProfile).filter(PatientProfile.id == payload.patient_id).first()
    if patient is None:
        patient = db.query(PatientProfile).order_by(PatientProfile.id.asc()).first()
    if patient is None:
        patient = get_or_create_patient(db, "Unknown Patient")

    dq = DoctorQuestion(
        patient_id=patient.id,
        question_text=payload.question_text,
        category=payload.category or "Personal Question",
        context_note=payload.context_note or "Added by patient",
        is_checked=False
    )
    db.add(dq)
    db.commit()
    db.refresh(dq)
    return dq

@router.patch("/{question_id}/toggle", response_model=DoctorQuestionOut)
def toggle_question_check(question_id: int, payload: ToggleStatus, db: Session = Depends(get_db)):
    """
    Toggles whether a question has been asked / addressed.
    """
    dq = db.query(DoctorQuestion).filter(DoctorQuestion.id == question_id).first()
    if not dq:
        raise HTTPException(status_code=404, detail="Question not found")
    dq.is_checked = payload.is_checked
    db.commit()
    db.refresh(dq)
    return dq

@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """
    Removes a question from the checklist.
    """
    dq = db.query(DoctorQuestion).filter(DoctorQuestion.id == question_id).first()
    if not dq:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(dq)
    db.commit()
    return {"success": True, "message": "Question removed from checklist"}
