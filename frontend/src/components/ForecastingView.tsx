import React, { useState, useEffect } from 'react';
import { 
  LineChart as LineChartIcon, AlertTriangle, ShieldAlert, 
  CheckCircle2, TrendingUp, Info, RefreshCw
} from 'lucide-react';
import { 
  ResponsiveContainer, ComposedChart, Line, Area, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend 
} from 'recharts';
import { analyticsApi } from '../services/api';
import { ForecastResult, AnomalyItem } from '../types';

interface ForecastingViewProps {
  activeDatasetId?: string;
}

export const ForecastingView: React.FC<ForecastingViewProps> = ({ activeDatasetId }) => {
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [periods, setPeriods] = useState(6);

  useEffect(() => {
    loadData();
  }, [activeDatasetId, periods]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [fRes, aRes] = await Promise.all([
        analyticsApi.getForecast(activeDatasetId, periods).catch(() => null),
        analyticsApi.getAnomalies(activeDatasetId).catch(() => [])
      ]);
      if (fRes) setForecast(fRes);
      if (aRes) setAnomalies(aRes);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Merge history and forecast into continuous chart data
  const chartData: any[] = [];
  if (forecast) {
    forecast.history.forEach(pt => {
      chartData.push({
        date: pt.date,
        actual: pt.actual,
        predicted: null,
        lower: null,
        upper: null,
      });
    });

    forecast.forecast.forEach(pt => {
      chartData.push({
        date: pt.date,
        actual: null,
        predicted: pt.predicted,
        lower: pt.lower_bound,
        upper: pt.upper_bound,
      });
    });
  }

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'critical':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold uppercase">CRITICAL</span>;
      case 'high':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20 font-semibold uppercase">HIGH</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-500/10 text-sky-400 border border-sky-500/20 uppercase">MEDIUM</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-white tracking-tight flex items-center space-x-2">
            <LineChartIcon className="w-4 h-4 text-sky-400" />
            <span>Time-Series Forecasting Tournament & Anomaly Sentry</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Backtested algorithm tournament (Holt-Winters vs. Trend Regression) with 95% confidence intervals and Z-score outlier detection.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 text-xs text-slate-300">
            <span>Horizon:</span>
            <select
              value={periods}
              onChange={(e) => setPeriods(Number(e.target.value))}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-white font-mono focus:outline-none"
            >
              <option value={3}>3 Periods</option>
              <option value={6}>6 Periods</option>
              <option value={12}>12 Periods</option>
            </select>
          </div>
          <button 
            onClick={loadData}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 border border-slate-700 transition"
            title="Re-run forecast tournament"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Model Selection & Horizon Cards */}
      {forecast && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">Selected Algorithm</span>
            <div className="text-sm font-bold text-white tracking-tight">{forecast.model_name}</div>
            <span className="text-[10px] text-emerald-400 font-mono mt-1 block">Selected via cross-validation</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">Backtest Error (MAPE)</span>
            <div className="text-2xl font-bold text-white font-mono">{forecast.validation_mape}%</div>
            <span className="text-[10px] text-slate-400 font-mono mt-1 block">Mean Abs Percentage Error</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">Residual Error (RMSE)</span>
            <div className="text-2xl font-bold text-white font-mono">${forecast.validation_rmse.toLocaleString()}</div>
            <span className="text-[10px] text-slate-400 font-mono mt-1 block">Root Mean Square Error</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">Projected Growth</span>
            <div className={`text-2xl font-bold font-mono ${forecast.summary_growth_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {forecast.summary_growth_pct > 0 ? `+${forecast.summary_growth_pct}` : forecast.summary_growth_pct}%
            </div>
            <span className="text-[10px] text-slate-400 font-mono mt-1 block">Over next {periods} periods</span>
          </div>
        </div>
      )}

      {/* Forecast Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Projected Trajectory with 95% Confidence Band</h3>
            <p className="text-xs text-slate-400">Historical observations joined to future prediction envelope</p>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono">
            <span className="flex items-center space-x-1.5 text-slate-300">
              <span className="w-3 h-0.5 bg-sky-400"></span>
              <span>Historical Actual</span>
            </span>
            <span className="flex items-center space-x-1.5 text-slate-300">
              <span className="w-3 h-0.5 bg-emerald-400"></span>
              <span>Projected Mean</span>
            </span>
            <span className="flex items-center space-x-1.5 text-slate-300">
              <span className="w-3 h-2 bg-emerald-500/20 border border-emerald-500/40 rounded-sm"></span>
              <span>95% Confidence Range</span>
            </span>
          </div>
        </div>

        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `$${v/1000}k`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                formatter={(value: any) => [value ? `$${Number(value).toLocaleString()}` : '—', '']}
              />
              {/* Confidence Band Envelope */}
              <Area type="monotone" dataKey="upper" stroke="none" fill="#10b981" fillOpacity={0.15} name="Upper Bound (95%)" />
              <Area type="monotone" dataKey="lower" stroke="none" fill="#0f172a" fillOpacity={1} name="Lower Bound (95%)" />
              {/* Actual & Prediction Lines */}
              <Line type="monotone" dataKey="actual" stroke="#38bdf8" strokeWidth={2.5} dot={{ r: 3 }} name="Actual Historical" />
              <Line type="monotone" dataKey="predicted" stroke="#10b981" strokeWidth={2.5} strokeDasharray="4 4" dot={{ r: 4 }} name="Forecast Mean" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Statistical Anomaly Detection Ledger */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Statistical Anomaly & Outlier Ledger</span>
            </h3>
            <p className="text-xs text-slate-400">
              Transactions exceeding 2.5 standard deviations (Z-Score) or falling outside interquartile range (IQR)
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">{anomalies.length} outliers detected</span>
        </div>

        <div className="overflow-x-auto border border-slate-800 rounded-lg">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-[11px]">
              <tr>
                <th className="p-3">Entity / Record</th>
                <th className="p-3">Date</th>
                <th className="p-3 text-right">Observed</th>
                <th className="p-3 text-right">Expected Avg</th>
                <th className="p-3 text-right">Deviation (Z)</th>
                <th className="p-3 text-center">Severity</th>
                <th className="p-3">Audit Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {anomalies.map((anom) => (
                <tr key={anom.id} className="hover:bg-slate-800/40 transition">
                  <td className="p-3 font-semibold text-white">{anom.entity}</td>
                  <td className="p-3 text-slate-400">{anom.date}</td>
                  <td className="p-3 text-right text-emerald-400 font-semibold">${anom.observed_value.toLocaleString()}</td>
                  <td className="p-3 text-right text-slate-400">${anom.expected_value.toLocaleString()}</td>
                  <td className="p-3 text-right text-amber-400">{anom.deviation_z_score > 0 ? `+${anom.deviation_z_score}` : anom.deviation_z_score}σ</td>
                  <td className="p-3 text-center">{getSeverityBadge(anom.severity)}</td>
                  <td className="p-3 text-slate-300 font-sans text-[11px] max-w-xs truncate">{anom.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
