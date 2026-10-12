import React, { useEffect, useState } from 'react';
import {
  FileText,
  CheckCircle2,
  FileSearch,
  HelpCircle,
  Sparkles,
  Info,
  Calendar,
  Building,
  Volume2
} from 'lucide-react';
import { DocumentDetail, KeyFinding, LanguageMode, LocalizedExplanation } from '../types';
import { LANGUAGES, t } from '../i18n/translations';
import { useSpeech } from '../hooks/useSpeech';
import { fetchLocalizedExplanation } from '../services/api';
import { EvidenceViewerModal } from '../components/EvidenceViewerModal';

interface ExplainerProps {
  document: DocumentDetail | null;
  allDocuments: DocumentDetail[];
  onSelectDocument: (id: number) => void;
  language: LanguageMode;
  setLanguage: (lang: LanguageMode) => void;
}

export const ExplainerPage: React.FC<ExplainerProps> = ({
  document,
  allDocuments,
  onSelectDocument,
  language,
  setLanguage
}) => {
  const [selectedFinding, setSelectedFinding] = useState<KeyFinding | null>(null);
  const [simpleMode, setSimpleMode] = useState(false);
  const [localized, setLocalized] = useState<LocalizedExplanation | null>(null);
  const speech = useSpeech(language);

  const isCoreLang = language === 'en' || language === 'te';

  useEffect(() => {
    let active = true;
    if (!document || isCoreLang) {
      setLocalized(null);
      return;
    }
    fetchLocalizedExplanation(document.id, language).then((res) => {
      if (active) setLocalized(res);
    });
    return () => {
      active = false;
    };
  }, [document, language, isCoreLang]);

  if (!document) {
    return (
      <div className="py-12 text-center text-slate-500">
        <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <p className="text-sm">No report selected for explanation. Please choose or upload a document.</p>
      </div>
    );
  }

  const summary = document.summary;
  const findings = summary?.key_findings || [];
  const questions = summary?.questions_for_doctor || [];

  return (
    <div className="space-y-8 py-4">
      {/* Top Selector & Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
              {language === 'te' ? 'నివేదిక వివరణ' : 'Report explained'}
            </h1>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
              {language === 'te' ? 'ఆధారంతో' : 'Source-linked'}
            </span>
          </div>
          <div className="flex items-center space-x-3 text-xs text-slate-500 mt-1">
            <span className="flex items-center space-x-1">
              <Building className="w-3.5 h-3.5 text-slate-400" />
              <span>{document.laboratory_name || 'Laboratory'}</span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>{document.document_date || 'Date'}</span>
            </span>
          </div>
        </div>

        {/* Report Selector dropdown */}
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <select
            value={document.id}
            onChange={(e) => onSelectDocument(Number(e.target.value))}
            className="w-full sm:w-auto px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 outline-none focus:border-blue-400"
          >
            {allDocuments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.file_name} ({d.document_date})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main AI Summary Box (English & Telugu Toggle) */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="p-5 bg-gradient-to-r from-blue-50/60 to-white border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-bold text-slate-900">
              {language === 'te' ? 'మీ నివేదిక సులభంగా' : 'Your report, explained simply'}
            </h3>
            {summary?.is_demo_generated && (
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                Demo
              </span>
            )}
          </div>

          <div className="flex items-center space-x-3">
            {/* Simple-Language Mode Toggle */}
            <label className="flex items-center space-x-1.5 text-xs text-slate-600 cursor-pointer">
              <input
                type="checkbox"
                checked={simpleMode}
                onChange={(e) => setSimpleMode(e.target.checked)}
                className="rounded text-blue-600 focus:ring-blue-500 w-3.5 h-3.5"
              />
              <span className="font-medium">Simple-Language Mode</span>
            </label>

            {/* Read aloud */}
            <button
              onClick={() =>
                speech.speak(
                  localized?.summary ||
                    (language === 'te' ? summary?.telugu_summary : summary?.english_summary) ||
                    ''
                )
              }
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold transition-colors"
              title="Read aloud"
            >
              <Volume2 className="w-3.5 h-3.5" />
              <span>{t(language, 'read_report')}</span>
            </button>

            {/* Language Switch */}
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as LanguageMode)}
              className="px-2.5 py-1.5 bg-slate-100 border border-slate-200 rounded-lg text-xs font-bold text-slate-700 outline-none focus:border-blue-400 cursor-pointer"
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.nativeLabel}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="p-6 text-sm text-slate-700 leading-relaxed whitespace-pre-line">
          {localized?.summary ||
            (language === 'te' ? summary?.telugu_summary : summary?.english_summary)}
        </div>

        {summary?.uncertainty_notes && (
          <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 text-[11px] text-slate-500 flex items-center space-x-2">
            <Info className="w-4 h-4 text-slate-400 shrink-0" />
            <span>{summary.uncertainty_notes}</span>
          </div>
        )}
      </div>

      {/* Feature 2: Evidence-Linked Findings Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-1.5">
              <FileSearch className="w-4 h-4 text-blue-600" />
              <span>{language === 'te' ? 'ముఖ్యమైన ఫలితాలు' : 'Key findings'}</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {language === 'te' ? 'ఏదైనా ఫలితంపై నొక్కి మీ నివేదికలోని అసలు లైన్ చూడండి.' : 'Tap any finding to see the exact line from your report.'}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {findings.map((f, idx) => (
            <div
              key={idx}
              onClick={() => setSelectedFinding(f)}
              className="p-4 bg-white rounded-xl border border-slate-200/80 hover:border-blue-400 shadow-xs hover:shadow-md cursor-pointer transition-all group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-800">{f.title}</span>
                <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold ${
                  f.interpretation === 'ABNORMAL_HIGH'
                    ? 'bg-amber-100 text-amber-800'
                    : f.interpretation === 'ABNORMAL_LOW'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-emerald-100 text-emerald-800'
                }`}>
                  {f.interpretation === 'ABNORMAL_HIGH' ? 'Elevated' : f.interpretation === 'ABNORMAL_LOW' ? 'Below Normal' : 'Normal'}
                </span>
              </div>

              <p className="text-xs text-slate-600 leading-normal">{f.finding}</p>

              <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
                <span className="text-slate-400 font-mono">Ref: {f.reference_range || 'Standard'}</span>
                <span className="text-blue-700 font-bold group-hover:underline flex items-center space-x-1">
                  <span>View Source Excerpt</span>
                  <span>→</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Doctor Discussion Questions */}
      {questions.length > 0 && (
        <div className="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-xs space-y-3">
          <div className="flex items-center space-x-2 text-indigo-700 font-bold text-sm">
            <HelpCircle className="w-5 h-5" />
            <span>{language === 'te' ? 'మీ వైద్యుడిని అడగవలసిన ప్రశ్నలు' : 'Questions to ask your doctor'}</span>
          </div>
          <p className="text-xs text-slate-500">
            {language === 'te' ? 'మీ ఫలితాల ఆధారంగా సిద్ధం చేసిన ప్రశ్నలు.' : 'Suggested questions based on your results.'}
          </p>

          <div className="space-y-2 pt-2">
            {questions.map((q, idx) => (
              <div key={idx} className="p-3 bg-indigo-50/50 rounded-xl border border-indigo-100 text-xs text-slate-700 flex items-start space-x-2.5">
                <span className="font-bold text-indigo-700 shrink-0">{idx + 1}.</span>
                <span>{q}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal for clicked evidence */}
      <EvidenceViewerModal
        finding={selectedFinding}
        onClose={() => setSelectedFinding(null)}
        language={language}
      />
    </div>
  );
};
