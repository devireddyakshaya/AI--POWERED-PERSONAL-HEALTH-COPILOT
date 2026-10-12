import React, { useState, useEffect } from 'react';
import {
  GitCompare,
  TrendingDown,
  TrendingUp,
  Minus,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Layers,
  ArrowRight
} from 'lucide-react';
import { DocumentDetail, ReportComparison, LanguageMode } from '../types';
import { fetchReportComparison } from '../services/api';
import { TrendChart } from '../components/TrendChart';

interface ComparisonProps {
  documents: DocumentDetail[];
  language: LanguageMode;
}

export const ComparisonPage: React.FC<ComparisonProps> = ({ documents, language }) => {
  const [reportAId, setReportAId] = useState<number>(documents[0]?.id || 1);
  const [reportBId, setReportBId] = useState<number>(documents[1]?.id || documents[0]?.id || 2);
  const [comparison, setComparison] = useState<ReportComparison | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (documents.length >= 2) {
      // Pick oldest as A and newest as B
      setReportAId(documents[0].id);
      setReportBId(documents[1].id);
      loadComparison(documents[0].id, documents[1].id);
    } else if (documents.length === 1) {
      setReportAId(documents[0].id);
      setReportBId(documents[0].id);
    }
  }, [documents]);

  const loadComparison = async (idA: number, idB: number) => {
    setIsLoading(true);
    try {
      const res = await fetchReportComparison(idA, idB);
      setComparison(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompareClick = () => {
    loadComparison(reportAId, reportBId);
  };

  return (
    <div className="space-y-8 py-4">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
            {language === 'te' ? 'నివేదికల పోలిక' : 'Compare reports'}
          </h1>
          <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
            {language === 'te' ? 'మార్పులు' : 'Trends'}
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {language === 'te'
            ? 'రెండు నివేదికలను పోల్చి ఏది పెరిగింది, తగ్గింది లేదా మారలేదు చూడండి.'
            : 'Compare two reports. See what went up, down, or stayed the same.'}
        </p>
      </div>

      {/* Select Two Reports Bar */}
      <div className="p-5 bg-white rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        <div className="flex-1 space-y-1">
          <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            {language === 'te' ? 'పాత నివేదిక' : 'Older report'}
          </label>
          <select
            value={reportAId}
            onChange={(e) => setReportAId(Number(e.target.value))}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 outline-none"
          >
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.file_name} ({d.document_date})
              </option>
            ))}
          </select>
        </div>

        <div className="self-center hidden md:block text-slate-400">
          <ArrowRight className="w-5 h-5" />
        </div>

        <div className="flex-1 space-y-1">
          <label className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block">
            {language === 'te' ? 'కొత్త నివేదిక' : 'Newer report'}
          </label>
          <select
            value={reportBId}
            onChange={(e) => setReportBId(Number(e.target.value))}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 outline-none"
          >
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.file_name} ({d.document_date})
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleCompareClick}
          className="self-end md:self-auto px-5 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-xl text-xs font-bold shadow-sm transition-colors mt-2 md:mt-0"
        >
          {language === 'te' ? 'పోల్చండి' : 'Compare'}
        </button>
      </div>

      {/* Comparison Results */}
      {comparison && (
        <div className="space-y-6">
          {/* Trend Chart */}
          <div className="p-6 bg-white rounded-2xl border border-slate-200/80 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <GitCompare className="w-4 h-4 text-blue-600" />
              <span>{language === 'te' ? 'విలువల మార్పులు' : 'Value trends'}</span>
            </h3>
            <TrendChart
              items={comparison.matched_tests}
              dateA={comparison.report_a_date}
              dateB={comparison.report_b_date}
            />
          </div>

          {/* Matched Tests Table */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">{language === 'te' ? 'పోల్చిన ఫలితాలు' : 'Compared results'}</h3>
              <span className="text-xs text-blue-700 font-bold">
                {comparison.matched_tests.length} {language === 'te' ? 'పరీక్షలు పోల్చబడ్డాయి' : 'tests compared'}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-100 font-semibold">
                  <tr>
                    <th className="p-3.5 pl-5">{language === 'te' ? 'పరీక్ష' : 'Test'}</th>
                    <th className="p-3.5">{language === 'te' ? 'ముందు' : 'Prior'} ({comparison.report_a_date})</th>
                    <th className="p-3.5">{language === 'te' ? 'ఇప్పుడు' : 'Recent'} ({comparison.report_b_date})</th>
                    <th className="p-3.5">{language === 'te' ? 'మార్పు' : 'Change'}</th>
                    <th className="p-3.5">{language === 'te' ? 'సాధారణ పరిధి' : 'Normal range'}</th>
                    <th className="p-3.5">{language === 'te' ? 'స్థితి' : 'Status'}</th>
                    <th className="p-3.5 pr-5">{language === 'te' ? 'గమనిక' : 'Note'}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {comparison.matched_tests.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/70">
                      <td className="p-3.5 pl-5 font-bold text-slate-800">{item.test_name}</td>
                      <td className="p-3.5 font-mono text-slate-600">{item.report_a_value} {item.unit}</td>
                      <td className="p-3.5 font-mono text-blue-900 font-bold">{item.report_b_value} {item.unit}</td>
                      <td className="p-3.5 font-mono font-semibold">
                        <span className={`inline-flex items-center space-x-1 ${
                          item.trend_direction === 'DECREASED' ? 'text-blue-700' : 'text-slate-700'
                        }`}>
                          {item.trend_direction === 'DECREASED' && <TrendingDown className="w-3.5 h-3.5" />}
                          {item.trend_direction === 'INCREASED' && <TrendingUp className="w-3.5 h-3.5" />}
                          {item.trend_direction === 'STABLE' && <Minus className="w-3.5 h-3.5" />}
                          <span>{item.absolute_change > 0 ? `+${item.absolute_change}` : item.absolute_change} {item.unit}</span>
                        </span>
                      </td>
                      <td className="p-3.5 text-slate-500 font-mono text-[11px]">{item.reference_range_text}</td>
                      <td className="p-3.5">
                        <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          item.range_shift_status === 'WITHIN_NORMAL'
                            ? 'bg-emerald-100 text-emerald-800'
                            : item.range_shift_status === 'CLOSER_TO_NORMAL'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}>
                          {item.range_shift_status.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="p-3.5 pr-5 text-slate-600 max-w-xs">{item.clinical_note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Safety Disclaimer */}
          <div className="p-4 bg-amber-50 rounded-2xl border border-amber-200 text-amber-900 text-xs flex items-start space-x-2.5">
            <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <p className="leading-relaxed">{comparison.disclaimer}</p>
          </div>
        </div>
      )}
    </div>
  );
};
