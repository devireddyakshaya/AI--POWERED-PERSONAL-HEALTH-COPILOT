export interface Observation {
  id: number;
  document_id: number;
  test_name: string;
  standardized_code?: string;
  original_value: string;
  user_corrected_value?: string;
  standardized_value?: number;
  unit?: string;
  reference_range_low?: number;
  reference_range_high?: number;
  reference_range_text?: string;
  interpretation: 'NORMAL' | 'HIGH' | 'LOW' | 'UNCERTAIN';
  is_verified: boolean;
  evidence_excerpt?: string;
  page_number: number;
  confidence_score: number;
  trust_notes?: string;
}

export interface Medication {
  id: number;
  document_id: number;
  medicine_name: string;
  dosage?: string;
  frequency?: string;
  timing_instructions?: string;
  duration?: string;
  is_incomplete: boolean;
  trust_warning?: string;
  is_verified: boolean;
  schedule_time: string;
  is_reminder_active: boolean;
  evidence_excerpt?: string;
}

export interface KeyFinding {
  title: string;
  finding: string;
  interpretation: 'NORMAL' | 'ABNORMAL_HIGH' | 'ABNORMAL_LOW' | 'ATTENTION';
  evidence_excerpt: string;
  reference_range?: string;
  needs_verification: boolean;
}

export interface HealthSummary {
  id: number;
  document_id: number;
  english_summary: string;
  telugu_summary: string;
  key_findings: KeyFinding[];
  questions_for_doctor: string[];
  uncertainty_notes?: string;
  is_demo_generated: boolean;
  created_at: string;
}

export interface DocumentSummary {
  id: number;
  patient_id: number;
  file_name: string;
  file_type: string;
  file_size: number;
  document_type: string;
  specialty?: string;
  document_date?: string;
  laboratory_name?: string;
  page_count: number;
  trust_score: number;
  trust_warnings: string[];
  is_synthetic: boolean;
  created_at: string;
  observation_count: number;
  medication_count: number;
}

export interface DocumentDetail extends DocumentSummary {
  raw_text?: string;
  observations: Observation[];
  medications: Medication[];
  summary?: HealthSummary;
}

export interface ComparisonItem {
  test_name: string;
  unit: string;
  report_a_value: number;
  report_b_value: number;
  report_a_original: string;
  report_b_original: string;
  absolute_change: number;
  percentage_change: number;
  trend_direction: 'INCREASED' | 'DECREASED' | 'STABLE';
  reference_range_text: string;
  range_shift_status: 'CLOSER_TO_NORMAL' | 'FARTHER_FROM_NORMAL' | 'WITHIN_NORMAL' | 'UNCHANGED' | 'UNSAFE_COMPARISON';
  clinical_note: string;
  is_safe_comparison: boolean;
  flag_reason?: string;
}

export interface ReportComparison {
  report_a_id: number;
  report_b_id: number;
  report_a_date: string;
  report_b_date: string;
  safe_comparison: boolean;
  warning_notes?: string;
  matched_tests: ComparisonItem[];
  unmatched_tests_a: string[];
  unmatched_tests_b: string[];
  disclaimer: string;
}

export interface DoctorQuestion {
  id: number;
  patient_id: number;
  source_document_id?: number;
  question_text: string;
  context_note?: string;
  category: string;
  is_checked: boolean;
  created_at: string;
}

export interface PatientProfile {
  id: number;
  synthetic_abha_id: string;
  full_name: string;
  age?: number;
  gender?: string;
  total_documents: number;
  created_at: string;
}

import type { LanguageCode } from '../i18n/translations';

export type LanguageMode = LanguageCode;

export type Gender = 'Female' | 'Male';

/** Preferred assistant voice. `system` uses whatever the device provides. */
export type VoiceType = 'female' | 'male' | 'system';

export interface LocalizedExplanation {
  language: string;
  summary: string;
  key_findings: KeyFinding[];
  questions_for_doctor: string[];
  uncertainty_notes?: string;
}

export interface VoiceAnswer {
  answer: string;
  query: string;
  language: string;
  document_id?: number | null;
  source: string;
}
