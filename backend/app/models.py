"""
SQLAlchemy ORM models for MediMitra AI.
Designed with FHIR-inspired structure and provenance tracking.
"""
from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

class PatientProfile(Base):
    """
    Patient identity entity.
    Synthetic ABHA identifier is provided purely for demonstration of ABDM readiness.
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    synthetic_abha_id = Column(String(50), unique=True, index=True, nullable=True)
    # Identifier printed on the report itself (e.g. "Patient ID: AK-78291",
    # UHID, MRN). When present it is the strongest signal for associating
    # subsequent reports with the same person without merging similar names.
    external_patient_id = Column(String(80), index=True, nullable=True)
    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    documents = relationship("HealthDocument", back_populates="patient", cascade="all, delete-orphan")
    doctor_questions = relationship("DoctorQuestion", back_populates="patient", cascade="all, delete-orphan")


class HealthDocument(Base):
    """
    Metadata and extracted content for an uploaded medical document.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, image/jpeg, image/png
    file_size = Column(Integer, nullable=False)  # in bytes
    document_type = Column(String(50), default="Laboratory Report")  # Laboratory Report, Prescription, Diagnostic Report, Discharge Summary
    specialty = Column(String(50), default="General Medicine")  # e.g. Cardiology, Neurology, Gynecology & Obstetrics
    document_date = Column(String(50), nullable=True)  # YYYY-MM-DD or raw parsed date
    laboratory_name = Column(String(200), nullable=True)
    raw_text = Column(Text, nullable=True)
    page_count = Column(Integer, default=1)
    
    # Smart Report Trust Check fields
    trust_score = Column(Integer, default=85)  # 0 to 100
    trust_warnings = Column(Text, default="[]")  # JSON list of warnings
    is_synthetic = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("PatientProfile", back_populates="documents")
    observations = relationship("ExtractedObservation", back_populates="document", cascade="all, delete-orphan")
    medications = relationship("ExtractedMedication", back_populates="document", cascade="all, delete-orphan")
    summary = relationship("HealthSummary", back_populates="document", uselist=False, cascade="all, delete-orphan")

    def get_warnings_list(self):
        try:
            return json.loads(self.trust_warnings) if self.trust_warnings else []
        except Exception:
            return []

    def set_warnings_list(self, warnings: list):
        self.trust_warnings = json.dumps(warnings)


class ExtractedObservation(Base):
    """
    Extracted laboratory or diagnostic test finding (FHIR Observation inspired).
    Preserves original extracted value, supports user correction, evidence linking.
    """
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String(150), nullable=False, index=True)
    standardized_code = Column(String(50), nullable=True)  # Mock LOINC e.g. "1558-6" for Fasting Glucose
    
    original_value = Column(String(50), nullable=False)
    standardized_value = Column(Float, nullable=True)
    user_corrected_value = Column(String(50), nullable=True)  # Separately recorded user correction
    unit = Column(String(50), nullable=True)  # e.g. mg/dL, %, g/dL
    
    reference_range_low = Column(Float, nullable=True)
    reference_range_high = Column(Float, nullable=True)
    reference_range_text = Column(String(100), nullable=True)  # e.g. "70 - 99 mg/dL"
    
    interpretation = Column(String(30), default="UNCERTAIN")  # NORMAL, HIGH, LOW, UNCERTAIN
    is_verified = Column(Boolean, default=False)
    
    # Evidence-linking & Trust Check
    evidence_excerpt = Column(Text, nullable=True)  # Original text snippet from document
    page_number = Column(Integer, default=1)
    confidence_score = Column(Float, default=0.92)  # OCR confidence 0.0 to 1.0
    trust_notes = Column(String(255), nullable=True)

    document = relationship("HealthDocument", back_populates="observations")


class ExtractedMedication(Base):
    """
    Extracted prescription medicine (FHIR MedicationRequest inspired).
    """
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    medicine_name = Column(String(150), nullable=False)
    dosage = Column(String(100), nullable=True)  # e.g. "500 mg"
    frequency = Column(String(100), nullable=True)  # e.g. "Once Daily"
    timing_instructions = Column(String(200), nullable=True)  # e.g. "After dinner"
    duration = Column(String(100), nullable=True)  # e.g. "30 days"
    
    is_incomplete = Column(Boolean, default=False)  # Flag for missing instructions
    trust_warning = Column(String(255), nullable=True)  # e.g. "Missing dosage duration"
    is_verified = Column(Boolean, default=False)  # User confirmed
    
    # Prescription-to-Reminder Planner
    schedule_time = Column(String(20), default="08:00 AM")  # Reminder trigger time
    is_reminder_active = Column(Boolean, default=False)
    evidence_excerpt = Column(Text, nullable=True)

    document = relationship("HealthDocument", back_populates="medications")


class HealthSummary(Base):
    """
    AI-generated patient-friendly summary in Plain English and Telugu.
    """
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    english_summary = Column(Text, nullable=False)
    telugu_summary = Column(Text, nullable=False)
    
    key_findings = Column(Text, default="[]")  # JSON list of structured findings
    questions_for_doctor = Column(Text, default="[]")  # JSON list of clinician questions
    uncertainty_notes = Column(Text, nullable=True)
    is_demo_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("HealthDocument", back_populates="summary")

    def get_findings(self):
        try:
            return json.loads(self.key_findings) if self.key_findings else []
        except Exception:
            return []

    def get_questions(self):
        try:
            return json.loads(self.questions_for_doctor) if self.questions_for_doctor else []
        except Exception:
            return []


class ReportComparison(Base):
    """
    Health Change Detector comparison result between two reports.
    """
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    report_a_id = Column(Integer, nullable=False)
    report_b_id = Column(Integer, nullable=False)
    report_a_date = Column(String(50), nullable=True)
    report_b_date = Column(String(50), nullable=True)
    
    comparison_data = Column(Text, default="[]")  # JSON array of test comparison objects
    safe_comparison = Column(Boolean, default=True)
    warning_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def get_comparison_data(self):
        try:
            return json.loads(self.comparison_data) if self.comparison_data else []
        except Exception:
            return []


class DoctorQuestion(Base):
    """
    Questions prepared for discussion with a doctor.
    """
    __tablename__ = "doctor_questions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    source_document_id = Column(Integer, nullable=True)
    question_text = Column(Text, nullable=False)
    context_note = Column(String(255), nullable=True)
    category = Column(String(50), default="Lab Follow-up")  # Abnormal result, Medication clarify, General
    is_checked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientProfile", back_populates="doctor_questions")
