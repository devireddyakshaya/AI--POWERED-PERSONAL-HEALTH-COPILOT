import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Edit2,
  Check,
  ArrowRight,
  Sparkles,
  FileUp,
  RefreshCw
} from 'lucide-react';
import { DocumentDetail, LanguageMode } from '../types';
import { t } from '../i18n/translations';
import { uploadMedicalDocument, correctObservation } from '../services/api';

interface UploadProps {
  onDocumentProcessed: (doc: DocumentDetail) => void;
  onNavigate: (tab: string, docId?: number) => void;
  language: LanguageMode;
  patientId?: number | null;
}

export const UploadPage: React.FC<UploadProps> = ({ onDocumentProcessed, onNavigate, language, patientId = null }) => {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('Laboratory Report');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedDoc, setProcessedDoc] = useState<DocumentDetail | null>(null);
  const [editingObsId, setEditingObsId] = useState<number | null>(null);
  const [correctedVal, setCorrectedVal] = useState('');
  const [statusMsg, setStatusMsg] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsProcessing(true);
    setStatusMsg(language === 'te' ? 'మీ నివేదికను చదువుతున్నాను...' : 'Reading your report...');
    try {
      const doc = await uploadMedicalDocument(file, docType, patientId);
      setProcessedDoc(doc);
      onDocumentProcessed(doc);
      setStatusMsg(language === 'te' ? 'నివేదిక సిద్ధంగా ఉంది!' : 'Report ready!');
    } catch (err) {
      const detail = err instanceof Error && err.message ? ` (${err.message})` : '';
      setStatusMsg(
        language === 'te'
          ? `ఏదో తప్పు జరిగింది. మళ్లీ ప్రయత్నించండి.${detail}`
          : `Something went wrong. Please try again.${detail}`
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLoadSampleReport = async (sampleType: 'glucose' | 'cbc') => {
    setIsProcessing(true);
    setStatusMsg(language === 'te' ? 'నమూనా నివేదిక లోడ్ అవుతోంది...' : 'Loading sample report...');
    
    const sampleContent = sampleType === 'glucose'
      ? `AAROGYAM PATHOLOGY & CLINICAL LAB
Patient: Ramesh Kumar (Age 48 M)
Date: 2026-02-14
Fasting Blood Glucose: 126.0 mg/dL (Reference: 70.0 - 99.0 mg/dL)
HbA1c: 6.9 % (Reference: 4.0 - 5.6 %)
Serum Creatinine: 1.0 mg/dL (Reference: 0.7 - 1.3 mg/dL)
Rx: Tab Metformin 500mg Once Daily after dinner`
      : `METROPOLIS HEALTHCARE LABS
Patient: Ramesh Kumar (Age 48 M)
Date: 2026-02-10
Hemoglobin: 13.8 g/dL (Reference: 13.0 - 17.0 g/dL)
Total Leukocyte Count: 6800 /cumm (Reference: 4000 - 11000 /cumm)
Platelet Count: 2.1 lakh/cumm (Reference: 1.5 - 4.5 lakh/cumm)`;

    const blob = new Blob([sampleContent], { type: 'text/plain' });
    const sampleFile = new File([blob], sampleType === 'glucose' ? 'Sample_Glycemic_Panel.txt' : 'Sample_CBC_Report.txt', {
      type: 'text/plain'
    });

    try {
      const doc = await uploadMedicalDocument(sampleFile, 'Laboratory Report', patientId);
      setProcessedDoc(doc);
      onDocumentProcessed(doc);
      setStatusMsg(language === 'te' ? 'నమూనా సిద్ధంగా ఉంది!' : 'Sample ready!');
    } catch (err) {
      const detail = err instanceof Error && err.message ? ` (${err.message})` : '';
      setStatusMsg(
        language === 'te'
          ? `నమూనాను లోడ్ చేయలేకపోయాం.${detail}`
          : `Could not load the sample.${detail}`
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveCorrection = async (obsId: number) => {
    if (!processedDoc || !correctedVal.trim()) return;
    try {
      const updatedObs = await correctObservation(processedDoc.id, obsId, correctedVal.trim());
      // Update local state
      const updatedList = processedDoc.observations.map(o => (o.id === obsId ? { ...o, ...updatedObs } : o));
      setProcessedDoc({ ...processedDoc, observations: updatedList });
      setEditingObsId(null);
      setCorrectedVal('');
    } catch (err) {
      alert('Failed to save correction.');
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
          {t(language, 'upload_title')}
        </h1>
        <p className="text-xs text-slate-500 mt-1">{t(language, 'upload_sub')}</p>
      </div>

      {/* Upload Zone & Sample Buttons */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl border-2 border-dashed border-slate-300 p-8 flex flex-col items-center justify-center text-center hover:border-blue-400 transition-colors">
          <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center mb-4">
            <UploadCloud className="w-8 h-8 stroke-[1.8]" />
          </div>

          <h3 className="text-sm font-bold text-slate-800">
            {file ? file.name : (language === 'te' ? 'అప్‌లోడ్ చేయడానికి నివేదికను ఎంచుకోండి' : 'Choose a report to upload')}
          </h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm">
            {language === 'te' ? 'PDF, JPG లేదా PNG, 15MB వరకు.' : 'PDF, JPG, or PNG. Up to 15MB.'}
          </p>

          <input
            type="file"
            id="fileInput"
            accept=".pdf,.jpg,.jpeg,.png,.txt"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="mt-5 flex flex-wrap gap-3 items-center">
            <label
              htmlFor="fileInput"
              className="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold cursor-pointer transition-colors"
            >
              Browse Local Files
            </label>

            {file && (
              <button
                onClick={handleUpload}
                disabled={isProcessing}
                className="flex items-center space-x-1.5 px-5 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold transition-colors disabled:opacity-50 shadow-sm"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Extracting...</span>
                  </>
                ) : (
                  <>
                    <FileUp className="w-3.5 h-3.5" />
                    <span>Process & Extract</span>
                  </>
                )}
              </button>
            )}
          </div>

          {statusMsg && (
            <p className="text-xs font-semibold text-blue-700 mt-3 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{statusMsg}</span>
            </p>
          )}
        </div>

        {/* 1-Click Instant Demo Reports */}
        <div className="p-6 bg-slate-900 text-white rounded-2xl flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center space-x-2 text-blue-400 text-xs font-bold mb-2">
              <Sparkles className="w-4 h-4" />
              <span>{language === 'te' ? 'త్వరిత డెమో' : 'QUICK DEMO'}</span>
            </div>
            <h3 className="text-base font-bold text-white">{language === 'te' ? 'నివేదిక లేదా?' : "Don't have a report?"}</h3>
            <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
              {language === 'te' ? 'ఇది ఎలా పనిచేస్తుందో చూడటానికి నమూనా నివేదిక ప్రయత్నించండి.' : 'Try a sample report to see how it works.'}
            </p>
          </div>

          <div className="space-y-2.5 mt-6">
            <button
              onClick={() => handleLoadSampleReport('glucose')}
              disabled={isProcessing}
              className="w-full text-left p-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors text-xs"
            >
              <div className="font-bold text-blue-300">Sample Glycemic & Lipid Panel</div>
              <div className="text-[11px] text-slate-400">Fasting Glucose 126 mg/dL, HbA1c 6.9%, Metformin</div>
            </button>

            <button
              onClick={() => handleLoadSampleReport('cbc')}
              disabled={isProcessing}
              className="w-full text-left p-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors text-xs"
            >
              <div className="font-bold text-blue-300">Sample Complete Blood Count (CBC)</div>
              <div className="text-[11px] text-slate-400">Hemoglobin 13.8 g/dL, WBC 6800, Platelets</div>
            </button>
          </div>
        </div>
      </div>

      {/* Review & Edit Extracted Fields */}
      {processedDoc && (
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden animate-in fade-in duration-200">
          <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  {language === 'te' ? 'విలువలను తనిఖీ చేయండి' : 'Check the extracted values'}
                </h3>
                {processedDoc.specialty && processedDoc.specialty !== 'General Medicine' && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                    {processedDoc.specialty}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {language === 'te' ? 'ఏదైనా విలువ తప్పు అయితే సరిచేయవచ్చు. అసలు విలువ భద్రంగా ఉంటుంది.' : 'You can fix any value. The original is always kept.'}
              </p>
            </div>

            <button
              onClick={() => onNavigate('explainer', processedDoc.id)}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs shadow-sm transition-colors self-start sm:self-auto"
            >
              <span>View AI Explainer</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Plain-language summary for this report */}
          {(processedDoc.summary?.english_summary || processedDoc.summary?.telugu_summary) && (
            <div className="px-5 py-4 bg-blue-50/50 border-b border-blue-100">
              <div className="flex items-center space-x-1.5 text-[11px] font-bold text-blue-800 mb-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                <span>{language === 'te' ? 'సులభమైన సారాంశం' : 'In plain language'}</span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
                {language === 'te'
                  ? processedDoc.summary?.telugu_summary || processedDoc.summary?.english_summary
                  : processedDoc.summary?.english_summary}
              </p>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-100 font-semibold">
                <tr>
                  <th className="p-3.5 pl-5">Test Name</th>
                  <th className="p-3.5">Extracted Value</th>
                  <th className="p-3.5">Corrected Value</th>
                  <th className="p-3.5">Unit</th>
                  <th className="p-3.5">Reference Range</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 pr-5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {processedDoc.observations.map((obs) => (
                  <tr key={obs.id} className="hover:bg-slate-50/70">
                    <td className="p-3.5 pl-5 font-bold text-slate-800">{obs.test_name}</td>
                    <td className="p-3.5 font-mono text-slate-600">
                      {obs.original_value}
                      <span className="text-[10px] text-slate-400 block font-sans">Original OCR</span>
                    </td>
                    <td className="p-3.5 font-mono text-blue-700 font-bold">
                      {obs.user_corrected_value || '—'}
                    </td>
                    <td className="p-3.5 text-slate-600">{obs.unit || '—'}</td>
                    <td className="p-3.5 text-slate-600">{obs.reference_range_text || '—'}</td>
                    <td className="p-3.5">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        obs.interpretation === 'HIGH'
                          ? 'bg-amber-100 text-amber-800'
                          : obs.interpretation === 'LOW'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {obs.interpretation}
                      </span>
                    </td>
                    <td className="p-3.5 pr-5 text-right">
                      {editingObsId === obs.id ? (
                        <div className="flex items-center justify-end space-x-1.5">
                          <input
                            type="text"
                            value={correctedVal}
                            onChange={(e) => setCorrectedVal(e.target.value)}
                            placeholder={obs.original_value}
                            className="w-16 px-2 py-1 text-xs border border-blue-400 rounded-lg outline-none"
                            autoFocus
                          />
                          <button
                            onClick={() => handleSaveCorrection(obs.id)}
                            className="p-1 rounded bg-blue-600 text-white hover:bg-blue-700"
                            title="Save"
                          >
                            <Check className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            setEditingObsId(obs.id);
                            setCorrectedVal(obs.user_corrected_value || obs.original_value);
                          }}
                          className="text-slate-400 hover:text-blue-700 p-1"
                          title="Correct value"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
