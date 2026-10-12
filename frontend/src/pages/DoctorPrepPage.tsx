import React, { useState, useEffect } from 'react';
import {
  HelpCircle,
  Plus,
  CheckCircle2,
  Printer,
  Trash2,
  AlertCircle,
  MessageSquare,
  Sparkles
} from 'lucide-react';
import { DoctorQuestion, LanguageMode } from '../types';
import {
  fetchDoctorQuestions,
  addDoctorQuestion,
  toggleDoctorQuestionCheck,
  deleteDoctorQuestion
} from '../services/api';

interface DoctorPrepProps {
  language: LanguageMode;
  patientId?: number | null;
}

export const DoctorPrepPage: React.FC<DoctorPrepProps> = ({ language, patientId = null }) => {
  const [questions, setQuestions] = useState<DoctorQuestion[]>([]);
  const [newQuestionText, setNewQuestionText] = useState('');
  const [category, setCategory] = useState('Personal Question');
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    loadQuestions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patientId]);

  const loadQuestions = async () => {
    setIsLoading(true);
    setLoadError(false);
    try {
      const qList = await fetchDoctorQuestions(patientId);
      setQuestions(qList);
    } catch (err) {
      console.error(err);
      setQuestions([]);
      setLoadError(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuestionText.trim()) return;

    try {
      const created = await addDoctorQuestion(newQuestionText.trim(), category, patientId);
      setQuestions([created, ...questions]);
      setNewQuestionText('');
    } catch (err) {
      alert('Failed to add question.');
    }
  };

  const handleToggle = async (id: number, currentStatus: boolean) => {
    try {
      await toggleDoctorQuestionCheck(id, !currentStatus);
      setQuestions(questions.map(q => (q.id === id ? { ...q, is_checked: !currentStatus } : q)));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteDoctorQuestion(id);
      setQuestions(questions.filter(q => q.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
              {language === 'te' ? 'డాక్టర్ ప్రశ్నలు' : 'Doctor questions'}
            </h1>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200">
              {language === 'te' ? 'సన్నద్ధత' : 'Prep'}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {language === 'te'
              ? 'మీ వైద్యుడిని అడగవలసిన ప్రశ్నల జాబితా.'
              : 'A checklist of questions to ask your doctor.'}
          </p>
        </div>

        <button
          onClick={handlePrint}
          className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
        >
          <Printer className="w-4 h-4 text-slate-600" />
          <span>{language === 'te' ? 'ప్రింట్' : 'Print'}</span>
        </button>
      </div>

      {/* Add Custom Question Form */}
      <form onSubmit={handleAddQuestion} className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs space-y-3">
        <span className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
          <MessageSquare className="w-4 h-4 text-blue-600" />
          <span>{language === 'te' ? 'మీ స్వంత ప్రశ్న జోడించండి' : 'Add your own question'}</span>
        </span>

        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={newQuestionText}
            onChange={(e) => setNewQuestionText(e.target.value)}
            placeholder={language === 'te' ? 'మీ ప్రశ్న ఇక్కడ టైప్ చేయండి...' : 'Type your question here...'}
            className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs outline-none focus:border-blue-400"
          />

          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 outline-none"
          >
            <option value="Abnormal Lab Follow-up">Abnormal Lab Follow-up</option>
            <option value="Medication Clarification">Medication Clarification</option>
            <option value="Personal Question">Personal Question</option>
            <option value="Preventive Care">Preventive Care</option>
          </select>

          <button
            type="submit"
            className="flex items-center justify-center space-x-1 px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-xs font-bold transition-colors shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>Add Question</span>
          </button>
        </div>
      </form>

      {/* Checklist Grid */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">{language === 'te' ? 'మీ చెక్‌లిస్ట్' : 'Your checklist'}</h3>
          <span className="text-xs text-slate-500 font-medium">
            {questions.filter(q => q.is_checked).length} / {questions.length} {language === 'te' ? 'పూర్తయ్యాయి' : 'done'}
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {questions.map((q) => (
            <div
              key={q.id}
              className={`p-4 sm:p-5 flex items-start justify-between gap-4 transition-colors ${
                q.is_checked ? 'bg-slate-50/70' : 'hover:bg-slate-50/50'
              }`}
            >
              <div className="flex items-start space-x-3.5 flex-1">
                <input
                  type="checkbox"
                  checked={q.is_checked}
                  onChange={() => handleToggle(q.id, q.is_checked)}
                  className="mt-1 w-4 h-4 rounded text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
                <div>
                  <span className={`text-xs sm:text-sm font-semibold leading-relaxed block ${
                    q.is_checked ? 'line-through text-slate-400' : 'text-slate-800'
                  }`}>
                    {q.question_text}
                  </span>
                  <div className="flex items-center space-x-2 mt-1.5 text-[11px] text-slate-500">
                    <span className="font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                      {q.category}
                    </span>
                    {q.context_note && <span>• {q.context_note}</span>}
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleDelete(q.id)}
                className="text-slate-300 hover:text-rose-500 p-1 rounded-lg transition-colors"
                title="Remove Question"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}

          {questions.length === 0 && (
            <div className="p-10 text-center text-xs text-slate-500">
              {isLoading
                ? language === 'te' ? 'లోడ్ అవుతోంది...' : 'Loading...'
                : loadError
                ? language === 'te'
                  ? 'ప్రశ్నలను లోడ్ చేయలేకపోయాం. సర్వర్ అందుబాటులో ఉందో చూడండి.'
                  : 'Could not load questions. Please check the server connection.'
                : language === 'te'
                ? 'ఇంకా ప్రశ్నలు లేవు. నివేదిక అప్‌లోడ్ చేయండి లేదా మీ స్వంత ప్రశ్న జోడించండి.'
                : 'No questions yet. Upload a report or add your own question above.'}
            </div>
          )}
        </div>
      </div>

      {/* Safety Notice */}
      <div className="p-4 bg-slate-100 rounded-2xl border border-slate-200 text-slate-600 text-xs flex items-center space-x-2.5">
        <AlertCircle className="w-4 h-4 text-slate-500 shrink-0" />
        <p>
          {language === 'te'
            ? 'గమనిక: ఇవి మీ వైద్యుడితో చర్చించడానికి సహాయక ప్రశ్నలు మాత్రమే. ఇవి వైద్య సలహాలు కావు.'
            : 'Note: These are helpful talking points only. They are not medical advice.'}
        </p>
      </div>
    </div>
  );
};
