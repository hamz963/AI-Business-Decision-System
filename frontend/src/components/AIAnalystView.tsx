import React, { useState, useEffect } from 'react';
import { 
  Bot, Send, Sparkles, CheckCircle2, ArrowRight, 
  Terminal, ShieldCheck, HelpCircle, ExternalLink, Cpu
} from 'lucide-react';
import { aiAnalystApi } from '../services/api';
import { AIAnalystResponse, ModelOption } from '../types';

interface AIAnalystViewProps {
  activeDatasetId?: string;
  onNavigate: (tab: string) => void;
}

export const AIAnalystView: React.FC<AIAnalystViewProps> = ({ activeDatasetId, onNavigate }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<ModelOption[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('gemini-2.5-flash');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; data?: AIAnalystResponse; text?: string }>>([
    {
      role: 'assistant',
      text: 'Hello. I am your Grounded Business Decision Analyst powered by 100% free-tier AI models and deterministic computation. You can select your model of choice from the top right selector or run offline using local models.'
    }
  ]);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const data = await aiAnalystApi.getModels();
      setModels(data);
      const active = data.find(m => m.is_active);
      if (active) {
        setSelectedModel(active.id);
      }
    } catch (err) {
      console.error('Failed to fetch AI models:', err);
    }
  };

  const handleModelChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newModel = e.target.value;
    setSelectedModel(newModel);
    try {
      await aiAnalystApi.selectModel(newModel);
      setModels(prev => prev.map(m => ({ ...m, is_active: m.id === newModel })));
    } catch (err) {
      console.error('Failed to set active model:', err);
    }
  };

  const quickPrompts = [
    "Why did gross margin contract in recent periods?",
    "What happens if prices increase by 8%?",
    "Forecast revenue trajectory for next 6 months",
    "Identify unusual transaction anomalies in the ledger",
  ];

  const handleSend = async (textToSend?: string) => {
    const q = textToSend || query;
    if (!q.trim()) return;

    const userMsg = { role: 'user' as const, text: q };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await aiAnalystApi.query(q, activeDatasetId, selectedModel);
      setMessages(prev => [...prev, { role: 'assistant', data: res }]);
    } catch (e: any) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: `Error processing query: ${e.response?.data?.detail || e.message}` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      {/* Top Bar */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Grounded AI Business Analyst</h3>
            <p className="text-xs text-slate-400">Zero hallucinations • OpenCode & Free-Tier Engine • Auditable grounding</p>
          </div>
        </div>

        {/* Dynamic Model Selector */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 shadow-sm">
            <Cpu className="w-3.5 h-3.5 text-sky-400" />
            <label className="text-[11px] text-slate-400 font-mono">Model:</label>
            <select
              value={selectedModel}
              onChange={handleModelChange}
              className="bg-transparent text-xs text-sky-300 font-mono font-medium focus:outline-none cursor-pointer"
            >
              {models.map((m) => (
                <option key={m.id} value={m.id} className="bg-slate-900 text-white">
                  {m.name} {m.free_tier ? '(Free)' : ''}
                </option>
              ))}
            </select>
          </div>

          <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Guardrails Enforced</span>
          </span>
        </div>
      </div>

      {/* Conversation Stream */}
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'user' ? (
              <div className="max-w-xl bg-sky-600 text-white rounded-2xl rounded-tr-none px-4 py-3 text-xs leading-relaxed shadow">
                {msg.text}
              </div>
            ) : msg.data ? (
              /* Structured Grounded AI Output */
              <div className="max-w-3xl bg-slate-950 border border-slate-800 rounded-2xl rounded-tl-none p-5 space-y-4 shadow-xl text-left">
                {/* Intent & Confidence Header */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 text-[11px] font-mono">
                  <div className="flex items-center space-x-2">
                    <span className="text-sky-400 font-semibold uppercase tracking-wider">
                      Intent: {msg.data.intent}
                    </span>
                    {msg.data.analyst_mode && (
                      <span className="px-2 py-0.5 rounded text-[10px] bg-sky-500/10 text-sky-300 border border-sky-500/20">
                        {msg.data.analyst_mode}
                      </span>
                    )}
                  </div>
                  <span className="text-slate-400">Confidence: {msg.data.confidence}</span>
                </div>

                {/* Synthesis Answer */}
                <div className="text-xs text-slate-200 leading-relaxed font-medium whitespace-pre-line">
                  {msg.data.answer}
                </div>

                {/* Categorized Grounding Blocks */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {/* Verified Facts */}
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 font-bold block">
                      FACT (Verified Ledger)
                    </span>
                    {msg.data.facts.map((f, i) => (
                      <div key={i} className="text-slate-300 text-[11px] flex items-start space-x-1.5">
                        <span className="text-emerald-400 mt-0.5">•</span>
                        <span>{f}</span>
                      </div>
                    ))}
                  </div>

                  {/* Statistical Inferences */}
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-sky-400 font-bold block">
                      INFERENCE (Driver Analysis)
                    </span>
                    {msg.data.inferences.map((inf, i) => (
                      <div key={i} className="text-slate-300 text-[11px] flex items-start space-x-1.5">
                        <span className="text-sky-400 mt-0.5">•</span>
                        <span>{inf}</span>
                      </div>
                    ))}
                  </div>

                  {/* Model Predictions */}
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-indigo-400 font-bold block">
                      PREDICTION (Validated Models)
                    </span>
                    {msg.data.predictions.map((p, i) => (
                      <div key={i} className="text-slate-300 text-[11px] flex items-start space-x-1.5">
                        <span className="text-indigo-400 mt-0.5">•</span>
                        <span>{p}</span>
                      </div>
                    ))}
                  </div>

                  {/* Strategic Recommendations */}
                  <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1.5">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-amber-400 font-bold block">
                      RECOMMENDATION (Actionable)
                    </span>
                    {msg.data.recommendations.map((r, i) => (
                      <div key={i} className="text-slate-300 text-[11px] flex items-start space-x-1.5">
                        <span className="text-amber-400 mt-0.5">•</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Underlying Evidence Citations */}
                <div className="pt-2 border-t border-slate-800 flex flex-wrap gap-2 text-[11px] font-mono">
                  {msg.data.evidence.map((ev, i) => (
                    <span key={i} className="px-2 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                      {ev.metric}: <span className="text-sky-400">{ev.value}</span>
                    </span>
                  ))}
                </div>

                {/* Suggested Action Buttons */}
                {msg.data.suggested_actions && msg.data.suggested_actions.length > 0 && (
                  <div className="pt-2 border-t border-slate-800 flex flex-wrap gap-2">
                    {msg.data.suggested_actions.map((act, i) => (
                      <button
                        key={i}
                        onClick={() => {
                          if (act.toLowerCase().includes('scenario')) onNavigate('scenarios');
                          else if (act.toLowerCase().includes('decision')) onNavigate('decisions');
                          else if (act.toLowerCase().includes('forecast')) onNavigate('forecasting');
                        }}
                        className="text-xs px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 transition flex items-center space-x-1"
                      >
                        <span>{act}</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="max-w-xl bg-slate-950 border border-slate-800 text-slate-300 rounded-2xl rounded-tl-none p-4 text-xs leading-relaxed">
                {msg.text}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-950 border border-slate-800 rounded-2xl rounded-tl-none px-4 py-3 text-xs text-slate-400 flex items-center space-x-2 font-mono">
              <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping"></span>
              <span>Executing analytical tools & verifying grounding citations with {selectedModel}...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Section & Quick Prompts */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/60 space-y-3">
        {/* Quick Chips */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-[11px]">
          <span className="text-slate-400 flex-shrink-0">Try:</span>
          {quickPrompts.map((p, i) => (
            <button
              key={i}
              onClick={() => handleSend(p)}
              className="px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-750 text-slate-300 border border-slate-700 whitespace-nowrap transition"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Query Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex space-x-2"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Ask a strategic question using ${selectedModel}...`}
            className="flex-1 px-4 py-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-sky-500 font-sans"
          />
          <button
            type="submit"
            disabled={!query.trim() || loading}
            className="px-4 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-slate-950 font-semibold text-xs flex items-center space-x-1.5 transition shadow cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send Query</span>
          </button>
        </form>
      </div>
    </div>
  );
};
