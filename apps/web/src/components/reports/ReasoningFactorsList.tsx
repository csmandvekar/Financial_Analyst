import React from "react";
import { Cpu, Layers, Sparkles } from "lucide-react";
import { ReasoningFactorData } from "@/lib/api";
import { formatPercent } from "@/lib/utils";

interface ReasoningFactorsListProps {
  factors: ReasoningFactorData[];
}

export function ReasoningFactorsList({ factors }: ReasoningFactorsListProps) {
  if (!factors || factors.length === 0) return null;

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 md:p-8 space-y-6 shadow-sm">
      <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 dark:border-slate-800/80 pb-4">
        <Cpu className="w-4 h-4 text-cyan-500" />
        Deterministic Multi-Factor Signal Decomposition
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {factors.map((factor) => {
          const isPositive = factor.signal_value >= 0;
          const absVal = Math.min(1.0, Math.abs(factor.signal_value));
          const scorePercent = (absVal * 100).toFixed(0);

          return (
            <div
              key={factor.factor_name}
              className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold capitalize text-slate-900 dark:text-white">
                  {factor.factor_name.replace("_", " ")}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-semibold text-slate-400">
                    Weight: {formatPercent(factor.weight)}
                  </span>
                  <span
                    className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                      isPositive
                        ? "bg-emerald-500/10 text-emerald-500"
                        : "bg-rose-500/10 text-rose-500"
                    }`}
                  >
                    {isPositive ? "+" : ""}
                    {factor.signal_value.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Bipolar progress bar [-1.0, 1.0] */}
              <div className="space-y-1">
                <div className="h-2 w-full rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden relative">
                  <div
                    className={`h-full rounded-full transition-all ${
                      isPositive ? "bg-emerald-500" : "bg-rose-500"
                    }`}
                    style={{ width: `${scorePercent}%` }}
                  />
                </div>
              </div>

              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                {factor.contribution_summary}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
