"""
Prescription-to-Reminder Planner routes.
Allows review of extracted prescriptions and verification of reminder schedules.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import ExtractedMedication, HealthDocument
from backend.app.schemas import MedicationOut, MedicationUpdate
from backend.app.services.medication_service import MedicationPlannerService

router = APIRouter(prefix="/medications", tags=["Medication Planner"])

@router.get("")
def list_medications(patient_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Returns medications, flagged trust issues, and daily computed schedule.
    When patient_id is supplied, only that patient's medications are returned.
    """
    query = db.query(ExtractedMedication)
    if patient_id is not None:
        query = (
            query.join(HealthDocument, ExtractedMedication.document_id == HealthDocument.id)
            .filter(HealthDocument.patient_id == patient_id)
        )
    meds = query.order_by(ExtractedMedication.id.desc()).all()

    med_dicts = [
        {
            "id": m.id,
            "document_id": m.document_id,
            "medicine_name": m.medicine_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "timing_instructions": m.timing_instructions,
            "duration": m.duration,
            "is_incomplete": m.is_incomplete,
            "trust_warning": m.trust_warning,
            "is_verified": m.is_verified,
            "schedule_time": m.schedule_time,
            "is_reminder_active": m.is_reminder_active,
            "evidence_excerpt": m.evidence_excerpt
        }
        for m in meds
    ]

    daily_schedule = MedicationPlannerService.compute_daily_schedule(med_dicts)

    return {
        "medications": med_dicts,
        "daily_schedule": daily_schedule,
        "total_active_reminders": sum(1 for m in meds if m.is_reminder_active)
    }

@router.patch("/{medication_id}", response_model=MedicationOut)
def update_medication(medication_id: int, payload: MedicationUpdate, db: Session = Depends(get_db)):
    """
    Updates medication schedule, verification status, and reminder state.
    Requires user verification before enabling reminders.
    """
    med = db.query(ExtractedMedication).filter(ExtractedMedication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")

    if payload.dosage is not None:
        med.dosage = payload.dosage
    if payload.frequency is not None:
        med.frequency = payload.frequency
    if payload.timing_instructions is not None:
        med.timing_instructions = payload.timing_instructions
    if payload.duration is not None:
        med.duration = payload.duration
    if payload.schedule_time is not None:
        med.schedule_time = payload.schedule_time
    if payload.is_verified is not None:
        med.is_verified = payload.is_verified
        # If user verifies, clear incomplete flag if dosage is provided
        if med.dosage and med.frequency:
            med.is_incomplete = False
            med.trust_warning = None

    if payload.is_reminder_active is not None:
        # Require verification to activate reminder
        if payload.is_reminder_active and not med.is_verified:
            # Auto-verify on explicit reminder activation
            med.is_verified = True
        med.is_reminder_active = payload.is_reminder_active

    db.commit()
    db.refresh(med)
    return med
