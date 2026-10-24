"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Activity,
  ArrowLeft,
  Calendar,
  CheckCircle2,
  Cpu,
  History,
  Loader2,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import { AccuracyTrendChart } from "@/components/tickers/AccuracyTrendChart";
import {
  EvaluationMetricsResponse,
  EvaluationOutcomeItem,
  getEvaluationMetrics,
  getEvaluationOutcomes,
  triggerBacktest,
} from "@/lib/api";

export default function TickerHistoryPage() {
  const params = useParams();
  const symbol = (params?.symbol as string) || "AAPL";

  const [metrics, setMetrics] = useState<EvaluationMetricsResponse["metrics"] | null>(null);
  const [outcomes, setOutcomes] = useState<EvaluationOutcomeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [backtesting, setBacktesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [mRes, oRes] = await Promise.all([
        getEvaluationMetrics(),
        getEvaluationOutcomes(50),
      ]);
      setMetrics(mRes.metrics);
      setOutcomes(oRes);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || "Failed to load accuracy metrics");
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [symbol]);

  const handleRunBacktest = async () => {
    setBacktesting(true);
    try {
      await triggerBacktest([symbol.toUpperCase(), "MSFT", "NVDA", "GOOGL", "AMZN"], 180, "3m");
      await loadData();
    } catch (err: any) {
      setError(err.message || "Backtest failed");
    } finally {
      setBacktesting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 dark:text-slate-400 hover:text-cyan-500 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Dashboard
        </Link>

        <button
          onClick={handleRunBacktest}
          disabled={backtesting}
          className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500 hover:bg-cyan-600 text-white shadow-md shadow-cyan-500/20 transition-all flex items-center gap-1.5 disabled:opacity-50"
        >
          {backtesting ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Running Backtest...
            </>
          ) : (
            <>
              <RefreshCw className="w-3.5 h-3.5" />
              Re-run Historical Backtest
            </>
          )}
        </button>
      </div>

      {/* Header */}
      <div className="space-y-2 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
          <Activity className="w-3.5 h-3.5" />
          Empirical Accountability & Calibration Framework
        </div>
        <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">
          Historical Prediction Accuracy: {symbol.toUpperCase()}
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Evaluates past multi-horizon forecast channels against realized market outcomes, measuring Brier score calibration and directional hit rate.
        </p>
      </div>

      {loading ? (
        <div className="p-16 flex flex-col items-center justify-center space-y-3 text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
          <p className="text-sm font-medium">Computing empirical calibration statistics...</p>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 text-xs font-medium">
          {error}
        </div>
      ) : metrics ? (
        <AccuracyTrendChart metrics={metrics} outcomes={outcomes} symbol={symbol} />
      ) : null}
    </div>
  );
}
