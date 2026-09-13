import React from 'react';
import { 
  LayoutDashboard, Database, Sliders, CheckSquare, 
  Bot, LineChart, ShieldAlert, FileText, Settings
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Executive Briefing', icon: LayoutDashboard },
    { id: 'datasets', label: 'Data & Quality Engine', icon: Database },
    { id: 'scenarios', label: 'Scenario Simulator', icon: Sliders },
    { id: 'decisions', label: 'Decision Intelligence', icon: CheckSquare },
    { id: 'ai-analyst', label: 'Grounded AI Analyst', icon: Bot },
    { id: 'forecasting', label: 'Forecasts & Anomalies', icon: LineChart },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col flex-shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 space-x-3">
        <div className="w-8 h-8 rounded-lg bg-sky-500 flex items-center justify-center text-slate-950 font-bold text-lg shadow-lg shadow-sky-500/20">
          AI
        </div>
        <div>
          <span className="font-bold tracking-tight text-white block text-sm">AI-BDSS</span>
          <span className="text-[10px] text-sky-400 font-mono tracking-wider uppercase">Decision Intelligence</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2 font-mono">
          Core Workspaces
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Bottom Status / Mode */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="font-mono text-[11px]">Grounding Engine</span>
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-sky-300">
            v1.0-PROD
          </span>
        </div>
      </div>
    </aside>
  );
};
