import React from 'react';
import {
  Activity,
  UploadCloud,
  FileText,
  GitCompare,
  Clock,
  HelpCircle,
  Pill,
  ShieldCheck,
  AlertTriangle,
  Layers,
  Users
} from 'lucide-react';
import { LanguageMode, PatientProfile } from '../types';
import { LANGUAGES, t } from '../i18n/translations';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  language: LanguageMode;
  setLanguage: (lang: LanguageMode) => void;
  openDisclaimer: () => void;
  isDemoMode?: boolean;
  patients?: PatientProfile[];
  activePatientId?: number | null;
  onSelectPatient?: (patientId: number) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  language,
  setLanguage,
  openDisclaimer,
  isDemoMode = false,
  patients = [],
  activePatientId = null,
  onSelectPatient
}) => {
  const activePatient = patients.find((p) => p.id === activePatientId) || null;
  const abhaLabel = activePatient?.synthetic_abha_id || 'No record';
  const profileLabel = activePatient
    ? `${activePatient.full_name}${activePatient.age ? ` • ${activePatient.age}y` : ''}${activePatient.gender ? ` • ${activePatient.gender}` : ''}`
    : 'No patient selected';

  const navItems = [
    { id: 'dashboard', label: t(language, 'nav_dashboard'), icon: Activity },
    { id: 'upload', label: t(language, 'nav_upload'), icon: UploadCloud },
    { id: 'explainer', label: t(language, 'nav_explainer'), icon: FileText },
    { id: 'comparison', label: t(language, 'nav_comparison'), icon: GitCompare },
    { id: 'timeline', label: t(language, 'nav_timeline'), icon: Clock },
    { id: 'doctor-prep', label: t(language, 'nav_doctor'), icon: HelpCircle },
    { id: 'medications', label: t(language, 'nav_medications'), icon: Pill },
    { id: 'privacy-vault', label: t(language, 'nav_privacy'), icon: ShieldCheck },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      {/* Top Banner: Synthetic ABHA & Demo Notice */}
      <div className="bg-slate-900 text-slate-300 text-xs py-1.5 px-4 flex flex-wrap items-center justify-between gap-2 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-900/80 text-blue-300 border border-blue-700/60">
            HacXLerate 2026
          </span>
          <span className="text-slate-400">Team TEKSQUADS</span>
          <span className="text-slate-600 hidden sm:inline">•</span>
          <span className="hidden sm:inline text-slate-400">Your health records, clearly understood.</span>
        </div>
        <div className="flex items-center space-x-3 text-[11px]">
          {patients.length > 1 && onSelectPatient ? (
            <label className="inline-flex items-center space-x-1.5 bg-slate-800 px-2 py-0.5 rounded text-slate-300 border border-slate-700">
              <Users className="w-3 h-3 text-blue-400" />
              <span className="text-slate-400">Patient:</span>
              <select
                value={activePatientId ?? ''}
                onChange={(e) => onSelectPatient(Number(e.target.value))}
                className="bg-transparent text-blue-300 font-medium outline-none cursor-pointer"
              >
                {patients.map((p) => (
                  <option key={p.id} value={p.id} className="text-slate-900">
                    {p.full_name}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <div className="inline-flex items-center space-x-1.5 bg-slate-800 px-2 py-0.5 rounded text-slate-300 border border-slate-700">
              <Layers className="w-3 h-3 text-blue-400" />
              <span className="font-mono text-blue-300 font-medium">ABHA:</span>
              <span className="text-slate-200">{abhaLabel}</span>
            </div>
          )}
          {activePatient && (
            <span className="hidden md:inline text-slate-400">{profileLabel}</span>
          )}
          {isDemoMode && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-amber-950/70 text-amber-300 border border-amber-800/80">
              DEMO MODE
            </span>
          )}
        </div>
      </div>

      {/* Main Brand & Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Product Name */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-700 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Activity className="w-6 h-6 stroke-[2.2]" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="text-xl font-bold tracking-tight text-slate-900">MediMitra</span>
                <span className="text-xs font-extrabold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                  AI
                </span>
              </div>
              <p className="text-[11px] font-medium text-slate-500 hidden sm:block">
                Personal Health Copilot
              </p>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-blue-50 text-blue-800 shadow-xs border border-blue-200/80 font-bold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-blue-600 stroke-[2.5]' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Language Selector & Disclaimer Button */}
          <div className="flex items-center space-x-2">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as LanguageMode)}
              aria-label="Select language"
              className="px-2.5 py-1.5 text-xs font-bold rounded-lg bg-slate-100 border border-slate-200 text-slate-700 outline-none focus:border-blue-400 cursor-pointer"
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.nativeLabel} ({lang.label})
                </option>
              ))}
            </select>

            {/* Medical Disclaimer trigger button */}
            <button
              onClick={openDisclaimer}
              className="p-2 text-slate-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg border border-transparent hover:border-amber-200 transition-colors"
              title="Medical Safety & Privacy Notice"
            >
              <AlertTriangle className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Mobile / Tablet Horizontal Navigation Scroll */}
        <div className="lg:hidden flex overflow-x-auto py-2 border-t border-slate-100 gap-1 no-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs whitespace-nowrap font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white font-bold'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
