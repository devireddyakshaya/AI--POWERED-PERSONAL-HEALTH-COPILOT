"""
Pydantic schemas and FHIR-aligned data transfer objects for MediMitra AI.
"""
from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

# --- Observation Schemas ---

class ObservationBase(BaseModel):
    test_name: str
    standardized_code: Optional[str] = None
    original_value: str
    standardized_value: Optional[float] = None
    unit: Optional[str] = None
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    reference_range_text: Optional[str] = None
    interpretation: str = "UNCERTAIN"  # NORMAL, HIGH, LOW, UNCERTAIN
    is_verified: bool = False
    evidence_excerpt: Optional[str] = None
    page_number: int = 1
    confidence_score: float = 0.90
    trust_notes: Optional[str] = None

class ObservationCorrection(BaseModel):
    user_corrected_value: str
    is_verified: bool = True

class ObservationOut(ObservationBase):
    id: int
    document_id: int
    user_corrected_value: Optional[str] = None

    class Config:
        from_attributes = True

# --- Medication Schemas ---

class MedicationBase(BaseModel):
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    timing_instructions: Optional[str] = None
    duration: Optional[str] = None
    is_incomplete: bool = False
    trust_warning: Optional[str] = None
    is_verified: bool = False
    schedule_time: str = "08:00 AM"
    is_reminder_active: bool = False
    evidence_excerpt: Optional[str] = None

class MedicationUpdate(BaseModel):
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    timing_instructions: Optional[str] = None
    duration: Optional[str] = None
    schedule_time: Optional[str] = None
    is_reminder_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class MedicationOut(MedicationBase):
    id: int
    document_id: int

    class Config:
        from_attributes = True

# --- Health Summary Schemas ---

class KeyFinding(BaseModel):
    title: str
    finding: str
    interpretation: str  # NORMAL, ABNORMAL_HIGH, ABNORMAL_LOW, ATTENTION
    evidence_excerpt: str
    reference_range: Optional[str] = None
    needs_verification: bool = False

class HealthSummaryOut(BaseModel):
    id: int
    document_id: int
    english_summary: str
    telugu_summary: str
    key_findings: List[KeyFinding] = []
    questions_for_doctor: List[str] = []
    uncertainty_notes: Optional[str] = None
    is_demo_generated: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

# --- Document Schemas ---

class DocumentSummaryOut(BaseModel):
    id: int
    patient_id: int
    file_name: str
    file_type: str
    file_size: int
    document_type: str
    specialty: Optional[str] = None
    document_date: Optional[str] = None
    laboratory_name: Optional[str] = None
    page_count: int
    trust_score: int
    trust_warnings: List[str] = []
    is_synthetic: bool
    created_at: datetime
    observation_count: int = 0
    medication_count: int = 0

    class Config:
        from_attributes = True

class DocumentDetailOut(BaseModel):
    id: int
    patient_id: int
    file_name: str
    file_type: str
    file_size: int
    document_type: str
    specialty: Optional[str] = None
    document_date: Optional[str] = None
    laboratory_name: Optional[str] = None
    raw_text: Optional[str] = None
    page_count: int
    trust_score: int
    trust_warnings: List[str] = []
    is_synthetic: bool
    created_at: datetime
    observations: List[ObservationOut] = []
    medications: List[MedicationOut] = []
    summary: Optional[HealthSummaryOut] = None

    class Config:
        from_attributes = True

# --- Comparison Schemas ---

class ComparisonItem(BaseModel):
    test_name: str
    unit: str
    report_a_value: float
    report_b_value: float
    report_a_original: str
    report_b_original: str
    absolute_change: float
    percentage_change: float
    trend_direction: str  # "INCREASED", "DECREASED", "STABLE"
    reference_range_text: str
    range_shift_status: str  # "CLOSER_TO_NORMAL", "FARTHER_FROM_NORMAL", "WITHIN_NORMAL", "UNCHANGED"
    clinical_note: str  # Clear patient explanation without claiming recovery
    is_safe_comparison: bool = True
    flag_reason: Optional[str] = None

class ReportComparisonResponse(BaseModel):
    report_a_id: int
    report_b_id: int
    report_a_date: str
    report_b_date: str
    safe_comparison: bool
    warning_notes: Optional[str] = None
    matched_tests: List[ComparisonItem] = []
    unmatched_tests_a: List[str] = []
    unmatched_tests_b: List[str] = []
    disclaimer: str

# --- Doctor Prep Schemas ---

class DoctorQuestionCreate(BaseModel):
    question_text: str
    category: Optional[str] = "Personal Question"
    context_note: Optional[str] = None
    patient_id: Optional[int] = None

class DoctorQuestionOut(BaseModel):
    id: int
    patient_id: int
    source_document_id: Optional[int] = None
    question_text: str
    context_note: Optional[str] = None
    category: str
    is_checked: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Patient Profile ---

class PatientProfileOut(BaseModel):
    id: int
    synthetic_abha_id: str
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    total_documents: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# --- ABDM/FHIR R4 Inspired Resource Models ---

class FHIRIdentifier(BaseModel):
    system: str
    value: str

class FHIRCoding(BaseModel):
    system: str
    code: str
    display: str

class FHIRCodeableConcept(BaseModel):
    coding: List[FHIRCoding]
    text: str

class FHIRQuantity(BaseModel):
    value: float
    unit: str
    system: str = "http://unitsofmeasure.org"

class FHIRPatientResource(BaseModel):
    resourceType: str = "Patient"
    id: str
    identifier: List[FHIRIdentifier]
    name: List[Dict[str, Any]]
    gender: str
    birthDate: Optional[str] = None

class FHIRObservationResource(BaseModel):
    resourceType: str = "Observation"
    id: str
    status: str = "final"
    code: FHIRCodeableConcept
    subject: Dict[str, str]
    effectiveDateTime: Optional[str] = None
    valueQuantity: Optional[FHIRQuantity] = None
    interpretation: Optional[List[FHIRCodeableConcept]] = None
    referenceRange: Optional[List[Dict[str, Any]]] = None

class FHIRMedicationRequestResource(BaseModel):
    resourceType: str = "MedicationRequest"
    id: str
    status: str = "active"
    intent: str = "order"
    medicationCodeableConcept: FHIRCodeableConcept
    subject: Dict[str, str]
    dosageInstruction: Optional[List[Dict[str, Any]]] = None

class FHIRDiagnosticReportResource(BaseModel):
    resourceType: str = "DiagnosticReport"
    id: str
    status: str = "final"
    code: FHIRCodeableConcept
    subject: Dict[str, str]
    effectiveDateTime: Optional[str] = None
    result: List[Dict[str, str]]
    conclusion: Optional[str] = None
