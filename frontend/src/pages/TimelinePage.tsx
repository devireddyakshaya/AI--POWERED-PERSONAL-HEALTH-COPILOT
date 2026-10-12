import React, { useState } from 'react';
import {
  Clock,
  Search,
  Filter,
  FileText,
  Calendar,
  Trash2,
  Eye,
  AlertCircle,
  Building,
  ShieldCheck
} from 'lucide-react';
import { DocumentSummary, LanguageMode } from '../types';
import { deleteDocumentRecord } from '../services/api';

interface TimelineProps {
  documents: DocumentSummary[];
  onSelectDocument: (id: number) => void;
  onRefresh: () => void;
  language: LanguageMode;
}

export const TimelinePage: React.FC<TimelineProps> = ({
  documents,
  onSelectDocument,
  onRefresh,
  language
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const documentTypes = ['ALL', 'Laboratory Report', 'Prescription', 'Diagnostic Report', 'Discharge Summary'];

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.file_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (doc.laboratory_name && doc.laboratory_name.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = selectedType === 'ALL' || doc.document_type === selectedType;
    return matchesSearch && matchesType;
  });

  const handleDelete = async (id: number) => {
    if (!window.confirm(language === 'te' ? 'ఈ నివేదికను శాశ్వతంగా తొలగించాలా?' : 'Delete this report permanently?')) {
      return;
    }
    setDeletingId(id);
    try {
      await deleteDocumentRecord(id);
      onRefresh();
    } catch (err) {
      alert('Failed to delete document.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
            {language === 'te' ? 'ఆరోగ్య టైమ్‌లైన్' : 'Health timeline'}
          </h1>
          <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
            {language === 'te' ? 'చరిత్ర' : 'History'}
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {language === 'te'
            ? 'మీ అన్ని నివేదికలు ఒకే చోట. వెతకండి లేదా వడపోత చేయండి.'
            : 'All your reports in one place. Search or filter them.'}
        </p>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 bg-white rounded-2xl border border-slate-200/80 shadow-xs flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={language === 'te' ? 'నివేదికలను వెతకండి...' : 'Search reports...'}
            className="w-full pl-9 pr-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs outline-none focus:border-blue-400"
          />
        </div>

        {/* Category Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto no-scrollbar py-1">
          {documentTypes.map((t) => (
            <button
              key={t}
              onClick={() => setSelectedType(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                selectedType === t
                  ? 'bg-blue-700 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {t === 'ALL' ? 'All Records' : t}
            </button>
          ))}
        </div>
      </div>

      {/* Chronological Timeline Feed */}
      <div className="relative pl-6 sm:pl-8 border-l-2 border-blue-200/80 space-y-6">
        {filteredDocs.map((doc) => (
          <div key={doc.id} className="relative group">
            {/* Timeline Node Icon */}
            <div className="absolute -left-[35px] sm:-left-[43px] top-1.5 w-6 h-6 rounded-full bg-white border-2 border-blue-600 flex items-center justify-center text-blue-700 shadow-xs">
              <Calendar className="w-3 h-3" />
            </div>

            {/* Document Card */}
            <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:border-blue-300 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono font-bold text-blue-700">
                      {doc.document_date || 'Date Undefined'}
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                      {doc.document_type}
                    </span>
                    {doc.is_synthetic && (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                        Demo
                      </span>
                    )}
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 mt-1">{doc.file_name}</h3>
                  <div className="flex items-center space-x-3 text-xs text-slate-500 mt-1">
                    <span className="flex items-center space-x-1">
                      <Building className="w-3 h-3 text-slate-400" />
                      <span>{doc.laboratory_name || 'Health Diagnostic Services'}</span>
                    </span>
                    <span>•</span>
                    <span>{doc.observation_count} Tests Tracked</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2 self-end sm:self-auto">
                  <button
                    onClick={() => onSelectDocument(doc.id)}
                    className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-800 text-xs font-bold transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5 text-blue-600" />
                    <span>{language === 'te' ? 'చూడండి' : 'View'}</span>
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    disabled={deletingId === doc.id}
                    className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                    title="Permanently Delete (Privacy Vault)"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Trust Check Alert if any */}
              {doc.trust_warnings && doc.trust_warnings.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-100 text-[11px] text-amber-800 flex items-center space-x-2">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span>{doc.trust_warnings[0]}</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {filteredDocs.length === 0 && (
          <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-xs text-slate-500">
            {language === 'te' ? 'నివేదికలు కనుగొనబడలేదు.' : 'No reports found.'}
          </div>
        )}
      </div>
    </div>
  );
};
