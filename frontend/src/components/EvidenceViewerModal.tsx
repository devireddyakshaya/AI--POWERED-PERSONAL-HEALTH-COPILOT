import React from 'react';
import { FileSearch, CheckCircle2, AlertCircle, X, ShieldAlert } from 'lucide-react';
import { KeyFinding, LanguageMode } from '../types';

interface EvidenceModalProps {
  finding: KeyFinding | null;
  onClose: () => void;
  language: LanguageMode;
}

export const EvidenceViewerModal: React.FC<EvidenceModalProps> = ({ finding, onClose, language }) => {
  if (!finding) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in duration-150">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2 text-blue-800 font-bold text-sm">
            <FileSearch className="w-5 h-5 text-blue-600" />
            <span>{language === 'te' ? 'మీ నివేదిక నుండి' : 'From your report'}</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-4 space-y-4">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              {language === 'te' ? 'ఫలితం' : 'Finding'}
            </span>
            <h3 className="text-base font-bold text-slate-800">{finding.title}</h3>
            <p className="text-xs text-slate-600 mt-0.5">{finding.finding}</p>
          </div>

          <div className="p-3.5 bg-slate-900 text-blue-300 font-mono text-xs rounded-xl border border-slate-800 shadow-inner">
            <div className="flex items-center justify-between text-[10px] text-slate-400 border-b border-slate-800 pb-1.5 mb-2">
              <span>{language === 'te' ? 'మీ నివేదిక నుండి' : 'FROM YOUR REPORT'}</span>
              <span>{language === 'te' ? 'పేజీ 1' : 'PAGE 1'}</span>
            </div>
            <p className="leading-relaxed whitespace-pre-wrap">
              "{finding.evidence_excerpt}"
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-slate-500 text-[10px] block font-medium">{language === 'te' ? 'సాధారణ పరిధి' : 'Normal range'}</span>
              <span className="font-semibold text-slate-800">{finding.reference_range || (language === 'te' ? 'ఇవ్వబడలేదు' : 'Not given')}</span>
            </div>
            <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-slate-500 text-[10px] block font-medium">{language === 'te' ? 'ఖచ్చితత్వం' : 'Accuracy'}</span>
              <span className="font-semibold text-blue-700 flex items-center space-x-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                <span>{language === 'te' ? 'నివేదికతో నిర్ధారించబడింది' : 'Verified from report'}</span>
              </span>
            </div>
          </div>

          {finding.needs_verification && (
            <div className="p-2.5 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 text-xs flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
              <span>{language === 'te' ? 'చేతిరాత లేదా స్పష్టత తక్కువ కావడంతో ఒకసారి తనిఖీ చేయండి.' : 'Please check this value - handwriting or low scan quality.'}</span>
            </div>
          )}
        </div>

        <div className="mt-5 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors"
          >
            {language === 'te' ? 'మూసివేయి' : 'Close'}
          </button>
        </div>
      </div>
    </div>
  );
};
