"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Activity,
  ArrowLeft,
  Calendar,
  CheckCircle2,
  Clock,
  Compass,
  Cpu,
  FileCheck2,
  FileText,
  Layers,
  Loader2,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { BullBearPanel } from "@/components/reports/BullBearPanel";
import { EvidenceSourceList } from "@/components/reports/EvidenceSourceList";
import { ForecastChart } from "@/components/reports/ForecastChart";
import { ReasoningFactorsList } from "@/components/reports/ReasoningFactorsList";
import { ReportSummaryCard } from "@/components/reports/ReportSummaryCard";
import { getReport, ReportData } from "@/lib/api";

export default function ReportViewerPage() {
  const params = useParams();
  const reportId = params?.id as string;

  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!reportId) return;

    getReport(reportId)
      .then((data) => {
        setReport(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load report document");
        setLoading(false);
      });
  }, [reportId]);

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

        <div className="flex items-center gap-3">
          <Link
            href={`/tickers/${report?.ticker || "AAPL"}/history`}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:underline"
          >
            <Activity className="w-3.5 h-3.5" />
            Historical Calibration Log
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="p-16 flex flex-col items-center justify-center space-y-3 text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
          <p className="text-sm font-medium">Retrieving synthesized multi-agent report...</p>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-500 text-xs font-medium">
          {error}
        </div>
      ) : report ? (
        <div className="space-y-8">
          {/* 1. Header & Summary Card */}
          <ReportSummaryCard report={report} jobId={reportId} />

          {/* 2. Bull vs Bear Argument Panel */}
          <BullBearPanel bullCase={report.bull_case} bearCase={report.bear_case} />

          {/* 3. Multi-Horizon Forecast Visualizer */}
          <ForecastChart horizons={report.horizons} />

          {/* 4. Multi-Factor Signal Decomposition */}
          <ReasoningFactorsList factors={report.reasoning_factors} />

          {/* 5. Agent Contributions Audit */}
          {report.agent_contributions && report.agent_contributions.length > 0 && (
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 md:p-8 space-y-4 shadow-sm">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 dark:border-slate-800/80 pb-4">
                <Cpu className="w-4 h-4 text-cyan-500" />
                Agent Contribution & Traceability Log
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {report.agent_contributions.map((agent) => (
                  <div
                    key={agent.agent_name}
                    className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900 dark:text-white capitalize">
                        {agent.agent_name.replace("_", " ")}
                      </span>
                      <span className="text-[10px] font-mono text-cyan-500">v{agent.version}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                      <span
                        className={`inline-block w-2 h-2 rounded-full ${
                          agent.status === "success"
                            ? "bg-emerald-500"
                            : agent.status === "degraded"
                            ? "bg-amber-500"
                            : "bg-rose-500"
                        }`}
                      />
                      <span>Status: <strong className="capitalize text-slate-700 dark:text-slate-300">{agent.status}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 6. Upstream Citations & Data Reliability */}
          <EvidenceSourceList
            citations={report.citations || []}
            degradedSources={report.degraded_sources || []}
          />
        </div>
      ) : null}
    </div>
  );
}
