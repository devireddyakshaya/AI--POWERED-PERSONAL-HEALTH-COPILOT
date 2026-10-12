import React from 'react';
import { ComparisonItem } from '../types';

interface TrendChartProps {
  items: ComparisonItem[];
  dateA: string;
  dateB: string;
}

export const TrendChart: React.FC<TrendChartProps> = ({ items, dateA, dateB }) => {
  if (!items || items.length === 0) {
    return <div className="p-6 text-center text-xs text-slate-500">No tests to compare.</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-xs text-slate-500 px-1">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-slate-400 inline-block" />
            <span className="font-semibold text-slate-700">Older ({dateA})</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-blue-600 inline-block" />
            <span className="font-semibold text-blue-800">Newer ({dateB})</span>
          </span>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">Trend</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((item, idx) => {
          const maxVal = Math.max(item.report_a_value, item.report_b_value, 1) * 1.25;
          const pctA = Math.min(100, Math.max(10, (item.report_a_value / maxVal) * 100));
          const pctB = Math.min(100, Math.max(10, (item.report_b_value / maxVal) * 100));

          return (
            <div key={idx} className="p-4 bg-white rounded-xl border border-slate-200/90 shadow-xs hover:border-blue-200 transition-all">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-800">{item.test_name}</span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                  Normal: {item.reference_range_text}
                </span>
              </div>

              {/* Bar Comparison */}
              <div className="space-y-2 text-xs">
                <div>
                  <div className="flex justify-between text-[11px] mb-0.5 text-slate-500">
                    <span>Older: {dateA}</span>
                    <span className="font-semibold text-slate-700">{item.report_a_value} {item.unit}</span>
                  </div>
                  <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-slate-400 rounded-full transition-all duration-500"
                      style={{ width: `${pctA}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-0.5 text-blue-700">
                    <span>Newer: {dateB}</span>
                    <span className="font-extrabold text-blue-900">{item.report_b_value} {item.unit}</span>
                  </div>
                  <div className="h-2.5 bg-blue-50 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 rounded-full transition-all duration-500"
                      style={{ width: `${pctB}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Status footer */}
              <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
                <span className={`font-semibold ${
                  item.range_shift_status === 'WITHIN_NORMAL'
                    ? 'text-emerald-700'
                    : item.range_shift_status === 'CLOSER_TO_NORMAL'
                    ? 'text-blue-700'
                    : 'text-amber-700'
                }`}>
                  {item.range_shift_status === 'WITHIN_NORMAL'
                    ? 'Normal'
                    : item.range_shift_status === 'CLOSER_TO_NORMAL'
                    ? 'Improving'
                    : 'Needs attention'}
                </span>
                <span className="font-mono text-slate-600">
                  Δ {item.absolute_change > 0 ? `+${item.absolute_change}` : item.absolute_change} {item.unit} ({item.percentage_change}%)
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
