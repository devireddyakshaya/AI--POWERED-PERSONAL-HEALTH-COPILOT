import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { MedicalDisclaimerModal } from './components/MedicalDisclaimerModal';
import { OnboardingFlow } from './components/OnboardingFlow';
import { VoiceAssistant } from './components/VoiceAssistant';
import { LanguageCode } from './i18n/translations';
import type { VoiceType } from './types';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';
import { ExplainerPage } from './pages/ExplainerPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { TimelinePage } from './pages/TimelinePage';
import { DoctorPrepPage } from './pages/DoctorPrepPage';
import { MedicationPlannerPage } from './pages/MedicationPlannerPage';
import { PrivacyVaultPage } from './pages/PrivacyVaultPage';
import {
  DocumentSummary,
  DocumentDetail,
  LanguageMode,
  Gender,
  PatientProfile
} from './types';
import {
  fetchPatients,
  fetchDocuments,
  fetchDocumentDetail,
  fetchSystemStatus,
  updatePatientProfile
} from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [language, setLanguage] = useState<LanguageMode>(
    (typeof localStorage !== 'undefined' && (localStorage.getItem('mm_language') as LanguageCode)) || 'en'
  );
  const [gender, setGender] = useState<Gender | null>(
    (typeof localStorage !== 'undefined' && (localStorage.getItem('mm_gender') as Gender)) || null
  );
  const [setupComplete, setSetupComplete] = useState<boolean>(
    typeof localStorage !== 'undefined' &&
      !!localStorage.getItem('mm_language') &&
      !!localStorage.getItem('mm_gender')
  );
  const [patients, setPatients] = useState<PatientProfile[]>([]);
  const [activePatientId, setActivePatientId] = useState<number | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [activeDocDetail, setActiveDocDetail] = useState<DocumentDetail | null>(null);
  const [allDocDetails, setAllDocDetails] = useState<DocumentDetail[]>([]);
  const [isDisclaimerOpen, setIsDisclaimerOpen] = useState<boolean>(false);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const activePatient = patients.find((p) => p.id === activePatientId) || null;

  /**
   * Loads patients and the records for one patient. Passing a patientId scopes
   * everything to that person; otherwise the first patient is used. Stale data
   * is always cleared first so a previous patient's report can never leak in.
   */
  const loadData = useCallback(async (preferredPatientId?: number | null) => {
    setIsLoading(true);
    // Clear everything so we never show a previous patient's data.
    setDocuments([]);
    setAllDocDetails([]);
    setActiveDocDetail(null);

    try {
      const status = await fetchSystemStatus();
      if (status && typeof status.is_demo_mode === 'boolean') {
        setIsDemoMode(status.is_demo_mode);
      }
    } catch {
      /* offline */
    }

    let patientList: PatientProfile[] = [];
    try {
      patientList = await fetchPatients();
    } catch (err) {
      console.error('Could not load patients:', err);
    }
    setPatients(patientList);

    const resolvedId =
      (preferredPatientId != null && patientList.some((p) => p.id === preferredPatientId)
        ? preferredPatientId
        : patientList[0]?.id) ?? null;

    setActivePatientId(resolvedId);

    if (resolvedId == null) {
      setIsLoading(false);
      return;
    }

    try {
      const docs = await fetchDocuments(resolvedId);
      setDocuments(docs);
      if (docs.length > 0) {
        const details = await Promise.all(docs.map((d) => fetchDocumentDetail(d.id)));
        setAllDocDetails(details);
        setActiveDocDetail(details[0] ?? null);
      }
    } catch (err) {
      console.error('Could not load documents:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (setupComplete) loadData();
  }, [setupComplete, loadData]);

  const handleOnboardingComplete = async (lang: LanguageCode, voiceType: VoiceType) => {
    const genderMap: Record<VoiceType, Gender> = { female: 'Female', male: 'Male', system: 'Female' };
    setLanguage(lang);
    setGender(genderMap[voiceType]);
    try {
      localStorage.setItem('mm_language', lang);
      localStorage.setItem('mm_gender', genderMap[voiceType]);
    } catch {
      /* storage unavailable */
    }
    setSetupComplete(true);
    setActiveTab('upload');
    // Persist to the patient profile when one already exists.
    try {
      if (activePatientId != null) {
        await updatePatientProfile({ gender: genderMap[voiceType] }, activePatientId);
      }
    } catch {
      /* no patient yet - keep the preference locally */
    }
  };

  const handleSelectPatient = async (patientId: number) => {
    if (patientId === activePatientId) return;
    await loadData(patientId);
    setActiveTab('dashboard');
  };

  const handleSelectDocument = async (docId: number) => {
    try {
      const doc = await fetchDocumentDetail(docId);
      setActiveDocDetail(doc);
      setActiveTab('explainer');
    } catch (err) {
      console.error(err);
    }
  };

  const handleDocumentProcessed = async (doc: DocumentDetail) => {
    // Reflect the freshly processed report immediately, then re-sync from the
    // backend so counts, specialty and patient assignment are authoritative.
    setActiveDocDetail(doc);
    setAllDocDetails((prev) => [doc, ...prev.filter((d) => d.id !== doc.id)]);
    setDocuments((prev) => {
      const summary: DocumentSummary = {
        id: doc.id,
        patient_id: doc.patient_id,
        file_name: doc.file_name,
        file_type: doc.file_type,
        file_size: doc.file_size,
        document_type: doc.document_type,
        specialty: doc.specialty,
        document_date: doc.document_date,
        laboratory_name: doc.laboratory_name,
        page_count: doc.page_count,
        trust_score: doc.trust_score,
        trust_warnings: doc.trust_warnings,
        is_synthetic: doc.is_synthetic,
        created_at: doc.created_at,
        observation_count: doc.observations.length,
        medication_count: doc.medications.length
      };
      return [summary, ...prev.filter((d) => d.id !== doc.id)];
    });
    await loadData(doc.patient_id);
  };

  const handleDataChanged = async () => {
    await loadData(activePatientId);
  };

  if (!setupComplete) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#f8fafc]">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
        openDisclaimer={() => setIsDisclaimerOpen(true)}
        isDemoMode={isDemoMode}
        patients={patients}
        activePatientId={activePatientId}
        onSelectPatient={handleSelectPatient}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'landing' && (
          <LandingPage onStart={(tab) => setActiveTab(tab)} language={language} />
        )}

        {activeTab === 'dashboard' && (
          <DashboardPage
            documents={documents}
            allDocuments={allDocDetails}
            activePatient={activePatient}
            isLoading={isLoading}
            onNavigate={(tab, docId) => {
              if (docId) handleSelectDocument(docId);
              else setActiveTab(tab);
            }}
            language={language}
          />
        )}

        {activeTab === 'upload' && (
          <UploadPage
            onDocumentProcessed={handleDocumentProcessed}
            onNavigate={(tab, docId) => {
              if (docId) handleSelectDocument(docId);
              else setActiveTab(tab);
            }}
            language={language}
            patientId={activePatientId}
          />
        )}

        {activeTab === 'explainer' && (
          <ExplainerPage
            document={activeDocDetail}
            allDocuments={allDocDetails}
            onSelectDocument={async (id) => {
              const doc = await fetchDocumentDetail(id);
              setActiveDocDetail(doc);
            }}
            language={language}
            setLanguage={setLanguage}
          />
        )}

        {activeTab === 'comparison' && (
          <ComparisonPage documents={allDocDetails} language={language} />
        )}

        {activeTab === 'timeline' && (
          <TimelinePage
            documents={documents}
            onSelectDocument={handleSelectDocument}
            onRefresh={handleDataChanged}
            language={language}
          />
        )}

        {activeTab === 'doctor-prep' && (
          <DoctorPrepPage language={language} patientId={activePatientId} />
        )}

        {activeTab === 'medications' && (
          <MedicationPlannerPage language={language} patientId={activePatientId} />
        )}

        {activeTab === 'privacy-vault' && (
          <PrivacyVaultPage
            language={language}
            activeDocumentId={activeDocDetail?.id ?? null}
            onDataPurged={handleDataChanged}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-800">MediMitra AI</span>
            <span>—</span>
            <span>Your Health Records. Clearly Understood.</span>
          </div>

          <div className="flex items-center space-x-4 text-slate-500">
            <span>HacXLerate 2026 | Team TEKSQUADS</span>
            <span>•</span>
            <button
              onClick={() => setIsDisclaimerOpen(true)}
              className="hover:text-blue-700 underline underline-offset-2"
            >
              Medical Disclaimer & Privacy
            </button>
          </div>
        </div>
      </footer>

      {/* Safety & Privacy Disclaimer Modal */}
      <MedicalDisclaimerModal
        isOpen={isDisclaimerOpen}
        onClose={() => setIsDisclaimerOpen(false)}
        language={language}
      />

      {/* Global Voice Assistant (accessibility for blind / low-literacy / motor-impaired users) */}
      <VoiceAssistant
        language={language}
        onNavigate={(tab) => setActiveTab(tab)}
        activeDocument={activeDocDetail}
        onOpenSetup={() => setSetupComplete(false)}
      />
    </div>
  );
};

export default App;
