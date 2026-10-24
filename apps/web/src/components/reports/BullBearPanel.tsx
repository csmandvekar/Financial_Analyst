import React from "react";
import { ArrowDownRight, ArrowUpRight, ShieldAlert, Sparkles } from "lucide-react";

interface BullBearPanelProps {
  bullCase: string;
  bearCase: string;
}

export function BullBearPanel({ bullCase, bearCase }: BullBearPanelProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Bull Case */}
      <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 dark:bg-emerald-950/20 p-6 md:p-7 space-y-3 relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-sm uppercase tracking-wider">
            <div className="p-1.5 rounded-lg bg-emerald-500/20">
              <ArrowUpRight className="w-4 h-4" />
            </div>
            Bull Case & Growth Catalysts
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-600 dark:text-emerald-400">
            UPSIDE
          </span>
        </div>
        <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
          {bullCase}
        </p>
      </div>

      {/* Bear Case */}
      <div className="rounded-2xl border border-rose-500/20 bg-rose-500/5 dark:bg-rose-950/20 p-6 md:p-7 space-y-3 relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-bold text-sm uppercase tracking-wider">
            <div className="p-1.5 rounded-lg bg-rose-500/20">
              <ArrowDownRight className="w-4 h-4" />
            </div>
            Bear Case & Downside Risks
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-600 dark:text-rose-400">
            DOWNSIDE
          </span>
        </div>
        <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">
          {bearCase}
        </p>
      </div>
    </div>
  );
}
