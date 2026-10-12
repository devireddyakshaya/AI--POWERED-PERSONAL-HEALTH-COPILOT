import React from 'react';
import { AlertTriangle, ShieldCheck, X } from 'lucide-react';
import { LanguageMode } from '../types';

interface DisclaimerProps {
  isOpen: boolean;
  onClose: () => void;
  language: LanguageMode;
}

export const MedicalDisclaimerModal: React.FC<DisclaimerProps> = ({ isOpen, onClose, language }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in duration-150">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2 text-amber-700 font-bold text-base">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span>{language === 'te' ? 'భద్రత & గోప్యత' : 'Safety & privacy'}</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-4 space-y-3.5 text-xs text-slate-600 leading-relaxed">
          <div className="p-3 bg-amber-50 rounded-xl border border-amber-200/80 text-amber-900 font-medium">
            {language === 'te' ? (
              <p>
                ⚠️ <strong>ముఖ్యమైన వైద్య గమనిక:</strong> హెల్త్‌సాథి AI (MediMitra AI) కేవలం సమాచార ప్రయోజనాల కొరకు రూపొందించబడింది.
                ఇది ఏ వ్యాధి నిర్ధారణను లేదా చికిత్సా మార్పులను స్వతంత్రంగా సిఫార్సు చేయదు. మీ ఆరోగ్య నిర్ణయాల కొరకు ఎల్లప్పుడూ అర్హత కలిగిన వైద్యుడిని సంప్రదించండి.
              </p>
            ) : (
              <p>
                ⚠️ <strong>Important:</strong> MediMitra AI helps you understand your reports.
                It is <strong>not a doctor</strong>. It never diagnoses you or changes your treatment.
                Always talk to a qualified doctor about your health.
              </p>
            )}
          </div>

          <div className="space-y-2">
            <h4 className="font-bold text-slate-800 text-xs flex items-center space-x-1.5">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              <span>{language === 'te' ? 'మా గోప్యతా సూత్రాలు:' : 'Our Privacy & Safety Guarantees:'}</span>
            </h4>
            <ul className="list-disc pl-5 space-y-1 text-slate-600">
              <li>
                <strong>{language === 'te' ? 'ఎటువంటి నిల్వ లేదు:' : 'No files stored:'}</strong> {language === 'te' ? 'అప్‌లోడ్ చేసిన ఫైళ్లు సర్వర్‌లో ఉంచబడవు.' : 'Uploaded files are not kept on any server.'}
              </li>
              <li>
                <strong>{language === 'te' ? 'ఆధారాలు:' : 'Source links:'}</strong> {language === 'te' ? 'ప్రతి వివరణ మీ నివేదికలోని అసలు లైన్‌కు లింక్ చేయబడుతుంది.' : 'Every explanation links back to the exact line in your report.'}
              </li>
              <li>
                <strong>{language === 'te' ? 'గోప్యత:' : 'Private:'}</strong> {language === 'te' ? 'మీ డేటాపై ఎటువంటి ట్రాకింగ్ ఉండదు.' : 'No tracking of your data.'}
              </li>
              <li>
                <strong>{language === 'te' ? 'ABDM సిద్ధత:' : 'ABDM ready:'}</strong> {language === 'te' ? 'డెమో IDలతో ABHA/FHIR మద్దతును చూపుతుంది.' : 'Shows ABHA/FHIR support using demo IDs only.'}
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white rounded-xl shadow-md transition-colors"
          >
            {language === 'te' ? 'అర్థమైంది' : 'I understand'}
          </button>
        </div>
      </div>
    </div>
  );
};
