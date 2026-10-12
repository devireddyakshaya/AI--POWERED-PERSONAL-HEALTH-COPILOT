import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Lock,
  Trash2,
  Layers,
  Code2,
  CheckCircle2,
  Database,
  EyeOff,
  Cpu,
  FileCode,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { LanguageMode } from '../types';
import { fetchFhirBundle, clearAllRecords } from '../services/api';

interface PrivacyProps {
  language: LanguageMode;
  activeDocumentId?: number | null;
  onDataPurged: () => void;
}

export const PrivacyVaultPage: React.FC<PrivacyProps> = ({ language, activeDocumentId = null, onDataPurged }) => {
  const [fhirData, setFhirData] = useState<any>(null);
  const [isCopied, setIsCopied] = useState(false);
  const [isPurging, setIsPurging] = useState(false);

  useEffect(() => {
    loadFhir();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeDocumentId]);

  const loadFhir = async () => {
    if (activeDocumentId == null) {
      setFhirData(null);
      return;
    }
    try {
      const bundle = await fetchFhirBundle(activeDocumentId);
      setFhirData(bundle);
    } catch (err) {
      console.error(err);
      setFhirData(null);
    }
  };

  const handlePurge = async () => {
    if (!window.confirm(language === 'te' ? 'అన్ని నివేదికలను తొలగించాలా? ఇది వెనక్కి తీసుకోలేము.' : 'Delete all reports? This cannot be undone.')) {
      return;
    }
    setIsPurging(true);
    try {
      await clearAllRecords();
      setFhirData(null);
      onDataPurged();
      alert(language === 'te' ? 'అన్ని నివేదికలు తొలగించబడ్డాయి.' : 'All records deleted.');
    } catch (err) {
      alert(language === 'te' ? 'తొలగించడం విఫలమైంది.' : 'Failed to delete records.');
    } finally {
      setIsPurging(false);
    }
  };

  const handleCopyJson = () => {
    if (!fhirData) return;
    navigator.clipboard.writeText(JSON.stringify(fhirData, null, 2));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
            {language === 'te' ? 'గోప్యత & డేటా' : 'Privacy & your data'}
          </h1>
          <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
            {language === 'te' ? 'గోప్యత' : 'Privacy'}
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {language === 'te'
            ? 'మీ డేటా మీ దగ్గరే ఉంటుంది. ఎప్పుడైనా తొలగించవచ్చు.'
            : 'Your data stays with you. Delete it any time.'}
        </p>
      </div>

      {/* Privacy Guarantees Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
          <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
            <EyeOff className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">{language === 'te' ? 'ఫైళ్లు నిల్వ ఉండవు' : 'No files stored'}</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            {language === 'te'
              ? 'మీరు అప్‌లోడ్ చేసిన ఫైల్‌లు చదివిన తర్వాత సర్వర్‌లో ఉంచబడవు.'
              : 'Uploaded files are read and then not kept on any server.'}
          </p>
        </div>

        <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
          <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
            <Database className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">{language === 'te' ? 'మీ పరికరంలోనే నిల్వ' : 'Stored on your device'}</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            {language === 'te'
              ? 'మీ నివేదికలు మీ పరికరంలోని స్థానిక డేటాబేస్‌లో ఉంటాయి. ఎటువంటి ట్రాకింగ్ లేదు.'
              : 'Records are saved in a local database on your device. No trackers.'}
          </p>
        </div>

        <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
          <div className="w-9 h-9 rounded-xl bg-rose-50 text-rose-700 flex items-center justify-center">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">{language === 'te' ? 'ఎప్పుడైనా తొలగించండి' : 'Delete anytime'}</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            {language === 'te'
              ? 'ఒక నివేదికను తొలగిస్తే దానికి సంబంధించిన మొత్తం డేటా పోతుంది.'
              : 'Delete a report and all its related data goes with it.'}
          </p>
        </div>
      </div>

      {/* Interactive System Architecture Diagram */}
      <div className="p-6 bg-white rounded-2xl border border-slate-200/90 shadow-xs space-y-6">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-blue-600" />
            <span>{language === 'te' ? 'మీ నివేదిక ఎలా ప్రాసెస్ అవుతుంది' : 'How your report is processed'}</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            {language === 'te' ? 'అప్‌లోడ్ నుండి ప్రామాణిక ఆకృతి వరకు నాలుగు దశలు.' : 'Four steps from upload to standard format.'}
          </p>
        </div>

        {/* Visual Pipeline Flow */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <span className="font-mono text-[10px] text-blue-700 font-bold uppercase">{language === 'te' ? 'దశ 1 • అప్‌లోడ్' : 'Step 1 • Upload'}</span>
            <h4 className="font-bold text-slate-800">{language === 'te' ? 'అప్‌లోడ్' : 'Upload'}</h4>
            <p className="text-[11px] text-slate-500">
              {language === 'te' ? 'PDF లేదా ఫోటో (JPG/PNG).' : 'PDF or photo (JPG/PNG).'}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <span className="font-mono text-[10px] text-blue-700 font-bold uppercase">{language === 'te' ? 'దశ 2 • చదవడం' : 'Step 2 • Read'}</span>
            <h4 className="font-bold text-slate-800">{language === 'te' ? 'నివేదిక చదవడం' : 'Read the report'}</h4>
            <p className="text-[11px] text-slate-500">
              {language === 'te' ? 'పరీక్షలు, విలువలు, సాధారణ పరిధులు గుర్తిస్తుంది.' : 'Finds tests, values, and normal ranges.'}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <span className="font-mono text-[10px] text-amber-700 font-bold uppercase">{language === 'te' ? 'దశ 3 • వివరణ' : 'Step 3 • Explain'}</span>
            <h4 className="font-bold text-slate-800">{language === 'te' ? 'సులభంగా వివరణ' : 'Explain simply'}</h4>
            <p className="text-[11px] text-slate-500">
              {language === 'te' ? 'సులభమైన ఇంగ్లీష్ + తెలుగు, మూలంతో లింకులతో.' : 'Simple English + Telugu, with source links.'}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <span className="font-mono text-[10px] text-indigo-700 font-bold uppercase">{language === 'te' ? 'దశ 4 • ప్రమాణం' : 'Step 4 • Standard'}</span>
            <h4 className="font-bold text-slate-800">{language === 'te' ? 'ప్రామాణిక ఆకృతి' : 'Standard format'}</h4>
            <p className="text-[11px] text-slate-500">
              {language === 'te' ? 'ABDM/FHIR అనే ఉమ్మడి ఆరోగ్య ఆకృతిలో డేటా.' : 'Shares data in the common ABDM/FHIR format.'}
            </p>
          </div>
        </div>
      </div>

      {/* ABDM Bonus: Interactive FHIR R4 Bundle Explorer */}
      <div className="bg-slate-900 text-slate-100 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-blue-400" />
              <h3 className="text-sm font-bold text-white">
                {language === 'te' ? 'ప్రామాణిక ఆరోగ్య డేటా (FHIR / ABDM)' : 'Standard health data (FHIR / ABDM)'}
              </h3>
            </div>
            <p className="text-xs text-slate-400">
              {language === 'te'
                ? 'మీ నివేదికల నుండి తయారు చేసిన ప్రామాణిక డేటా. ABDM సిద్ధతను చూపుతుంది.'
                : 'Standard data made from your reports. Shows ABDM readiness.'}
            </p>
          </div>

          <button
            onClick={handleCopyJson}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-blue-300 text-xs font-mono font-bold transition-colors"
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>{isCopied ? (language === 'te' ? 'కాపీ అయింది!' : 'Copied!') : (language === 'te' ? 'FHIR JSON కాపీ' : 'Copy FHIR JSON')}</span>
          </button>
        </div>

        {/* Code viewer */}
        <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 font-mono text-xs text-blue-300 max-h-72 overflow-y-auto">
          <pre className="whitespace-pre-wrap leading-relaxed">
            {fhirData
              ? JSON.stringify(fhirData, null, 2)
              : activeDocumentId == null
              ? `// ${language === 'te' ? 'FHIR బండిల్ చూడటానికి ఒక నివేదికను అప్‌లోడ్ చేయండి.' : 'Upload a report to view its FHIR bundle.'}`
              : `// ${language === 'te' ? 'లోడ్ అవుతోంది...' : 'Loading FHIR R4 Bundle...'}`}
          </pre>
        </div>
      </div>

      {/* Vault Reset & Data Purge Controls */}
      <div className="p-6 bg-rose-50/60 rounded-2xl border border-rose-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h4 className="text-sm font-bold text-rose-950">{language === 'te' ? 'అన్ని డేటా తొలగించు' : 'Delete all data'}</h4>
          <p className="text-xs text-rose-800 mt-0.5">
            {language === 'te'
              ? 'అన్ని అప్‌లోడ్ చేసిన నివేదికలను శాశ్వతంగా తొలగిస్తుంది.'
              : 'Permanently deletes all uploaded reports.'}
          </p>
        </div>

        <button
          onClick={handlePurge}
          disabled={isPurging}
          className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-rose-700 hover:bg-rose-800 text-white text-xs font-bold shadow-sm transition-colors shrink-0 disabled:opacity-50"
        >
          <Trash2 className="w-4 h-4" />
          <span>{isPurging ? (language === 'te' ? 'తొలగిస్తోంది...' : 'Deleting...') : (language === 'te' ? 'అన్నీ తొలగించు' : 'Delete all records')}</span>
        </button>
      </div>
    </div>
  );
};
