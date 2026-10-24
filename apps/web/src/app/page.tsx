"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Activity,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  Compass,
  Cpu,
  Database,
  Flame,
  Globe,
  Layers,
  Search,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Zap,
} from "lucide-react";
import { POPULAR_TICKERS } from "@/components/analysis/TickerSearchInput";

export default function DashboardPage() {
  const router = useRouter();
  const [searchTicker, setSearchTicker] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTicker.trim()) {
      router.push(`/analyze?ticker=${searchTicker.trim().toUpperCase()}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Hero Section */}
      <div className="relative rounded-3xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950 text-white p-8 md:p-14 shadow-2xl">
        <div className="absolute -right-20 -top-20 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-20 -bottom-20 w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Sparkles className="w-3.5 h-3.5" />
            Distributed Multi-Agent Architecture
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight leading-tight">
            Institutional AI <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400">
              Financial Intelligence
            </span>
          </h1>

          <p className="text-slate-300 text-sm md:text-base leading-relaxed max-w-2xl font-normal">
            Synthesize market microstructure, SEC quarterly statements, macro news sentiment, and quantitative downside stress tests into multi-horizon price targets with calibrated probabilities.
          </p>

          {/* Quick Ticker Search Form */}
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3 pt-2 max-w-xl">
            <div className="relative flex-1">
              <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Enter stock ticker (e.g. NVDA, AAPL, MSFT)"
                value={searchTicker}
                onChange={(e) => setSearchTicker(e.target.value)}
                className="w-full pl-11 pr-4 py-3.5 rounded-xl bg-slate-800/90 border border-slate-700 text-white font-bold placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 uppercase tracking-wider text-sm"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 font-bold text-sm text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2 shrink-0"
            >
              <span>Analyze Stock</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Featured Market Watchlist */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Active Market Coverage</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              One-click multi-agent intelligence runs for leading institutional equities
            </p>
          </div>
          <Link
            href="/analyze"
            className="text-xs font-bold text-cyan-500 hover:text-cyan-400 flex items-center gap-1"
          >
            Custom Analysis &rarr;
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {POPULAR_TICKERS.slice(0, 4).map((ticker) => (
            <div
              key={ticker.symbol}
              className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-cyan-500/40 dark:hover:border-cyan-500/40 hover:shadow-lg hover:shadow-cyan-500/5 transition-all flex flex-col justify-between space-y-4 group"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="font-black text-lg text-slate-900 dark:text-white group-hover:text-cyan-500 transition-colors">
                    {ticker.symbol}
                  </span>
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">
                    {ticker.sector}
                  </span>
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">{ticker.name}</div>
              </div>

              <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
                <Link
                  href={`/analyze?ticker=${ticker.symbol}`}
                  className="text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:underline flex items-center gap-1"
                >
                  Generate Report
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
                <Link
                  href={`/tickers/${ticker.symbol}/history`}
                  className="text-[11px] font-semibold text-slate-400 hover:text-slate-200"
                >
                  Accuracy Log
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Core Architectural Highlights */}
      <div className="space-y-4 pt-4">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Platform Core Architecture</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-500 flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white">LangGraph DAG Orchestrator</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Parallel fan-out across 5 collection agents, followed by validation, deterministic signal fusion, stress testing, and synthesis.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white">Resilience & Circuit Breakers</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Multi-layer resilience with 3-state circuit breakers, token bucket rate limiters, and graceful degraded fallbacks during outages.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white">Calibrated Brier Evaluation</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Empirical historical backtesting engine evaluating directional accuracy, Brier scores, and RMSE over 3m, 6m, and 1y horizons.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
