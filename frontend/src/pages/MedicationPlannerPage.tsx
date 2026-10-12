import React, { useState, useEffect } from 'react';
import {
  Pill,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Bell,
  BellOff,
  Edit2,
  Check,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { Medication, LanguageMode } from '../types';
import { fetchMedicationAgenda, updateMedicationSchedule } from '../services/api';

interface MedicationPlannerProps {
  language: LanguageMode;
  patientId?: number | null;
}

export const MedicationPlannerPage: React.FC<MedicationPlannerProps> = ({ language, patientId = null }) => {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [dailySchedule, setDailySchedule] = useState<any[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTime, setEditTime] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    loadMeds();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patientId]);

  const loadMeds = async () => {
    setIsLoading(true);
    setLoadError(false);
    try {
      const data = await fetchMedicationAgenda(patientId);
      setMedications(data.medications || []);
      setDailySchedule(data.daily_schedule || []);
    } catch (err) {
      console.error(err);
      setMedications([]);
      setDailySchedule([]);
      setLoadError(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleReminder = async (id: number, currentActive: boolean, isVerified: boolean) => {
    if (!currentActive && !isVerified) {
      const confirmVerify = window.confirm(
        language === 'te'
          ? 'దయచేసి డోస్ మరియు సమయం మీ ప్రిస్క్రిప్షన్‌తో సరిపోతుందో నిర్ధారించండి.'
          : 'Please confirm the dose and time match your prescription.'
      );
      if (!confirmVerify) return;
    }

    try {
      await updateMedicationSchedule(id, {
        is_reminder_active: !currentActive,
        is_verified: true
      });
      // Refresh local state
      setMedications(medications.map(m => m.id === id ? { ...m, is_reminder_active: !currentActive, is_verified: true } : m));
    } catch (err) {
      alert('Failed to update reminder.');
    }
  };

  const handleSaveTime = async (id: number) => {
    if (!editTime.trim()) return;
    try {
      await updateMedicationSchedule(id, { schedule_time: editTime.trim(), is_verified: true });
      setMedications(medications.map(m => m.id === id ? { ...m, schedule_time: editTime.trim(), is_verified: true } : m));
      setEditingId(null);
      setEditTime('');
    } catch (err) {
      alert('Failed to save schedule time.');
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
            {language === 'te' ? 'మందుల రిమైండర్లు' : 'Medicine reminders'}
          </h1>
          <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-800 border border-cyan-200">
            {language === 'te' ? 'రిమైండర్లు' : 'Reminders'}
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {language === 'te'
            ? 'మీ ప్రిస్క్రిప్షన్‌ను సులభమైన రోజువారీ రిమైండర్లుగా మార్చండి.'
            : 'Turn your prescription into simple daily reminders.'}
        </p>
      </div>

      {/* Trust Notice for Incomplete Instructions */}
      {medications.some(m => m.is_incomplete) && (
        <div className="p-4 bg-amber-50 rounded-2xl border border-amber-200 text-amber-900 text-xs flex items-start space-x-3">
          <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold text-amber-950">{language === 'te' ? 'స్పష్టంగా లేని మందుల సూచనలు' : 'Some instructions are incomplete'}</h4>
            <p className="mt-0.5 leading-relaxed text-amber-800">
              {language === 'te'
                ? 'కొన్ని మందులకు డోస్ లేదా వ్యవధి లేదు. దయచేసి వైద్యుడిని లేదా ఫార్మసిస్ట్‌ను సంప్రదించండి.'
                : 'Some medicines are missing the dose or duration. Please check with your doctor or pharmacist.'}
            </p>
          </div>
        </div>
      )}

      {/* Prescriptions Review & Verification Table */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">{language === 'te' ? 'మీ మందులు' : 'Your medicines'}</h3>
          <span className="text-xs text-slate-500 font-medium">
            {medications.filter(m => m.is_reminder_active).length} {language === 'te' ? 'రిమైండర్లు ఆన్' : 'active'}
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {medications.map((med) => (
            <div key={med.id} className="p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:bg-slate-50/60 transition-colors">
              <div className="flex items-start space-x-3.5">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                  med.is_incomplete ? 'bg-amber-100 text-amber-700' : 'bg-blue-50 text-blue-700'
                }`}>
                  <Pill className="w-5 h-5" />
                </div>

                <div>
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-bold text-slate-900">{med.medicine_name}</h4>
                    <span className="text-xs font-mono font-bold text-slate-600">
                      {med.dosage || 'Dosage Unspecified'}
                    </span>
                    {med.is_incomplete ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                        Needs Verification
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800">
                        Verified
                      </span>
                    )}
                  </div>

                  <div className="text-xs text-slate-500 mt-1 flex flex-wrap gap-x-3 gap-y-1">
                    <span>Frequency: <strong className="text-slate-700">{med.frequency || 'Daily'}</strong></span>
                    <span>•</span>
                    <span>Timing: <strong className="text-slate-700">{med.timing_instructions || 'As advised'}</strong></span>
                    <span>•</span>
                    <span>Duration: <strong className="text-slate-700">{med.duration || 'Ongoing'}</strong></span>
                  </div>

                  {med.trust_warning && (
                    <p className="text-[11px] text-amber-700 font-medium mt-1">
                      ⚠️ {med.trust_warning}
                    </p>
                  )}
                </div>
              </div>

              {/* Reminder Controls */}
              <div className="flex items-center space-x-3 self-end md:self-auto">
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 block font-medium">{language === 'te' ? 'రిమైండర్ సమయం' : 'Reminder time'}</span>
                  {editingId === med.id ? (
                    <div className="flex items-center space-x-1 mt-0.5">
                      <input
                        type="text"
                        value={editTime}
                        onChange={(e) => setEditTime(e.target.value)}
                        placeholder="08:30 PM"
                        className="w-20 px-1.5 py-0.5 text-xs border border-blue-400 rounded outline-none"
                      />
                      <button onClick={() => handleSaveTime(med.id)} className="p-1 rounded bg-blue-600 text-white">
                        <Check className="w-3 h-3" />
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-1">
                      <span className="text-xs font-mono font-bold text-slate-800">{med.schedule_time}</span>
                      <button
                        onClick={() => { setEditingId(med.id); setEditTime(med.schedule_time); }}
                        className="text-slate-400 hover:text-blue-700 p-0.5"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleToggleReminder(med.id, med.is_reminder_active, med.is_verified)}
                  className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all shadow-xs ${
                    med.is_reminder_active
                      ? 'bg-blue-700 hover:bg-blue-800 text-white'
                      : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                  }`}
                >
                  {med.is_reminder_active ? (
                    <>
                      <Bell className="w-3.5 h-3.5" />
                      <span>{language === 'te' ? 'రిమైండర్ ఆన్' : 'Reminder on'}</span>
                    </>
                  ) : (
                    <>
                      <BellOff className="w-3.5 h-3.5" />
                      <span>{language === 'te' ? 'రిమైండర్ పెట్టండి' : 'Set reminder'}</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}

          {medications.length === 0 && (
            <div className="p-10 text-center text-xs text-slate-500">
              {isLoading
                ? language === 'te' ? 'లోడ్ అవుతోంది...' : 'Loading...'
                : loadError
                ? language === 'te'
                  ? 'మందులను లోడ్ చేయలేకపోయాం. సర్వర్ అందుబాటులో ఉందో చూడండి.'
                  : 'Could not load medicines. Please check the server connection.'
                : language === 'te'
                ? 'ఇంకా మందులు లేవు. ప్రిస్క్రిప్షన్ ఉన్న నివేదికను అప్‌లోడ్ చేయండి.'
                : 'No medicines yet. Upload a report that contains a prescription.'}
            </div>
          )}
        </div>
      </div>

      {/* Daily Chronological Schedule Agenda */}
      <div className="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
          <Clock className="w-4 h-4 text-blue-600" />
          <span>{language === 'te' ? 'రోజువారీ షెడ్యూల్' : 'Daily schedule'}</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {dailySchedule.map((slot, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-blue-800 text-sm">{slot.time}</span>
                {slot.is_active ? (
                  <span className="text-[10px] font-bold text-blue-700 flex items-center space-x-1">
                    <Bell className="w-3 h-3" />
                    <span>Active</span>
                  </span>
                ) : (
                  <span className="text-[10px] text-slate-400">Off</span>
                )}
              </div>
              <h4 className="text-xs font-bold text-slate-800">{slot.medicine_name} ({slot.dosage})</h4>
              <p className="text-[11px] text-slate-500">{slot.instructions}</p>
            </div>
          ))}

          {dailySchedule.length === 0 && (
            <div className="md:col-span-3 p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
              {language === 'te'
                ? 'రోజువారీ షెడ్యూల్ ఇంకా లేదు.'
                : 'No daily schedule yet.'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
