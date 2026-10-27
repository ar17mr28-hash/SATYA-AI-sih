import React, { useState } from 'react';
import { Sparkles, RefreshCw, CheckCircle2, AlertTriangle, FileWarning, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

interface DemoBannerProps {
  onSelectScenario: (scenarioId: string) => void;
  onDataReset?: () => void;
}

export const DemoBanner: React.FC<DemoBannerProps> = ({ onSelectScenario, onDataReset }) => {
  const [resetting, setResetting] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  const handleReset = async () => {
    try {
      setResetting(true);
      await api.resetDemoDatabase();
      setResetSuccess(true);
      setTimeout(() => setResetSuccess(false), 3000);
      if (onDataReset) onDataReset();
    } catch (e) {
      alert('Failed to reset demo data: ' + e);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="bg-gradient-to-r from-navy-900 via-navy-800 to-navy-900 text-white border-b border-navy-700/60 px-4 py-2.5 text-xs shadow-md">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 bg-royal-600/80 text-white px-2 py-0.5 rounded font-mono font-semibold tracking-wider uppercase text-[10px] border border-royal-400/40">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            SIH 2026 Judge Demo Bar
          </span>
          <span className="text-slate-300 hidden md:inline">
            Explore 3 pre-configured institutional verification scenarios:
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => onSelectScenario('scenario-1')}
            className="flex items-center gap-1.5 bg-emerald-950/80 hover:bg-emerald-900 text-emerald-200 border border-emerald-500/40 px-2.5 py-1 rounded transition-colors"
            title="Apex Institute: All documents valid & consistent (100% compliance)"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-medium">Scenario 1: Valid App</span>
          </button>

          <button
            onClick={() => onSelectScenario('scenario-2')}
            className="flex items-center gap-1.5 bg-red-950/80 hover:bg-red-900 text-red-200 border border-red-500/40 px-2.5 py-1 rounded transition-colors"
            title="Bharati Academy: Missing mandatory Land Title Deed"
          >
            <FileWarning className="w-3.5 h-3.5 text-red-400" />
            <span className="font-medium">Scenario 2: Missing Document</span>
          </button>

          <button
            onClick={() => onSelectScenario('scenario-3')}
            className="flex items-center gap-1.5 bg-amber-950/80 hover:bg-amber-900 text-amber-200 border border-amber-500/40 px-2.5 py-1 rounded transition-colors"
            title="Global Institute: Name mismatch between Application & Registration Certificate"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span className="font-medium">Scenario 3: Name Mismatch (XAI)</span>
          </button>

          <button
            onClick={handleReset}
            disabled={resetting}
            className="flex items-center gap-1 bg-navy-700 hover:bg-navy-600 text-slate-200 border border-navy-500/50 px-2 py-1 rounded transition-colors disabled:opacity-50"
            title="Reset database to fresh test records"
          >
            <RefreshCw className={`w-3 h-3 ${resetting ? 'animate-spin text-cyan-400' : ''}`} />
            <span>{resetting ? 'Resetting...' : resetSuccess ? 'Reset Complete!' : 'Reset Demo'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
