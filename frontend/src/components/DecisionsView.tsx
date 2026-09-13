import React, { useState } from 'react';
import { 
  CheckSquare, ShieldAlert, Award, ArrowRight, CheckCircle2, 
  XCircle, Clock, AlertCircle, Sparkles, MessageSquare
} from 'lucide-react';
import { decisionsApi } from '../services/api';
import { Decision } from '../types';

interface DecisionsViewProps {
  decisions: Decision[];
  onRefresh: () => void;
}

export const DecisionsView: React.FC<DecisionsViewProps> = ({ decisions, onRefresh }) => {
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(decisions[0] || null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [acting, setActing] = useState(false);

  const activeDecision = selectedDecision || decisions[0];

  const handleAction = async (status: 'approved' | 'rejected' | 'implemented') => {
    if (!activeDecision) return;
    setActing(true);
    try {
      await decisionsApi.review(activeDecision.id, status, reviewNotes);
      setReviewNotes('');
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setActing(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">APPROVED</span>;
      case 'rejected':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20 font-semibold">REJECTED</span>;
      case 'implemented':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-500/10 text-sky-400 border border-sky-500/20 font-semibold">IMPLEMENTED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20 font-semibold">PROPOSED</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center space-x-2">
            <CheckSquare className="w-4 h-4 text-sky-400" />
            <span>Decision Intelligence & Human Governance Hub</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit multi-attribute scored alternatives, inspect underlying evidence, and exercise human-in-the-loop sign-off.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-400 font-mono">
          <span>Active Proposals: {decisions.length}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Proposals List (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          {decisions.map((dec) => {
            const isSelected = activeDecision?.id === dec.id;
            return (
              <div
                key={dec.id}
                onClick={() => setSelectedDecision(dec)}
                className={`p-4 rounded-xl border cursor-pointer transition text-left ${
                  isSelected
                    ? 'bg-slate-900 border-sky-500/40 shadow-lg'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-sky-400 font-semibold">
                    {dec.category}
                  </span>
                  {getStatusBadge(dec.status)}
                </div>
                <h3 className="text-xs font-semibold text-white mb-1.5 leading-snug">{dec.title}</h3>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-3">
                  {dec.description}
                </p>
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-slate-800/60">
                  <span>Confidence: {(dec.confidence_score * 100).toFixed(0)}%</span>
                  <span className="uppercase text-amber-400">Risk: {dec.risk_level}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Detailed Decision Breakdown & Governance Action (8 cols) */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          {activeDecision ? (
            <>
              {/* Proposal Banner */}
              <div className="flex items-start justify-between pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-sky-400 font-semibold">
                      {activeDecision.category} Strategy
                    </span>
                    <span>•</span>
                    {getStatusBadge(activeDecision.status)}
                  </div>
                  <h2 className="text-base font-bold text-white tracking-tight">{activeDecision.title}</h2>
                  <p className="text-xs text-slate-300 mt-1">{activeDecision.description}</p>
                </div>
              </div>

              {/* Rationale & Grounded Evidence */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 space-y-2">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
                    Analytical Rationale
                  </span>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {activeDecision.rationale}
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 space-y-2">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
                    Cited Evidence & KPIs
                  </span>
                  <div className="space-y-1.5">
                    {activeDecision.evidence.map((ev, i) => (
                      <div key={i} className="flex items-center justify-between text-xs font-mono">
                        <span className="text-slate-400">{ev.metric}:</span>
                        <span className="text-sky-400 font-semibold">{ev.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Multi-Criteria Options Matrix */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
                    Evaluated Alternatives (MCDA Scored)
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    Weights: Profit (35%) • Risk (25%) • Growth (20%) • Feasibility (20%)
                  </span>
                </div>

                <div className="overflow-x-auto border border-slate-800 rounded-lg">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-[11px]">
                      <tr>
                        <th className="p-3">Option</th>
                        <th className="p-3 text-right">Profit Score</th>
                        <th className="p-3 text-right">Risk (Lower=Better)</th>
                        <th className="p-3 text-right">Feasibility</th>
                        <th className="p-3 text-right text-sky-400">Composite Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {activeDecision.options_matrix?.map((opt, idx) => {
                        const isRecommended = opt.name === activeDecision.recommended_option;
                        return (
                          <tr key={idx} className={isRecommended ? 'bg-sky-500/5' : 'hover:bg-slate-800/30'}>
                            <td className="p-3 text-slate-200">
                              <div className="flex items-center space-x-1.5">
                                {isRecommended && <Award className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />}
                                <span className={isRecommended ? 'font-semibold text-white' : ''}>{opt.name}</span>
                              </div>
                              <div className="text-[10px] text-slate-400 mt-0.5 font-sans">{opt.description}</div>
                            </td>
                            <td className="p-3 text-right text-slate-300">{opt.expected_profit}</td>
                            <td className="p-3 text-right text-amber-400">{opt.risk_score}</td>
                            <td className="p-3 text-right text-slate-300">{opt.feasibility}</td>
                            <td className="p-3 text-right text-sky-400 font-bold text-sm">{opt.net_score}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Stated Assumptions & Impact */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800 space-y-1.5">
                  <span className="text-[11px] font-mono text-slate-400 font-semibold block">Explicit Model Assumptions</span>
                  {activeDecision.assumptions.map((assump, i) => (
                    <div key={i} className="text-slate-300 flex items-start space-x-1.5">
                      <span className="text-sky-400 mt-0.5">•</span>
                      <span>{assump}</span>
                    </div>
                  ))}
                </div>

                <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800 space-y-1 font-mono">
                  <span className="text-[11px] font-mono text-slate-400 font-semibold block">Expected Business Impact</span>
                  <div className="text-slate-300">Revenue Range: <span className="text-emerald-400">{activeDecision.expected_impact.revenue_impact_range}</span></div>
                  <div className="text-slate-300">Profit Impact: <span className="text-emerald-400">{activeDecision.expected_impact.profit_impact_range}</span></div>
                  <div className="text-slate-400 text-[11px]">Time to Value: {activeDecision.expected_impact.time_to_value}</div>
                </div>
              </div>

              {/* Human-In-The-Loop Governance Actions */}
              <div className="p-4 rounded-xl bg-slate-950 border border-sky-500/20 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-white flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-400" />
                    <span>Executive Sign-Off & Governance Audit</span>
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">Two-man rule enforced</span>
                </div>

                <input
                  type="text"
                  placeholder="Optional review notes or condition of approval..."
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-sky-500"
                />

                <div className="flex items-center space-x-3 pt-1">
                  <button
                    disabled={acting || activeDecision.status === 'approved'}
                    onClick={() => handleAction('approved')}
                    className="flex-1 py-2 px-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-semibold text-xs transition shadow-sm flex items-center justify-center space-x-1"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Approve Proposal</span>
                  </button>

                  <button
                    disabled={acting || activeDecision.status === 'rejected'}
                    onClick={() => handleAction('rejected')}
                    className="py-2 px-4 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 disabled:opacity-50 font-semibold text-xs transition flex items-center space-x-1"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>

                  <button
                    disabled={acting || activeDecision.status === 'implemented'}
                    onClick={() => handleAction('implemented')}
                    className="py-2 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 disabled:opacity-50 font-medium text-xs transition"
                  >
                    Mark Executed
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="p-12 text-center text-slate-400 text-xs">No decision selected.</div>
          )}
        </div>
      </div>
    </div>
  );
};
