"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  BarChart2,
  Calendar,
  Compass,
  Cpu,
  Layers,
  Loader2,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { TickerSearchInput } from "@/components/analysis/TickerSearchInput";
import { submitAnalysis } from "@/lib/api";

export const ANALYSIS_TYPES = [
  {
    id: "quarterly_outlook",
    title: "Quarterly Outlook",
    description: "Balanced multi-agent synthesis with 4-factor fusion (Fundamental, Technical, Sector, Sentiment).",
    icon: Compass,
    badge: "Recommended",
  },
  {
    id: "deep_dive",
    title: "Valuation Deep Dive",
    description: "In-depth financial statement forensics, peer margin multiples, and DuPont analysis.",
    icon: BarChart2,
    badge: "Forensics",
  },
  {
    id: "risk_assessment",
    title: "Downside Stress Test",
    description: "Quantitative tail-risk modeling, interest rate hike shocks, and market drawdown resilience.",
    icon: ShieldAlert,
    badge: "Defensive",
  },
];

export function AnalysisConfigForm({ initialTicker = "AAPL" }: { initialTicker?: string }) {
  const router = useRouter();
  const [ticker, setTicker] = useState(initialTicker);
  const [analysisType, setAnalysisType] = useState("quarterly_outlook");
  const [horizon, setHorizon] = useState("3m");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) {
      setErrorMessage("Please select or enter a valid stock ticker symbol.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const result = await submitAnalysis(ticker.trim().toUpperCase(), analysisType);
      if (result.job_id) {
        router.push(`/jobs/${result.job_id}`);
      } else {
        throw new Error("No job_id returned from API");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to trigger analysis. Please check your backend connection.");
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Ticker Search Autocomplete */}
      <TickerSearchInput value={ticker} onChange={setTicker} />

      {/* Analysis Type Selection */}
      <div className="space-y-3">
        <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          Intelligence Objective
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {ANALYSIS_TYPES.map((type) => {
            const Icon = type.icon;
            const isSelected = analysisType === type.id;
            return (
              <button
                key={type.id}
                type="button"
                onClick={() => setAnalysisType(type.id)}
                className={`relative p-4 rounded-xl text-left border transition-all flex flex-col justify-between ${
                  isSelected
                    ? "bg-cyan-500/10 dark:bg-cyan-950/30 border-cyan-500 text-slate-900 dark:text-white ring-1 ring-cyan-500/50 shadow-sm"
                    : "bg-white dark:bg-slate-900/80 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className={`p-2 rounded-lg ${isSelected ? "bg-cyan-500 text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                      {type.badge}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold mb-1 text-slate-900 dark:text-white">{type.title}</h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{type.description}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Target Forecast Horizon */}
      <div className="space-y-3">
        <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          Primary Prediction Horizon
        </label>
        <div className="grid grid-cols-3 gap-3">
          {[
            { id: "3m", label: "3 Months", sub: "Tactical (63 trading days)" },
            { id: "6m", label: "6 Months", sub: "Medium-term (126 days)" },
            { id: "1y", label: "1 Year", sub: "Structural (252 days)" },
          ].map((h) => (
            <button
              key={h.id}
              type="button"
              onClick={() => setHorizon(h.id)}
              className={`p-3 rounded-xl border text-center transition-all ${
                horizon === h.id
                  ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-transparent shadow-sm"
                  : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700"
              }`}
            >
              <div className="text-sm font-bold">{h.label}</div>
              <div className="text-[11px] opacity-70 mt-0.5">{h.sub}</div>
            </button>
          ))}
        </div>
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 text-xs font-medium">
          {errorMessage}
        </div>
      )}

      {/* Submit Trigger */}
      <button
        type="submit"
        disabled={isLoading || !ticker}
        className="w-full py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold text-base shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-[1.01] active:scale-[0.99] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Executing Multi-Agent DAG Pipeline...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            <span>Launch Multi-Agent Intelligence Pipeline</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </>
        )}
      </button>
    </form>
  );
}
