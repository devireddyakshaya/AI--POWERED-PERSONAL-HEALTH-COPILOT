import React from 'react';
import {
  Activity,
  UploadCloud,
  FileText,
  GitCompare,
  HelpCircle,
  Pill,
  Clock,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Eye,
  Calendar,
  Heart,
  TrendingDown,
  TrendingUp,
  Minus,
  Layers,
  Check,
  Inbox
} from 'lucide-react';
import { DocumentSummary, DocumentDetail, LanguageMode, PatientProfile } from '../types';

interface DashboardProps {
  documents: DocumentSummary[];
  allDocuments: DocumentDetail[];
  activePatient: PatientProfile | null;
  isLoading: boolean;
  onNavigate: (tab: string, docId?: number) => void;
  language: LanguageMode;
}

interface BiomarkerRow {
  name: string;
  latest: string;
  prior: string;
  goal: string;
  delta: string;
  status: string;
  direction: 'up' | 'down' | 'stable';
  statusColor: 'emerald' | 'amber' | 'blue';
}

const toNumber = (value?: string | number | null): number | null => {
  if (value === null || value === undefined) return null;
  const n = typeof value === 'number' ? value : parseFloat(String(value));
  return Number.isFinite(n) ? n : null;
};

const interpColor = (interp?: string): 'emerald' | 'amber' | 'blue' => {
  if (interp === 'HIGH') return 'amber';
  if (interp === 'LOW') return 'blue';
  return 'emerald';
};

