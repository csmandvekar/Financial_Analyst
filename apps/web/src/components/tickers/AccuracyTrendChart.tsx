"use client";

import React from "react";
import {
  Activity,
  Award,
  CheckCircle2,
  HelpCircle,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  XCircle,
} from "lucide-react";
import { EvaluationMetricsResponse, EvaluationOutcomeItem } from "@/lib/api";
import { formatCurrency, formatDate, formatPercent } from "@/lib/utils";

interface AccuracyTrendChartProps {
  metrics: EvaluationMetricsResponse["metrics"];
  outcomes: EvaluationOutcomeItem[];
  symbol: string;
}

export function AccuracyTrendChart({ metrics, outcomes, symbol }: AccuracyTrendChartProps) {
  const filteredOutcomes = outcomes.filter(
    (o) => !symbol || o.ticker.toUpperCase() === symbol.toUpperCase()
  );

  return (
    <div className="space-y-6">
      {/* Metric Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Directional Accuracy</span>
            <Activity className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {formatPercent(metrics.directional_accuracy)}
          </div>
          <p className="text-[11px] text-slate-500">Predicted bull/bear matches realized price change</p>
        </div>

        <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Brier Score</span>
            <ShieldCheck className="w-4 h-4 text-cyan-500" />
          </div>
          <div className="text-3xl font-black text-cyan-500">
            {metrics.brier_calibration_score.toFixed(3)}
          </div>
          <p className="text-[11px] text-slate-500">Calibration error (0.0 = perfect, &lt; 0.25 = well-calibrated)</p>
        </div>

        <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Price Forecast RMSE</span>
            <TrendingUp className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {formatCurrency(metrics.price_rmse)}
          </div>
          <p className="text-[11px] text-slate-500">Root Mean Square Error of range midpoint</p>
        </div>

        <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Interval Coverage</span>
            <Award className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {formatPercent(metrics.interval_coverage)}
          </div>
          <p className="text-[11px] text-slate-500">% actual prices landing within target [low, high]</p>
        </div>
      </div>

      {/* Historical Forecast Outcome Log */}
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">
              Historical Forecast Outcomes for {symbol.toUpperCase()}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Empirical backtest verification of past multi-horizon predictions vs actual market prices
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-950/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 uppercase font-semibold">
              <tr>
                <th className="px-4 py-3">Horizon</th>
                <th className="px-4 py-3">Predicted Stance</th>
                <th className="px-4 py-3">Realized Stance</th>
                <th className="px-4 py-3">Outcome</th>
                <th className="px-4 py-3">Predicted Target Channel</th>
                <th className="px-4 py-3">Actual Final Price</th>
                <th className="px-4 py-3 text-right">Evaluated Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium">
              {filteredOutcomes.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3.5 font-bold uppercase">{item.horizon}</td>
                  <td className="px-4 py-3.5 capitalize font-semibold">{item.predicted_direction}</td>
                  <td className="px-4 py-3.5 capitalize font-semibold">{item.actual_direction}</td>
                  <td className="px-4 py-3.5">
                    {item.is_direction_correct ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-500">
                        <CheckCircle2 className="w-3.5 h-3.5" /> HIT
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/10 text-rose-500">
                        <XCircle className="w-3.5 h-3.5" /> MISS
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3.5 font-mono text-slate-600 dark:text-slate-300">
                    {formatCurrency(item.predicted_price_low)} &rarr; {formatCurrency(item.predicted_price_high)}
                  </td>
                  <td className="px-4 py-3.5 font-mono font-bold text-slate-900 dark:text-white">
                    {formatCurrency(item.actual_price)}
                  </td>
                  <td className="px-4 py-3.5 text-right text-slate-500">{formatDate(item.evaluated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
