"use client";

import React, { useState } from "react";
import { Check, ChevronDown, Search, Sparkles, TrendingUp } from "lucide-react";

export interface TickerOption {
  symbol: string;
  name: string;
  sector: string;
}

export const POPULAR_TICKERS: TickerOption[] = [
  { symbol: "AAPL", name: "Apple Inc.", sector: "Consumer Tech" },
  { symbol: "MSFT", name: "Microsoft Corp.", sector: "Cloud / Software" },
  { symbol: "NVDA", name: "NVIDIA Corporation", sector: "Semiconductors" },
  { symbol: "GOOGL", name: "Alphabet Inc.", sector: "Internet / AI" },
  { symbol: "AMZN", name: "Amazon.com Inc.", sector: "E-Commerce / Cloud" },
  { symbol: "META", name: "Meta Platforms", sector: "Social Media / AI" },
  { symbol: "TSLA", name: "Tesla Inc.", sector: "Automotive / CleanTech" },
  { symbol: "JPM", name: "JPMorgan Chase & Co.", sector: "Financials" },
  { symbol: "LLY", name: "Eli Lilly and Co.", sector: "Healthcare / Biotech" },
];

interface TickerSearchInputProps {
  value: string;
  onChange: (symbol: string) => void;
}

export function TickerSearchInput({ value, onChange }: TickerSearchInputProps) {
  const [query, setQuery] = useState(value);
  const [isOpen, setIsOpen] = useState(false);

  const filtered = POPULAR_TICKERS.filter(
    (t) =>
      t.symbol.toLowerCase().includes(query.toLowerCase()) ||
      t.name.toLowerCase().includes(query.toLowerCase()) ||
      t.sector.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (symbol: string) => {
    setQuery(symbol);
    onChange(symbol);
    setIsOpen(false);
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1.5 uppercase tracking-wider">
          Target Equity Ticker
        </label>
        <div className="relative">
          <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={query}
            onFocus={() => setIsOpen(true)}
            onChange={(e) => {
              const val = e.target.value.toUpperCase();
              setQuery(val);
              onChange(val);
              setIsOpen(true);
            }}
            placeholder="Type symbol or company name (e.g. NVDA)"
            className="w-full pl-11 pr-10 py-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 font-semibold text-base focus:outline-none focus:ring-2 focus:ring-cyan-500/50 shadow-sm"
          />
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery("");
                onChange("");
              }}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-xs font-semibold text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800"
            >
              CLEAR
            </button>
          )}
        </div>

        {/* Dropdown Suggestions */}
        {isOpen && filtered.length > 0 && (
          <div className="absolute z-20 mt-1.5 w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl overflow-hidden divide-y divide-slate-100 dark:divide-slate-800/60 max-h-60 overflow-y-auto">
            {filtered.map((t) => (
              <button
                key={t.symbol}
                type="button"
                onClick={() => handleSelect(t.symbol)}
                className={`w-full px-4 py-3 text-left flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800/80 transition-colors ${
                  value === t.symbol ? "bg-cyan-50 dark:bg-cyan-950/40 text-cyan-600 dark:text-cyan-400" : ""
                }`}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-slate-900 dark:text-white">{t.symbol}</span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">{t.name}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 dark:text-slate-500">{t.sector}</span>
                </div>
                {value === t.symbol && <Check className="w-4 h-4 text-cyan-500" />}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Quick Select Badges */}
      <div>
        <span className="text-[11px] font-medium text-slate-400 dark:text-slate-500 mr-2">Popular:</span>
        <div className="inline-flex flex-wrap gap-1.5 mt-1">
          {POPULAR_TICKERS.slice(0, 6).map((t) => (
            <button
              key={t.symbol}
              type="button"
              onClick={() => handleSelect(t.symbol)}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all ${
                value === t.symbol
                  ? "bg-cyan-500/10 border-cyan-500 text-cyan-500 dark:text-cyan-400"
                  : "bg-white dark:bg-slate-900/90 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700"
              }`}
            >
              {t.symbol}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
