import {
  DocumentSummary,
  DocumentDetail,
  ReportComparison,
  DoctorQuestion,
  Medication,
  PatientProfile,
  Observation,
  LocalizedExplanation,
  VoiceAnswer
} from '../types';

const API_BASE = 'https://your-render-backend-url.onrender.com/api';

/**
 * MediMitra AI API client.
 *
 * IMPORTANT: this module never invents clinical data. If the backend is
 * unreachable or returns an error, functions either throw (mutations / detail
 * fetches) or return an empty result so the UI can show an honest empty state.
 */

async function extractError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (body && typeof body.detail === 'string') return body.detail;
    if (body && typeof body.error === 'string') return body.error;
  } catch {
    /* not JSON */
  }
  return `Request failed (${res.status})`;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(await extractError(res));
  return (await res.json()) as T;
}

// ---------------------------------------------------------------------------
// System status
// ---------------------------------------------------------------------------

export interface SystemStatus {
  mode: string;
  is_demo_mode: boolean;
  offline?: boolean;
  privacy?: Record<string, unknown>;
  capabilities?: Record<string, unknown>;
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  try {
    const res = await fetch(`${API_BASE}/status`);
    if (res.ok) return await res.json();
  } catch {
    /* offline */
  }
  return {
    mode: 'OFFLINE',
    is_demo_mode: false,
    offline: true
  };
}

// ---------------------------------------------------------------------------
// Patients
// ---------------------------------------------------------------------------

export async function fetchPatients(): Promise<PatientProfile[]> {
  return getJson<PatientProfile[]>('/patients');
}

export async function fetchPatient(id: number): Promise<PatientProfile> {
  return getJson<PatientProfile>(`/patients/${id}`);
}

export async function deletePatient(id: number): Promise<boolean> {
  const res = await fetch(`${API_BASE}/patients/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await extractError(res));
  return true;
}

export async function updatePatientProfile(
  payload: { full_name?: string; age?: number; gender?: string },
  patientId?: number | null
): Promise<PatientProfile> {
  const query = patientId != null ? `?patient_id=${patientId}` : '';
  const res = await fetch(`${API_BASE}/fhir/patient${query}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await extractError(res));
  return await res.json();
}

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------

export async function fetchDocuments(patientId?: number | null): Promise<DocumentSummary[]> {
  const query = patientId != null ? `?patient_id=${patientId}` : '';
  return getJson<DocumentSummary[]>(`/documents${query}`);
}

export async function fetchDocumentDetail(id: number): Promise<DocumentDetail> {
  return getJson<DocumentDetail>(`/documents/${id}`);
}

export async function uploadMedicalDocument(
  file: File,
  docType?: string,
  patientId?: number | null
): Promise<DocumentDetail> {
  const formData = new FormData();
  formData.append('file', file);
  if (docType) formData.append('document_type_override', docType);
  if (patientId != null) formData.append('patient_id', String(patientId));

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error(await extractError(res));
  return await res.json();
}

export async function correctObservation(
  docId: number,
  obsId: number,
  userCorrectedValue: string
): Promise<Observation> {
  const res = await fetch(`${API_BASE}/documents/${docId}/observations/${obsId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_corrected_value: userCorrectedValue, is_verified: true })
  });
  if (!res.ok) throw new Error(await extractError(res));
  return await res.json();
}

export async function deleteDocumentRecord(id: number): Promise<boolean> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await extractError(res));
  return true;
}

/** Permanently deletes ALL records. Does NOT restore synthetic demo data. */
export async function clearAllRecords(): Promise<boolean> {
  const res = await fetch(`${API_BASE}/documents/clear-all`, { method: 'POST' });
  if (!res.ok) throw new Error(await extractError(res));
  return true;
}

/** Debug/demo helper: resets the database to synthetic demo records. */
export async function resetDemoRecords(): Promise<boolean> {
  const res = await fetch(`${API_BASE}/documents/reset-demo`, { method: 'POST' });
  if (!res.ok) throw new Error(await extractError(res));
  return true;
}

// ---------------------------------------------------------------------------
// AI explanation (localized)
// ---------------------------------------------------------------------------

export async function fetchLocalizedExplanation(
  docId: number,
  language: string
): Promise<LocalizedExplanation | null> {
  try {
    const res = await fetch(`${API_BASE}/analysis/explain/${docId}?language=${language}`);
    if (res.ok) return await res.json();
  } catch {
    /* offline */
  }
  return null;
}

/** Sends a free-text question grounded in a report and returns a spoken answer. */
export async function askVoiceAssistant(
  query: string,
  language: string,
  docId?: number | null
): Promise<VoiceAnswer> {
  const res = await fetch(`${API_BASE}/voice/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: query.trim(), language, document_id: docId ?? null })
  });
  if (!res.ok) throw new Error(await extractError(res));
  return await res.json();
}

// ---------------------------------------------------------------------------
// Comparison (Health Change Detector)
// ---------------------------------------------------------------------------

export async function fetchReportComparison(
  reportAId: number,
  reportBId: number
): Promise<ReportComparison | null> {
  try {
    const res = await fetch(`${API_BASE}/comparison`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ report_a_id: reportAId, report_b_id: reportBId })
    });
    if (res.ok) return await res.json();
  } catch {
    /* offline */
  }
  return null;
}

// ---------------------------------------------------------------------------
// Doctor prep questions
// ---------------------------------------------------------------------------

export async function fetchDoctorQuestions(patientId?: number | null): Promise<DoctorQuestion[]> {
  const query = patientId != null ? `?patient_id=${patientId}` : '';
  return getJson<DoctorQuestion[]>(`/doctor-prep${query}`);
}

export async function addDoctorQuestion(
  questionText: string,
  category: string = 'Personal Question',
  patientId?: number | null
): Promise<DoctorQuestion> {
  const res = await fetch(`${API_BASE}/doctor-prep`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question_text: questionText, category, patient_id: patientId ?? null })
  });
  if (!res.ok) throw new Error(await extractError(res));
  return await res.json();
}

export async function toggleDoctorQuestionCheck(id: number, isChecked: boolean): Promise<boolean> {
  const res = await fetch(`${API_BASE}/doctor-prep/${id}/toggle`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_checked: isChecked })
  });
  if (!res.ok) throw new Error(await extractError(res));
  return true;
}

export async function deleteDoctorQuestion(id: number): Promise<boolean> {
  const res = await fetch(`${API_BASE}/doctor-prep/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(await extractError(res));
  return true;
}

// ---------------------------------------------------------------------------
// Medication planner
// ---------------------------------------------------------------------------

export interface MedicationAgenda {
  medications: Medication[];
  daily_schedule: any[];
  total_active_reminders?: number;
}

export async function fetchMedicationAgenda(patientId?: number | null): Promise<MedicationAgenda> {
  const query = patientId != null ? `?patient_id=${patientId}` : '';
  return getJson<MedicationAgenda>(`/medications${query}`);
}

export async function updateMedicationSchedule(
  id: number,
  payload: Partial<Medication>
): Promise<boolean> {
  const res = await fetch(`${API_BASE}/medications/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await extractError(res));
  return true;
}

// ---------------------------------------------------------------------------
// FHIR / ABDM bundle
// ---------------------------------------------------------------------------

export async function fetchFhirBundle(docId: number): Promise<any> {
  return getJson<any>(`/fhir/bundle/${docId}`);
}
