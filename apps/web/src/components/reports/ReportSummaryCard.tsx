import React from "react";
import Link from "next/link";
import {
  Activity,
  AlertCircle,
  Award,
  CheckCircle2,
  Clock,
  Compass,
  FileText,
  Layers,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { ReportData } from "@/lib/api";
import { formatDate, formatPercent, getDirectionBadgeStyle } from "@/lib/utils";

interface ReportSummaryCardProps {
  report: ReportData;
  jobId?: string;
}

export function ReportSummaryCard({ report, jobId }: ReportSummaryCardProps) {
  const primaryHorizon = report.horizons?.[0];
  const primaryDirection =
    primaryHorizon?.bull_prob > (primaryHorizon?.bear_prob || 0)
      ? "bullish"
      : (primaryHorizon?.bear_prob || 0) > (primaryHorizon?.bull_prob || 0)
      ? "bearish"
      : "neutral";

  const badgeStyle = getDirectionBadgeStyle(primaryDirection);

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
      {/* Header Banner */}
      <div className="p-6 md:p-8 border-b border-slate-100 dark:border-slate-800/80 bg-gradient-to-r from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                {report.ticker}
              </h1>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${badgeStyle.bg}`}>
                {badgeStyle.label} OUTLOOK
              </span>
              {report.degraded_sources?.length > 0 && (
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-500 border border-amber-500/30 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> DEGRADED
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2">
              <span>Report Schema v{report.version}</span> &bull;
              <span>Generated: {formatDate(report.as_of || new Date())}</span>
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Confidence Score Pill */}
            <div className="text-right">
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Confidence Calibration</div>
              <div className="text-2xl font-black text-slate-900 dark:text-white flex items-center justify-end gap-1.5 mt-0.5">
                <span className="text-cyan-500">{formatPercent(report.confidence)}</span>
              </div>
            </div>

            {jobId && (
              <Link
                href={`/jobs/${jobId}/trace`}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 transition-colors flex items-center gap-1.5"
              >
                <Activity className="w-3.5 h-3.5 text-cyan-500" />
                View Execution Trace
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Executive Summary Body */}
      <div className="p-6 md:p-8 space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
          <FileText className="w-4 h-4 text-cyan-500" />
          Executive Synthesis Thesis
        </div>
        <p className="text-slate-700 dark:text-slate-200 text-sm md:text-base leading-relaxed font-normal">
          {report.executive_summary}
        </p>
      </div>
    </div>
  );
}
