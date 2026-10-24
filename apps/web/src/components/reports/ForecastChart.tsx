"use client";

import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Compass, TrendingDown, TrendingUp } from "lucide-react";
import { HorizonForecastData } from "@/lib/api";
import { formatCurrency, formatPercent } from "@/lib/utils";

interface ForecastChartProps {
  horizons: HorizonForecastData[];
}

export function ForecastChart({ horizons }: ForecastChartProps) {
  if (!horizons || horizons.length === 0) {
    return null;
  }

  const chartData = horizons.map((h) => ({
    name: h.horizon.toUpperCase(),
    Bullish: Math.round(h.bull_prob * 100),
    Neutral: Math.round(h.neutral_prob * 100),
    Bearish: Math.round(h.bear_prob * 100),
    lowPrice: h.price_range_low,
    highPrice: h.price_range_high,
    vol: h.expected_vol,
  }));

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 md:p-8 space-y-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
            <Compass className="w-4 h-4 text-cyan-500" />
            Multi-Horizon Probabilistic Price Targets
          </div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1">
            Calibrated Outcome Channels & Volatility
          </h3>
        </div>
      </div>

      {/* Target Price Channel Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {horizons.map((h) => {
          const midPrice = (h.price_range_low + h.price_range_high) / 2;
          return (
            <div
              key={h.horizon}
              className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-black px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                  {h.horizon.toUpperCase()} HORIZON
                </span>
                <span className="text-[11px] font-semibold text-slate-500">
                  Vol: {formatPercent(h.expected_vol)}
                </span>
              </div>

              <div>
                <div className="text-[11px] font-semibold text-slate-400">Target Range (95% CI)</div>
                <div className="text-lg font-black text-slate-900 dark:text-white mt-0.5 flex items-center gap-1.5">
                  <span className="text-slate-500 text-sm">{formatCurrency(h.price_range_low)}</span>
                  <span className="text-slate-400">&rarr;</span>
                  <span className="text-cyan-500 font-bold">{formatCurrency(h.price_range_high)}</span>
                </div>
              </div>

              {/* Mini probability progress bar */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] font-bold">
                  <span className="text-emerald-500">{formatPercent(h.bull_prob)} Bull</span>
                  <span className="text-purple-400">{formatPercent(h.neutral_prob)} Flat</span>
                  <span className="text-rose-500">{formatPercent(h.bear_prob)} Bear</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden flex">
                  <div style={{ width: `${h.bull_prob * 100}%` }} className="bg-emerald-500" />
                  <div style={{ width: `${h.neutral_prob * 100}%` }} className="bg-purple-500" />
                  <div style={{ width: `${h.bear_prob * 100}%` }} className="bg-rose-500" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Probability Chart */}
      <div className="h-64 w-full pt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
            <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} domain={[0, 100]} unit="%" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#1e293b",
                borderRadius: "0.75rem",
                color: "#f8fafc",
                fontSize: "12px",
              }}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
            <Bar dataKey="Bullish" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]} />
            <Bar dataKey="Neutral" stackId="a" fill="#8b5cf6" radius={[0, 0, 0, 0]} />
            <Bar dataKey="Bearish" stackId="a" fill="#f43f5e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
