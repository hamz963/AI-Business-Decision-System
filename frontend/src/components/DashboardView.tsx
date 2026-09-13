import React from 'react';
import { 
  TrendingUp, TrendingDown, DollarSign, Percent, ShoppingBag, 
  Users, AlertCircle, ArrowUpRight, Sparkles, CheckCircle2, ShieldAlert
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar, CartesianGrid } from 'recharts';
import { ExecutiveDashboardData } from '../types';

interface DashboardViewProps {
  data: ExecutiveDashboardData;
  onNavigate: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ data, onNavigate }) => {
  const { metrics, briefing, monthly_trend, category_breakdown } = data;

  const kpis = [
    {
      title: 'Total Revenue',
      value: `$${metrics.revenue.toLocaleString()}`,
      change: '+6.4%',
      isPositive: true,
      subtext: 'vs. previous cycle',
      icon: DollarSign,
      color: 'text-sky-400',
      bg: 'bg-sky-500/10'
    },
    {
      title: 'Gross Margin',
      value: `${metrics.gross_margin_pct.toFixed(1)}%`,
      change: '+80 bps',
      isPositive: true,
      subtext: `$${metrics.gross_profit.toLocaleString()} Gross Profit`,
      icon: Percent,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10'
    },
    {
      title: 'Net Operating Profit',
      value: `$${metrics.net_profit.toLocaleString()}`,
      change: '+9.8%',
      isPositive: true,
      subtext: `${metrics.net_margin_pct.toFixed(1)}% Net Margin`,
      icon: TrendingUp,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10'
    },
    {
      title: 'Average Order Value (AOV)',
      value: `$${metrics.average_order_value.toFixed(2)}`,
      change: '+2.1%',
      isPositive: true,
      subtext: `${metrics.orders.toLocaleString()} total orders`,
      icon: ShoppingBag,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10'
    }
  ];

  return (
    <div className="space-y-6">
      {/* AI Business Briefing Card */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-sky-950/40 border border-sky-500/20 rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-sky-500/5 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="p-1.5 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white tracking-tight">AI Executive Intelligence Briefing</h2>
              <p className="text-xs text-slate-400">{briefing.generated_at}</p>
            </div>
          </div>
          <span className="px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{briefing.confidence}</span>
          </span>
        </div>

        <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Summary & Core Drivers */}
          <div className="lg:col-span-2 space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200 mb-1">{briefing.headline}</h3>
              <p className="text-xs text-slate-300 leading-relaxed">{briefing.summary}</p>
            </div>

            <div className="space-y-2">
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Key Performance Drivers</span>
              <ul className="space-y-1.5">
                {briefing.key_drivers.map((driver, idx) => (
                  <li key={idx} className="flex items-start space-x-2 text-xs text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-sky-400 mt-1.5 flex-shrink-0"></span>
                    <span>{driver}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Strategic Recommendations Box */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-mono uppercase tracking-wider text-sky-400 font-semibold">
                  Prescriptive Action
                </span>
                <span className="text-[10px] font-mono text-slate-400">MCDA Scored</span>
              </div>
              {briefing.strategic_recommendations.slice(0, 1).map((rec, i) => (
                <div key={i} className="space-y-2">
                  <div className="text-xs font-semibold text-white">{rec.initiative}</div>
                  <div className="text-[11px] text-emerald-400 font-mono">Impact: {rec.impact}</div>
                  <div className="text-[11px] text-slate-400">Risk: {rec.risk} • {rec.timeframe}</div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800 flex space-x-2">
              <button
                onClick={() => onNavigate('scenarios')}
                className="flex-1 py-1.5 px-3 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold text-xs flex items-center justify-center space-x-1 transition shadow-sm"
              >
                <span>Simulate Impact</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => onNavigate('decisions')}
                className="py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition"
              >
                Review Matrix
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-slate-400">{kpi.title}</span>
                <div className={`p-2 rounded-lg ${kpi.bg}`}>
                  <Icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">{kpi.value}</div>
              <div className="mt-2 flex items-center space-x-2 text-xs">
                <span className={`font-mono font-medium ${kpi.isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {kpi.change}
                </span>
                <span className="text-slate-400">{kpi.subtext}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Analytical Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue & Margin Velocity Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Trailing Revenue & Profit Trajectory</h3>
              <p className="text-xs text-slate-400">Monthly realized ledger vs cost profile</p>
            </div>
            <div className="flex items-center space-x-4 text-xs font-mono">
              <span className="flex items-center space-x-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-sm bg-sky-500"></span>
                <span>Revenue</span>
              </span>
              <span className="flex items-center space-x-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span>
                <span>Gross Profit</span>
              </span>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthly_trend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284c7" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `$${val/1000}k`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(value: any) => [`$${Number(value).toLocaleString()}`, '']}
                />
                <Area type="monotone" dataKey="revenue" stroke="#0284c7" strokeWidth={2} fillOpacity={1} fill="url(#colorRev)" name="Revenue" />
                <Area type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorProfit)" name="Gross Profit" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Contribution Breakdown */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Category Distribution</h3>
              <p className="text-xs text-slate-400">Share of recognized gross revenue</p>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={category_breakdown} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" fontSize={10} tickFormatter={(v) => `$${v/1000}k`} />
                <YAxis type="category" dataKey="category" stroke="#64748b" fontSize={10} width={100} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Revenue']}
                />
                <Bar dataKey="revenue" fill="#38bdf8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
