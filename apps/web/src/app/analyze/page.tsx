import React, { Suspense } from "react";
import { Compass, Sparkles } from "lucide-react";
import { AnalysisConfigForm } from "@/components/analysis/AnalysisConfigForm";

function AnalyzeContent({ searchParams }: { searchParams?: { ticker?: string } }) {
  const initialTicker = searchParams?.ticker || "AAPL";

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="space-y-2 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-500 dark:text-cyan-400 border border-cyan-500/20">
          <Sparkles className="w-3.5 h-3.5" />
          Multi-Agent Pipeline Configuration
        </div>
        <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">
          Configure Financial Intelligence Run
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Select target equity ticker, primary prediction horizon, and analytical objective.
        </p>
      </div>

      <div className="p-6 md:p-8 rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
        <AnalysisConfigForm initialTicker={initialTicker} />
      </div>
    </div>
  );
}

export default function AnalyzePage({ searchParams }: { searchParams?: { ticker?: string } }) {
  return (
    <Suspense fallback={<div className="p-10 text-center text-slate-400">Loading analysis config...</div>}>
      <AnalyzeContent searchParams={searchParams} />
    </Suspense>
  );
}
