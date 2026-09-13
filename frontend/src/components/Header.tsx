import React from 'react';
import { Building2, FileDown, Search, Bell } from 'lucide-react';
import { reportsApi } from '../services/api';

interface HeaderProps {
  currentTab: string;
  datasetName?: string;
}

export const Header: React.FC<HeaderProps> = ({ currentTab, datasetName }) => {
  const getTitle = () => {
    switch (currentTab) {
      case 'dashboard': return 'Executive Briefing & Strategic Cockpit';
      case 'datasets': return 'Data Quality Engine & Ingestion Pipeline';
      case 'scenarios': return 'Scenario Simulator & What-If Studio';
      case 'decisions': return 'Decision Matrix & Governance Hub';
      case 'ai-analyst': return 'Grounded AI Business Analyst';
      case 'forecasting': return 'Predictive Forecaster & Anomaly Sentry';
      default: return 'Business Decision Support System';
    }
  };

  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-8 flex-shrink-0">
      <div className="flex items-center space-x-4">
        <div>
          <h1 className="text-base font-semibold text-white tracking-tight">{getTitle()}</h1>
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <span className="flex items-center space-x-1">
              <Building2 className="w-3.5 h-3.5 text-sky-400" />
              <span>Acme Global Enterprise</span>
            </span>
            <span>•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              Active: <span className="text-sky-400">{datasetName || 'Synthetic Enterprise Baseline'}</span>
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Quick Export Button */}
        <button
          onClick={reportsApi.downloadMarkdown}
          className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-medium border border-slate-700 hover:border-slate-600 transition shadow-sm"
          title="Download Executive Markdown Report"
        >
          <FileDown className="w-3.5 h-3.5 text-sky-400" />
          <span>Export Briefing</span>
        </button>

        {/* User Pill */}
        <div className="flex items-center space-x-2 pl-3 border-l border-slate-800">
          <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow">
            AD
          </div>
          <div className="text-xs">
            <div className="font-medium text-slate-200">Alex Drake</div>
            <div className="text-[10px] text-slate-400">Chief Strategist</div>
          </div>
        </div>
      </div>
    </header>
  );
};
