import React from 'react';
import {
  UploadCloud,
  FileText,
  GitCompare,
  ShieldCheck,
  HelpCircle,
  Pill,
  ArrowRight,
  CheckCircle2,
  Mic,
  Layers
} from 'lucide-react';
import { LanguageMode } from '../types';

interface LandingProps {
  onStart: (tab: string) => void;
  language: LanguageMode;
}

export const LandingPage: React.FC<LandingProps> = ({ onStart, language }) => {
  const isTe = language === 'te';

  const features = [
    {
      icon: FileText,
      color: 'blue',
      title: isTe ? 'సులభమైన నివేదిక వివరణ' : 'Read reports in plain words',
      desc: isTe ? 'మీ రక్త పరీక్షలను సులభంగా అర్థమయ్యే భాషలో చెబుతుంది.' : 'We explain your lab values in simple language.'
    },
    {
      icon: GitCompare,
      color: 'cyan',
      title: isTe ? 'మార్పులను పోల్చండి' : 'Track changes over time',
      desc: isTe ? 'పాత మరియు కొత్త నివేదికలను పోల్చి మార్పులు చూపుతుంది.' : 'Compare old and new reports side by side.'
    },
    {
      icon: HelpCircle,
      color: 'indigo',
      title: isTe ? 'డాక్టర్ ప్రశ్నలు' : 'Prepare doctor questions',
      desc: isTe ? 'డాక్టర్‌ను అడగవలసిన ప్రశ్నల జాబితా ఇస్తుంది.' : 'Get a ready list of questions to ask your doctor.'
    },
    {
      icon: Pill,
      color: 'amber',
      title: isTe ? 'మందుల రిమైండర్లు' : 'Medicine reminders',
      desc: isTe ? 'మందుల సమయాన్ని గుర్తు చేస్తుంది.' : 'Turn prescriptions into simple daily reminders.'
    },
    {
      icon: Mic,
      color: 'rose',
      title: isTe ? 'వాయిస్ సహాయకుడు' : 'Talk to the voice assistant',
      desc: isTe ? 'మాట్లాడి ప్రశ్నలు అడగండి, సమాధానం వినండి.' : 'Ask questions by voice and hear the answer.'
    },
    {
      icon: ShieldCheck,
      color: 'emerald',
      title: isTe ? 'గోప్యత ముందుగా' : 'Privacy first',
      desc: isTe ? 'మీ డేటా మీ దగ్గరే ఉంటుంది. ఎప్పుడైనా తొలగించవచ్చు.' : 'Your data stays with you. Delete it any time.'
    }
  ];

  const steps = [
    { n: 1, title: isTe ? 'అప్‌లోడ్ చేయండి' : 'Upload', desc: isTe ? 'మీ నివేదిక లేదా ప్రిస్క్రిప్షన్.' : 'Add your report or prescription.' },
    { n: 2, title: isTe ? 'అర్థం చేసుకోండి' : 'Understand', desc: isTe ? 'సులభమైన వివరణ మరియు ముఖ్య ఫలితాలు.' : 'See clear results and simple explanations.' },
    { n: 3, title: isTe ? 'నడిపించండి' : 'Act', desc: isTe ? 'పోలికలు, ప్రశ్నలు, రిమైండర్లు.' : 'Compare, ask questions, set reminders.' }
  ];

  return (
    <div className="space-y-14 py-6">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50/70 via-slate-50 to-white rounded-3xl p-7 sm:p-12 border border-blue-100/60 shadow-xs">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-100/80 border border-blue-200 text-blue-800 text-xs font-bold mb-5">
            <Mic className="w-3.5 h-3.5 text-blue-600" />
            <span>{isTe ? 'వాయిస్-ఫస్ట్ ఆరోగ్య సహాయకుడు' : 'Voice-first health assistant'}</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-[1.12]">
            {isTe ? (
              <>
                మీ ఆరోగ్య నివేదికలు. <br />
                <span className="text-blue-700">సులభంగా అర్థం చేసుకోండి.</span>
              </>
            ) : (
              <>
                Your health reports. <br />
                <span className="text-blue-700">Clearly understood.</span>
              </>
            )}
          </h1>

          <p className="mt-4 text-sm sm:text-base text-slate-600 leading-relaxed max-w-xl">
            {isTe
              ? 'నివేదికలను అప్‌లోడ్ చేయండి. సులభమైన వివరణలు పొందండి. మాట్లాడి ప్రశ్నలు అడగండి.'
              : 'Upload a report. Get simple explanations. Ask questions by voice.'}
          </p>

          {/* Key points */}
          <ul className="mt-5 space-y-1.5 text-sm text-slate-700">
            {(isTe
              ? ['ఏ నివేదికనైనా అప్‌లోడ్ చేయండి', 'సులభమైన భాషలో వివరణ', 'వాయిస్‌తో ప్రశ్నలు అడగండి']
              : ['Upload any medical report', 'Flat, easy explanations', 'Ask questions by voice']
            ).map((item) => (
              <li key={item} className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>

          <div className="mt-7 flex flex-wrap gap-3 items-center">
            <button
              onClick={() => onStart('upload')}
              className="flex items-center space-x-2 px-6 py-3.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-sm shadow-md shadow-blue-700/20 transition-all"
            >
              <UploadCloud className="w-4 h-4" />
              <span>{isTe ? 'నివేదిక అప్‌లోడ్ చేయండి' : 'Upload a report'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => onStart('dashboard')}
              className="flex items-center space-x-2 px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 font-bold text-sm border border-slate-300 shadow-xs hover:border-blue-300 transition-all"
            >
              <FileText className="w-4 h-4 text-blue-600" />
              <span>{isTe ? 'డెమో చూడండి' : 'See the demo'}</span>
            </button>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="space-y-6">
        <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 text-center">
          {isTe ? 'ఇది ఎలా పనిచేస్తుంది' : 'How it works'}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {steps.map((step) => (
            <div key={step.n} className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs">
              <div className="w-9 h-9 rounded-full bg-blue-700 text-white flex items-center justify-center font-extrabold mb-3">
                {step.n}
              </div>
              <h3 className="text-sm font-bold text-slate-900">{step.title}</h3>
              <p className="text-xs text-slate-500 mt-1">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="space-y-6">
        <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 text-center">
          {isTe ? 'మీరు ఏమి చేయగలరు' : 'What you can do'}
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => {
            const Icon = f.icon;
            return (
              <div
                key={f.title}
                className="p-5 rounded-2xl bg-white border border-slate-200/80 hover:border-blue-200 shadow-xs hover:shadow-md transition-all"
              >
                <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center mb-3">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-sm font-bold text-slate-800">{f.title}</h3>
                <p className="text-xs text-slate-500 mt-1">{f.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* ABDM callout */}
      <section className="bg-slate-900 text-slate-100 rounded-3xl p-7 sm:p-9 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
        <div className="space-y-1.5 max-w-xl">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-blue-900 text-blue-300 text-[11px] font-bold">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>{isTe ? 'ABDM సిద్ధమైనది' : 'ABDM-ready'}</span>
          </div>
          <h3 className="text-lg font-extrabold text-white">
            {isTe ? 'ప్రామాణిక ఆరోగ్య డేటా (FHIR R4)' : 'Built on open health standards (FHIR R4)'}
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            {isTe
              ? 'మీ రికార్డులు ప్రామాణిక ఆకృతిలో ఉంటాయి. భవిష్యత్ ఆరోగ్య వ్యవస్థలతో పనిచేయడానికి సిద్ధం.'
              : 'Your records are saved in a standard format, ready for India\'s digital health system.'}
          </p>
        </div>
        <button
          onClick={() => onStart('privacy-vault')}
          className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shrink-0 shadow-md transition-colors"
        >
          {isTe ? 'గోప్యత & FHIR చూడండి' : 'View privacy & FHIR'}
        </button>
      </section>
    </div>
  );
};
