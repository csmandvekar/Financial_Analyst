"use client";

import React, { useEffect, useState } from "react";
import {
  CheckCircle2,
  CircleDashed,
  Compass,
  Cpu,
  Database,
  FileCheck2,
  Layers,
  Loader2,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

export interface PipelineStage {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
}

export const PIPELINE_STAGES: PipelineStage[] = [
  {
    id: "collection",
    name: "1. Data Collection Fan-Out",
    description: "Concurrently querying Market Data, Financials, News, Sentiment & Sector Peers",
    icon: Database,
  },
  {
    id: "validation",
    name: "2. Data Sanity & Provenance Validation",
    description: "Verifying timestamps, schema bounds, and identifying degraded data sources",
    icon: ShieldCheck,
  },
  {
    id: "signal",
    name: "3. Deterministic Signal Generation",
    description: "Computing fundamental, technical momentum, and sector factor scores in [-1.0, 1.0]",
    icon: Cpu,
  },
  {
    id: "risk",
    name: "4. Quantitative Risk Modeling",
    description: "Simulating interest rate hikes, market selloffs, and volatility bands",
    icon: Layers,
  },
  {
    id: "forecast",
    name: "5. Multi-Horizon Probabilistic Forecasting",
    description: "Synthesizing price channels and bull/bear/neutral calibrated probabilities (3m, 6m, 1y)",
    icon: Compass,
  },
  {
    id: "report",
    name: "6. Narrative Synthesis & Persistence",
    description: "Drafting executive thesis, citations audit, and persisting to PostgreSQL & Redis",
    icon: FileCheck2,
  },
];

interface JobStatusStepperProps {
  status: "pending" | "running" | "completed" | "degraded" | "failed";
  currentStageIndex?: number;
}

export function JobStatusStepper({ status, currentStageIndex = 6 }: JobStatusStepperProps) {
  const isFinished = status === "completed" || status === "degraded";

  return (
    <div className="space-y-4">
      {PIPELINE_STAGES.map((stage, idx) => {
        const Icon = stage.icon;
        const isPast = isFinished || idx < currentStageIndex;
        const isCurrent = !isFinished && idx === currentStageIndex;

        return (
          <div
            key={stage.id}
            className={`p-4 rounded-xl border transition-all flex items-start gap-4 ${
              isPast
                ? "bg-white/90 dark:bg-slate-900/90 border-slate-200 dark:border-slate-800"
                : isCurrent
                ? "bg-cyan-500/10 dark:bg-cyan-950/40 border-cyan-500 ring-1 ring-cyan-500/50 shadow-md shadow-cyan-500/10"
                : "bg-slate-50/50 dark:bg-slate-950/40 border-slate-200/50 dark:border-slate-800/40 opacity-50"
            }`}
          >
            <div className="mt-0.5">
              {isPast ? (
                <div className="w-8 h-8 rounded-full bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-500 flex items-center justify-center border border-emerald-500/30">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
              ) : isCurrent ? (
                <div className="w-8 h-8 rounded-full bg-cyan-500 text-white flex items-center justify-center shadow-md shadow-cyan-500/30 animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
              ) : (
                <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center border border-slate-200 dark:border-slate-700">
                  <CircleDashed className="w-4 h-4" />
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4
                  className={`text-sm font-bold ${
                    isPast
                      ? "text-slate-900 dark:text-white"
                      : isCurrent
                      ? "text-cyan-600 dark:text-cyan-400"
                      : "text-slate-500 dark:text-slate-400"
                  }`}
                >
                  {stage.name}
                </h4>
                <span className="text-[11px] font-semibold uppercase tracking-wider">
                  {isPast ? (
                    <span className="text-emerald-500">Completed</span>
                  ) : isCurrent ? (
                    <span className="text-cyan-500 animate-pulse">Running</span>
                  ) : (
                    <span className="text-slate-400">Pending</span>
                  )}
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{stage.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