export const DashboardPage: React.FC<DashboardProps> = ({
  documents,
  allDocuments,
  activePatient,
  isLoading,
  onNavigate,
  language
}) => {
  const totalObs = documents.reduce((acc, d) => acc + (d.observation_count || 0), 0);
  const totalMeds = documents.reduce((acc, d) => acc + (d.medication_count || 0), 0);
  const avgTrust = documents.length
    ? Math.round(documents.reduce((acc, d) => acc + d.trust_score, 0) / documents.length)
    : 0;

  // Build "key results over time" strictly from this patient's real reports.
  // allDocuments is ordered newest-first by the backend.
  const series: Record<string, { values: { value: number; unit: string; ref: string; interp: string; date?: string }[]; display: string }> = {};
  allDocuments.forEach((doc) => {
    (doc.observations || []).forEach((obs) => {
      const num = toNumber(obs.standardized_value ?? obs.user_corrected_value ?? obs.original_value);
      if (num === null) return;
      const key = obs.test_name.trim().toLowerCase();
      if (!series[key]) series[key] = { values: [], display: obs.test_name };
      series[key].values.push({
        value: num,
        unit: obs.unit || '',
        ref: obs.reference_range_text || '—',
        interp: obs.interpretation,
        date: doc.document_date
      });
    });
  });

  const biomarkerRows: BiomarkerRow[] = Object.values(series)
    .filter((s) => s.values.length > 0)
    .sort((a, b) => {
      const aAbn = a.values[0].interp !== 'NORMAL' ? 0 : 1;
      const bAbn = b.values[0].interp !== 'NORMAL' ? 0 : 1;
      return aAbn - bAbn;
    })
    .slice(0, 4)
    .map((s) => {
      const latest = s.values[0];
      const prior = s.values[1];
      const delta =
        prior !== undefined
          ? Math.round((latest.value - prior.value) * 100) / 100
          : null;
      const direction: BiomarkerRow['direction'] =
        delta === null || Math.abs(delta) < 1e-9 ? 'stable' : delta > 0 ? 'up' : 'down';
      const status =
        latest.interp === 'HIGH'
          ? language === 'te' ? 'పరిధి పైన' : 'Above range'
          : latest.interp === 'LOW'
          ? language === 'te' ? 'పరిధి కింద' : 'Below range'
          : language === 'te' ? 'సాధారణం' : 'Within range';
      return {
        name: s.display,
        latest: `${latest.value} ${latest.unit}`.trim(),
        prior: prior ? `${prior.value} ${prior.unit}`.trim() : '—',
        goal: latest.ref,
        delta: delta === null ? '—' : `${delta > 0 ? '+' : ''}${delta} ${latest.unit}`.trim(),
        status,
        direction,
        statusColor: interpColor(latest.interp)
      };
    });

  const latestDoc = allDocuments[0] || null;
  const todayMeds = (latestDoc?.medications || []).slice(0, 4);

  if (!activePatient) {
    return (
      <div className="py-16 text-center text-slate-500 animate-in fade-in duration-150">
        <Inbox className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-slate-800">
          {language === 'te' ? 'ఇంకా ఎటువంటి ఆరోగ్య నివేదికలు లేవు' : 'No health records yet'}
        </h2>
        <p className="text-sm mt-1">
          {language === 'te'
            ? 'ప్రారంభించడానికి మీ మొదటి నివేదికను అప్‌లోడ్ చేయండి.'
            : 'Upload your first report to get started.'}
        </p>
        <button
          onClick={() => onNavigate('upload')}
          className="mt-5 inline-flex items-center space-x-2 px-5 py-3 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs shadow-md transition-all"
        >
          <UploadCloud className="w-4 h-4" />
          <span>{language === 'te' ? 'నివేదిక అప్‌లోడ్' : 'Upload a report'}</span>
        </button>
      </div>
    );
  }

  const ageGender = [activePatient.age ? `${activePatient.age} Yrs` : null, activePatient.gender]
    .filter(Boolean)
    .join(' • ');

  return (
    <div className="space-y-8 py-4 animate-in fade-in duration-150">
      {/* Patient Profile Header Card */}
      <div className="p-6 bg-gradient-to-r from-blue-900 via-slate-900 to-slate-900 text-white rounded-3xl shadow-md border border-slate-800 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
              {language === 'te' ? 'రోగి ప్రొఫైల్' : 'PATIENT PROFILE'}
            </span>
            <span className="text-xs font-mono text-slate-400">ABHA: {activePatient.synthetic_abha_id}</span>
          </div>

          <div className="flex items-center space-x-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {activePatient.full_name}
            </h1>
            {ageGender && (
              <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                {ageGender}
              </span>
            )}
          </div>

          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            {documents.length > 0
              ? language === 'te'
                ? `మీకు ${documents.length} నివేదికలు ఉన్నాయి. తాజా ఫలితాలు క్రింద ఉన్నాయి.`
                : `You have ${documents.length} saved report${documents.length > 1 ? 's' : ''}. Your latest results are below.`
              : language === 'te'
              ? 'ఇంకా నివేదికలు అప్‌లోడ్ చేయలేదు.'
              : 'No reports have been uploaded yet.'}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => onNavigate('upload')}
            className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-blue-500 hover:bg-blue-400 text-slate-950 font-bold text-xs shadow-md transition-all"
          >
            <UploadCloud className="w-4 h-4" />
            <span>{language === 'te' ? 'నివేదిక అప్‌లోడ్' : 'Upload New Report'}</span>
          </button>

          {allDocuments.length >= 2 && (
            <button
              onClick={() => onNavigate('comparison')}
              className="flex items-center space-x-2 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition-all"
            >
              <GitCompare className="w-4 h-4 text-blue-400" />
              <span>{language === 'te' ? 'పోల్చండి' : 'Compare Trends'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:border-blue-300 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">{language === 'te' ? 'నివేదికలు' : 'Saved Reports'}</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-black text-slate-900">{documents.length}</span>
            <span className="text-[11px] text-blue-700 font-semibold">{language === 'te' ? 'సేవ్ చేయబడింది' : 'Saved'}</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">{language === 'te' ? 'ల్యాబ్ నివేదికలు' : 'Lab reports & scans'}</p>
        </div>

        <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:border-blue-300 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">{language === 'te' ? 'పరీక్షలు' : 'Test Results'}</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-black text-slate-900">{totalObs}</span>
            <span className="text-[11px] text-blue-700 font-semibold">{language === 'te' ? 'ఫలితాలు' : 'Results'}</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">{language === 'te' ? 'మీ నివేదికల నుండి' : 'From your reports'}</p>
        </div>

        <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:border-indigo-300 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">{language === 'te' ? 'మందులు' : 'Medicines'}</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-700 flex items-center justify-center">
              <Pill className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-black text-slate-900">{totalMeds}</span>
            <span className="text-[11px] text-indigo-700 font-semibold">{language === 'te' ? 'కనుగొనబడింది' : 'Found'}</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">{language === 'te' ? 'ప్రిస్క్రిప్షన్ల నుండి' : 'From prescriptions'}</p>
        </div>

        <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:border-emerald-300 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">{language === 'te' ? 'ఖచ్చితత్వం' : 'Report Accuracy'}</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-black text-emerald-700">{avgTrust}%</span>
            <span className="text-[11px] text-emerald-600 font-semibold">{language === 'te' ? 'నమ్మకం' : 'Confidence'}</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">{language === 'te' ? 'మీరు తనిఖీ చేసింది' : 'Checked by you'}</p>
        </div>
      </div>

      {/* Key results over time */}
      {biomarkerRows.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-1.5">
                <Heart className="w-4 h-4 text-rose-600" />
                <span>{language === 'te' ? 'కీలక ఫలితాలు' : 'Key results over time'}</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {language === 'te' ? 'మీ తాజా నివేదికల నుండి.' : 'Derived from your latest reports.'}
              </p>
            </div>
{allDocuments.length >= 2 && (
              <button
                onClick={() => onNavigate('comparison')}
                className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
              >
                {language === 'te' ? 'పూర్తి comparison →' : 'See full comparison →'}
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {biomarkerRows.map((bio, idx) => (
              <div key={idx} className="p-4 bg-white rounded-2xl border border-slate-200/80 shadow-xs space-y-2 hover:border-blue-300 transition-all">
                <div className="flex items-center justify-between text-xs gap-2">
                  <span className="font-bold text-slate-800 truncate">{bio.name}</span>
                  <span className={`rounded-xl px-2 py-1 text-[9px] font-bold ${
                    bio.statusColor === 'emerald'
                      ? 'bg-emerald-100 text-emerald-800'
                      : bio.statusColor === 'blue'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {bio.status}
                  </span>
                </div>

                <div className="flex items-baseline justify-between pt-1">
                  <span className="text-xl font-extrabold text-slate-900">{bio.latest}</span>
                  {bio.delta !== '—' && (
                    <span className="text-xs font-mono font-semibold text-blue-700 flex items-center space-x-0.5">
                      {bio.direction === 'up' && <TrendingUp className="w-3.5 h-3.5" />}
                      {bio.direction === 'down' && <TrendingDown className="w-3.5 h-3.5" />}
                      {bio.direction === 'stable' && <Minus className="w-3.5 h-3.5" />}
                      <span>{bio.delta}</span>
                    </span>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                  <span>{language === 'te' ? 'ముందు:' : 'Prior:'} <strong className="text-slate-700">{bio.prior}</strong></span>
                  <span className="text-right">{language === 'te' ? 'పరిధి:' : 'Range:'} <strong className="text-slate-700">{bio.goal}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid: Today's Meds Agenda + Shortcuts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Latest Medicines */}
        <div className="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Pill className="w-4 h-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900">{language === 'te' ? 'తాజా మందులు' : 'Latest medicines'}</h3>
            </div>
            <button
              onClick={() => onNavigate('medications')}
              className="text-xs font-bold text-blue-700 hover:text-blue-800"
            >
              {language === 'te' ? 'ప్లానర్ →' : 'Planner →'}
            </button>
          </div>

          {todayMeds.length > 0 ? (
            <div className="space-y-3">
              {todayMeds.map((m, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-slate-800">{m.medicine_name}</span>
                      <span className="text-xs font-mono text-slate-600">{m.dosage || '—'}</span>
                    </div>
                    <div className="text-[11px] text-slate-500">
                      <span>{m.timing_instructions || m.frequency || '—'}</span>
                      {m.schedule_time && <span> • <span className="font-semibold text-blue-800">{m.schedule_time}</span></span>}
                    </div>
                    {m.is_incomplete && (
                      <span className="text-[10px] text-amber-700 font-bold block">
                        {language === 'te' ? '⚠️ డోస్ స్పష్టంగా లేదు' : '⚠️ Dosage missing - please check'}
                      </span>
                    )}
                  </div>
                  <div className="w-6 h-6 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-slate-300">
                    <Check className="w-3.5 h-3.5" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500">
              {language === 'te'
                ? 'మీ నివేదికల్లో మందులు కనుగొనబడలేదు.'
                : 'No medicines were found in your reports.'}
            </p>
          )}
        </div>

        {/* Feature Action Shortcuts */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <ShortcutCard
            onClick={() => onNavigate('explainer')}
            icon={<FileText className="w-5 h-5" />}
            iconBg="bg-blue-600"
            arrow="text-blue-600"
            title={language === 'te' ? 'నివేదిక వివరణ' : 'Report explainer'}
            desc={language === 'te' ? 'సులభమైన ఇంగ్లీష్ మరియు తెలుగులో వివరణ.' : 'Simple explanation in English and Telugu.'}
            cta={language === 'te' ? 'నివేదిక చూడండి →' : 'Explain report →'}
            ctaColor="text-blue-700"
          />
          <ShortcutCard
            onClick={() => onNavigate('doctor-prep')}
            icon={<HelpCircle className="w-5 h-5" />}
            iconBg="bg-indigo-600"
            arrow="text-indigo-600"
            title={language === 'te' ? 'డాక్టర్ సన్నద్ధత' : 'Doctor prep'}
            desc={language === 'te' ? 'డాక్టర్‌ను అడగవలసిన ప్రశ్నల జాబితా.' : 'A ready list of questions for your doctor.'}
            cta={language === 'te' ? 'ప్రశ్నలు చూడండి →' : 'View questions →'}
            ctaColor="text-indigo-700"
          />
          <ShortcutCard
            onClick={() => onNavigate('timeline')}
            icon={<Clock className="w-5 h-5" />}
            iconBg="bg-slate-800"
            arrow="text-slate-700"
            title={language === 'te' ? 'ఆరోగ్య టైమ్‌లైన్' : 'Health timeline'}
            desc={language === 'te' ? 'మీ పాత నివేదికలను శోధించండి.' : 'Search all your past reports in one place.'}
            cta={language === 'te' ? 'టైమ్‌లైన్ →' : 'Open timeline →'}
            ctaColor="text-slate-800"
          />
          <ShortcutCard
            onClick={() => onNavigate('privacy-vault')}
            icon={<Layers className="w-5 h-5" />}
            iconBg="bg-cyan-700"
            arrow="text-cyan-700"
            title={language === 'te' ? 'గోప్యత & FHIR' : 'Privacy & FHIR'}
            desc={language === 'te' ? 'మీ డేటాను నిర్వహించండి, ప్రామాణిక ఆకృతి చూడండి.' : 'Manage your data and see the standard format.'}
            cta={language === 'te' ? 'గోప్యత →' : 'Open privacy →'}
            ctaColor="text-cyan-800"
          />
        </div>
      </div>

      {/* Recent Medical Records */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">
              {language === 'te' ? 'ఇటీవలి ఆరోగ్య నివేదికలు' : 'Recent Medical Documents'}
            </h2>
          </div>
          {documents.length > 0 && (
            <button
              onClick={() => onNavigate('timeline')}
              className="text-xs font-bold text-blue-700 hover:text-blue-800"
            >
              {language === 'te' ? 'పూర్తి టైమ్‌లైన్ →' : 'View Full Timeline →'}
            </button>
          )}
        </div>

        {documents.length === 0 ? (
          <div className="p-10 text-center text-xs text-slate-500">
            {isLoading
              ? language === 'te' ? 'లోడ్ అవుతోంది...' : 'Loading...'
              : language === 'te' ? 'ఇంకా నివేదికలు లేవు.' : 'No documents yet.'}
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 hover:bg-slate-50/70 transition-colors">
                <div className="flex items-start space-x-3.5">
                  <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600 shrink-0">
                    <FileText className="w-5 h-5 text-blue-700" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2 flex-wrap">
                      <h3 className="text-xs sm:text-sm font-bold text-slate-900">{doc.file_name}</h3>
                      {doc.is_synthetic && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                          {language === 'te' ? 'నమూనా' : 'Synthetic Demo'}
                        </span>
                      )}
                      {doc.specialty && doc.specialty !== 'General Medicine' && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                          {doc.specialty}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-3 text-xs text-slate-500 mt-1 flex-wrap">
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        <span>{doc.document_date || (language === 'te' ? 'తేదీ లేదు' : 'Unknown Date')}</span>
                      </span>
                      <span>•</span>
                      <span>{doc.document_type}</span>
                      <span>•</span>
                      <span className="font-semibold text-slate-700">{doc.observation_count} {language === 'te' ? 'పరీక్షలు' : 'Tests'}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 self-end sm:self-auto">
                  <div className="text-right hidden sm:block">
                    <span className="text-[10px] text-slate-400 block font-medium">{language === 'te' ? 'నమ్మకం' : 'Trust Score'}</span>
                    <span className="text-xs font-bold text-blue-700">{doc.trust_score}%</span>
                  </div>
                  <button
                    onClick={() => onNavigate('explainer', doc.id)}
                    className="flex items-center space-x-1 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-800 text-xs font-bold transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5 text-blue-600" />
                    <span>{language === 'te' ? 'వివరణ' : 'Explain Report'}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

interface ShortcutCardProps {
  onClick: () => void;
  icon: React.ReactNode;
  iconBg: string;
  arrow: string;
  title: string;
  desc: string;
  cta: string;
  ctaColor: string;
}

const ShortcutCard: React.FC<ShortcutCardProps> = ({ onClick, icon, iconBg, arrow, title, desc, cta, ctaColor }) => (
  <div
    onClick={onClick}
    className="p-5 bg-gradient-to-br from-slate-50 to-white rounded-2xl border border-slate-200/80 hover:border-blue-300 shadow-xs cursor-pointer group transition-all flex flex-col justify-between"
  >
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className={`w-9 h-9 rounded-xl ${iconBg} text-white flex items-center justify-center shadow-xs`}>
          {icon}
        </div>
        <ArrowRight className={`w-4 h-4 ${arrow} group-hover:translate-x-1 transition-transform`} />
      </div>
      <h3 className="text-sm font-bold text-slate-900">{title}</h3>
      <p className="text-xs text-slate-500 mt-1">{desc}</p>
    </div>
    <span className={`text-xs font-bold ${ctaColor} mt-4`}>{cta}</span>
  </div>
);
