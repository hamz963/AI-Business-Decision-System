import React, { useState, useEffect } from 'react';
import { 
  Sliders, TrendingUp, TrendingDown, AlertTriangle, ShieldCheck, 
  Save, RefreshCcw, ArrowRight, DollarSign, Percent
} from 'lucide-react';
import { scenariosApi } from '../services/api';
import { ScenarioParams, ScenarioResult } from '../types';

interface ScenariosViewProps {
  activeDatasetId?: string;
}

export const ScenariosView: React.FC<ScenariosViewProps> = ({ activeDatasetId }) => {
  const [params, setParams] = useState<ScenarioParams>({
    price_change_pct: 5.0,
    marketing_spend_pct: 10.0,
    operating_cost_pct: -3.0,
    headcount_change_pct: 0.0,
    discount_rate_pct: 0.0,
    assumed_elasticity: -1.2
  });

  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    runSim();
  }, [params, activeDatasetId]);

  const runSim = async () => {
    setLoading(true);
    try {
      const res = await scenariosApi.simulate(params, activeDatasetId);
      setResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await scenariosApi.save(params, `Scenario: Price ${params.price_change_pct}% / Mktg ${params.marketing_spend_pct}%`, '', activeDatasetId);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  const resetParams = () => {
    setParams({
      price_change_pct: 0.0,
      marketing_spend_pct: 0.0,
      operating_cost_pct: 0.0,
      headcount_change_pct: 0.0,
      discount_rate_pct: 0.0,
      assumed_elasticity: -1.2
    });
  };

  return (
    <div className="space-y-6">
      {/* Top Description */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-sky-400" />
            <span>What-If Econometric Simulation Studio</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Test business levers: pricing elasticity, marketing budget scaling, operational cost shocks, and margin stress tests.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={resetParams}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-medium border border-slate-700 flex items-center space-x-1 transition"
          >
            <RefreshCcw className="w-3.5 h-3.5" />
            <span>Reset Baseline</span>
          </button>
          <button
            onClick={handleSave}
            className="px-3 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-semibold flex items-center space-x-1.5 transition shadow-sm"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{saveSuccess ? 'Saved to Audit!' : 'Save Scenario'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Levers & Sliders Panel (5 cols) */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-6">
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
            Adjust Strategic Levers
          </h3>

          {/* Lever 1: Price */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-300 font-medium">Selling Price Adjustment</span>
              <span className="font-mono text-sky-400 font-semibold">
                {params.price_change_pct > 0 ? `+${params.price_change_pct}` : params.price_change_pct}%
              </span>
            </div>
            <input 
              type="range" min="-30" max="50" step="1"
              value={params.price_change_pct}
              onChange={(e) => setParams({ ...params, price_change_pct: parseFloat(e.target.value) })}
              className="w-full accent-sky-500 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-30% Discount</span>
              <span>Baseline (0%)</span>
              <span>+50% Uplift</span>
            </div>
          </div>

          {/* Lever 2: Marketing Budget */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-300 font-medium">Marketing Budget Scaling</span>
              <span className="font-mono text-emerald-400 font-semibold">
                {params.marketing_spend_pct > 0 ? `+${params.marketing_spend_pct}` : params.marketing_spend_pct}%
              </span>
            </div>
            <input 
              type="range" min="-50" max="100" step="5"
              value={params.marketing_spend_pct}
              onChange={(e) => setParams({ ...params, marketing_spend_pct: parseFloat(e.target.value) })}
              className="w-full accent-emerald-500 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-50% Cut</span>
              <span>Baseline (0%)</span>
              <span>+100% Scale</span>
            </div>
          </div>

          {/* Lever 3: Operating Costs */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-300 font-medium">Operational Cost Shift (OPEX)</span>
              <span className="font-mono text-amber-400 font-semibold">
                {params.operating_cost_pct > 0 ? `+${params.operating_cost_pct}` : params.operating_cost_pct}%
              </span>
            </div>
            <input 
              type="range" min="-25" max="35" step="1"
              value={params.operating_cost_pct}
              onChange={(e) => setParams({ ...params, operating_cost_pct: parseFloat(e.target.value) })}
              className="w-full accent-amber-500 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-25% Rationalization</span>
              <span>Baseline (0%)</span>
              <span>+35% Inflation</span>
            </div>
          </div>

          {/* Lever 4: Price Elasticity */}
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-300 font-medium">Demand Price Elasticity (ε)</span>
              <span className="font-mono text-indigo-400 font-semibold">{params.assumed_elasticity}</span>
            </div>
            <input 
              type="range" min="-2.5" max="-0.5" step="0.1"
              value={params.assumed_elasticity}
              onChange={(e) => setParams({ ...params, assumed_elasticity: parseFloat(e.target.value) })}
              className="w-full accent-indigo-500 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-2.5 (Highly Elastic)</span>
              <span>-1.2 (Standard)</span>
              <span>-0.5 (Inelastic)</span>
            </div>
          </div>
        </div>

        {/* Projected Impact & P&L Cards (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {result ? (
            <>
              {/* Core Output Deltas */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                  <span className="text-[11px] font-mono text-slate-400 block mb-1">Projected Revenue</span>
                  <div className="text-xl font-bold text-white font-mono">
                    ${result.projected.revenue.toLocaleString()}
                  </div>
                  <div className={`text-xs font-mono mt-1 ${result.deltas.revenue_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {result.deltas.revenue_delta_pct > 0 ? `+${result.deltas.revenue_delta_pct}` : result.deltas.revenue_delta_pct}%
                    <span className="text-slate-400 text-[10px] ml-1 font-sans">
                      ({result.deltas.revenue_delta >= 0 ? '+$' : '-$'}{Math.abs(result.deltas.revenue_delta).toLocaleString()})
                    </span>
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                  <span className="text-[11px] font-mono text-slate-400 block mb-1">Projected Net Profit</span>
                  <div className="text-xl font-bold text-white font-mono">
                    ${result.projected.net_profit.toLocaleString()}
                  </div>
                  <div className={`text-xs font-mono mt-1 ${result.deltas.net_profit_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {result.deltas.net_profit_delta_pct > 0 ? `+${result.deltas.net_profit_delta_pct}` : result.deltas.net_profit_delta_pct}%
                    <span className="text-slate-400 text-[10px] ml-1 font-sans">
                      ({result.deltas.net_profit_delta >= 0 ? '+$' : '-$'}{Math.abs(result.deltas.net_profit_delta).toLocaleString()})
                    </span>
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                  <span className="text-[11px] font-mono text-slate-400 block mb-1">Risk Score</span>
                  <div className="text-xl font-bold text-white font-mono flex items-center space-x-2">
                    <span>{result.risk_score}/100</span>
                    <span className={`text-[10px] font-sans px-2 py-0.5 rounded font-semibold uppercase ${
                      result.risk_score < 35 ? 'bg-emerald-500/10 text-emerald-400' :
                      result.risk_score < 65 ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'
                    }`}>
                      {result.risk_assessment.level}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400 block mt-1">Multi-factor volatility</span>
                </div>
              </div>

              {/* Baseline vs Projected Comparison Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 overflow-x-auto">
                <div className="text-xs font-semibold text-white mb-3">P&L Variance Breakdown</div>
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                      <th className="pb-2">Metric</th>
                      <th className="pb-2 text-right">Baseline</th>
                      <th className="pb-2 text-right">Projected</th>
                      <th className="pb-2 text-right">Variance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    <tr>
                      <td className="py-2.5 text-slate-300">Gross Revenue</td>
                      <td className="py-2.5 text-right text-slate-400">${result.baseline.revenue.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-white font-semibold">${result.projected.revenue.toLocaleString()}</td>
                      <td className={`py-2.5 text-right ${result.deltas.revenue_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {result.deltas.revenue_delta >= 0 ? '+' : ''}${result.deltas.revenue_delta.toLocaleString()}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 text-slate-300">Cost of Goods Sold (COGS)</td>
                      <td className="py-2.5 text-right text-slate-400">${result.baseline.cogs.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-white">${result.projected.cogs.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-slate-400">
                        ${(result.projected.cogs - result.baseline.cogs).toLocaleString()}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 text-slate-300">Operating Expenses (OPEX)</td>
                      <td className="py-2.5 text-right text-slate-400">${result.baseline.operating_expenses.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-white">${result.projected.operating_expenses.toLocaleString()}</td>
                      <td className="py-2.5 text-right text-slate-400">
                        ${(result.projected.operating_expenses - result.baseline.operating_expenses).toLocaleString()}
                      </td>
                    </tr>
                    <tr className="bg-slate-950/40">
                      <td className="py-2.5 text-slate-200 font-semibold">Net Operating Margin</td>
                      <td className="py-2.5 text-right text-slate-400">{result.baseline.net_margin_pct.toFixed(1)}%</td>
                      <td className="py-2.5 text-right text-white font-semibold">{result.projected.net_margin_pct.toFixed(1)}%</td>
                      <td className={`py-2.5 text-right font-semibold ${result.deltas.margin_delta_basis_pts >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {result.deltas.margin_delta_basis_pts >= 0 ? '+' : ''}{result.deltas.margin_delta_basis_pts.toFixed(0)} bps
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Tradeoff & Prescriptive Recommendation */}
              <div className="bg-gradient-to-r from-slate-900 to-slate-950 border border-slate-800 rounded-xl p-5 space-y-3">
                <div>
                  <span className="text-[11px] font-mono uppercase tracking-wider text-sky-400 font-semibold">
                    Tradeoff Synthesis
                  </span>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                    {result.tradeoff_summary}
                  </p>
                </div>
                <div className="pt-2 border-t border-slate-800">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-400 font-semibold">
                    Model Recommendation
                  </span>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                    {result.recommendation}
                  </p>
                </div>
              </div>
            </>
          ) : (
            <div className="p-12 text-center text-slate-400 text-xs">Simulating scenario...</div>
          )}
        </div>
      </div>
    </div>
  );
};
