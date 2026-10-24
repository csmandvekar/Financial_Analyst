export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface HorizonForecastData {
  horizon: "3m" | "6m" | "1y";
  bull_prob: number;
  bear_prob: number;
  neutral_prob: number;
  expected_vol: number;
  price_range_low: number;
  price_range_high: number;
  confidence: number;
}

export interface ReasoningFactorData {
  factor_name: string;
  signal_value: number;
  weight: number;
  contribution_summary: string;
}

export interface AgentContributionData {
  agent_name: string;
  version: string;
  status: string;
  latency_ms: number;
  summary: string;
}

export interface ReportData {
  id?: string;
  job_id?: string;
  ticker: string;
  version: string;
  as_of?: string;
  executive_summary: string;
  bull_case: string;
  bear_case: string;
  confidence: number;
  horizons: HorizonForecastData[];
  reasoning_factors: ReasoningFactorData[];
  agent_contributions: AgentContributionData[];
  citations: string[];
  degraded_sources: string[];
  data_freshness_seconds?: Record<string, number>;
}

export interface AnalysisSubmissionResponse {
  job_id: string;
  ticker: string;
  status: "completed" | "degraded" | "failed" | "pending";
  report?: ReportData;
}

export interface AgentRunData {
  id: string;
  agent_name: string;
  agent_version: string;
  status: "success" | "degraded" | "failed" | "running";
  started_at: string;
  finished_at: string | null;
  duration_ms: number | null;
  error: string | null;
  input_hash: string | null;
}

export interface JobTraceResponse {
  job_id: string;
  ticker: string;
  status: string;
  degraded_sources: string[];
  agent_runs: AgentRunData[];
}

export interface TickerSnapshotData {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap?: number;
  pe_ratio?: number;
  as_of?: string;
}

export interface EvaluationMetricsResponse {
  sample_size: number;
  horizon_filter: string;
  metrics: {
    directional_accuracy: number;
    brier_calibration_score: number;
    price_mae: number;
    price_rmse: number;
    interval_coverage: number;
  };
}

export interface EvaluationOutcomeItem {
  id: string;
  ticker: string;
  horizon: string;
  prediction_date: string;
  predicted_direction: string;
  actual_direction: string;
  is_direction_correct: boolean;
  predicted_price_low: number;
  predicted_price_high: number;
  actual_price: number;
  price_error_abs: number;
  evaluated_at: string;
}

/**
 * Normalizes backend API response variations (nested payload vs top-level fields,
 * confidence_score vs confidence, bull_probability vs bull_prob, agent_version vs version)
 * into a single consistent flat ReportData object for the UI components.
 */
export function normalizeReportData(raw: any): ReportData {
  if (!raw) {
    return {
      ticker: "UNKNOWN",
      version: "1.0.0",
      executive_summary: "",
      bull_case: "",
      bear_case: "",
      confidence: 0.85,
      horizons: [],
      reasoning_factors: [],
      agent_contributions: [],
      citations: [],
      degraded_sources: [],
    };
  }

  const payload = raw.payload || raw;

  // 1. Horizons normalization
  const rawHorizons =
    payload.forecast?.horizons ||
    raw.forecast?.horizons ||
    payload.horizons ||
    raw.horizons ||
    [];

  const normalizedHorizons: HorizonForecastData[] = rawHorizons.map((h: any) => ({
    horizon: h.horizon || "3m",
    bull_prob: h.bull_probability ?? h.bull_prob ?? 0.33,
    bear_prob: h.bear_probability ?? h.bear_prob ?? 0.33,
    neutral_prob: h.neutral_probability ?? h.neutral_prob ?? 0.34,
    expected_vol: h.expected_volatility ?? h.expected_vol ?? 0.2,
    price_range_low: h.expected_price_low ?? h.price_range_low ?? 0,
    price_range_high: h.expected_price_high ?? h.price_range_high ?? 0,
    confidence: h.confidence ?? raw.confidence_score ?? raw.confidence ?? 0.85,
  }));

  // 2. Reasoning Factors normalization
  const rawFactors = payload.reasoning_factors || raw.reasoning_factors || [];
  const normalizedFactors: ReasoningFactorData[] = rawFactors.map((rf: any) => ({
    factor_name: rf.factor || rf.factor_name || "Factor Analysis",
    signal_value:
      rf.signal_value ??
      (rf.direction === "bullish" ? 0.65 : rf.direction === "bearish" ? -0.65 : 0.0),
    weight: rf.weight ?? 0.25,
    contribution_summary:
      rf.contribution_summary ||
      `${(rf.direction || "neutral").toUpperCase()} signal weighting ${(
        (rf.weight ?? 0.25) * 100
      ).toFixed(0)}% of model.`,
  }));

  // 3. Agent Contributions normalization
  const rawContributions = payload.agent_contributions || raw.agent_contributions || [];
  const normalizedContributions: AgentContributionData[] = rawContributions.map((ac: any) => ({
    agent_name: ac.agent_name || "Agent",
    version: ac.agent_version || ac.version || "1.0.0",
    status: ac.status || "success",
    latency_ms: ac.latency_ms ?? 0,
    summary:
      ac.summary ||
      `Status: ${ac.status || "success"} (v${ac.agent_version || ac.version || "1.0.0"})`,
  }));

  // 4. Extract Confidence
  const confidenceScore =
    raw.confidence_score !== undefined
      ? raw.confidence_score
      : raw.confidence !== undefined
      ? raw.confidence
      : payload.confidence_score !== undefined
      ? payload.confidence_score
      : payload.confidence !== undefined
      ? payload.confidence
      : 0.85;

  return {
    id: raw.id || payload.id,
    job_id: raw.job_id || payload.job_id,
    ticker: raw.ticker || payload.ticker || "UNKNOWN",
    version: raw.version || payload.schema_version || payload.version || "1.0.0",
    as_of:
      raw.created_at ||
      payload.generated_at ||
      payload.as_of ||
      raw.as_of ||
      new Date().toISOString(),
    executive_summary:
      payload.executive_summary ||
      raw.executive_summary ||
      "No executive summary provided for this analysis.",
    bull_case:
      payload.bull_case ||
      raw.bull_case ||
      "No bull case catalysts provided for this analysis.",
    bear_case:
      payload.bear_case ||
      raw.bear_case ||
      "No bear case risks provided for this analysis.",
    confidence: confidenceScore,
    horizons: normalizedHorizons,
    reasoning_factors: normalizedFactors,
    agent_contributions: normalizedContributions,
    citations: payload.citations || raw.citations || [],
    degraded_sources: payload.degraded_sources || raw.degraded_sources || [],
    data_freshness_seconds: payload.data_freshness || raw.data_freshness || {},
  };
}

export async function submitAnalysis(
  ticker: string,
  analysisType: string = "quarterly_outlook"
): Promise<AnalysisSubmissionResponse> {
  const res = await fetch(`${API_BASE}/analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker: ticker.toUpperCase(), analysis_type: analysisType }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to submit analysis" }));
    throw new Error(err.detail || "Analysis request failed");
  }
  const data = await res.json();
  if (data.report) {
    data.report = normalizeReportData(data.report);
  }
  return data;
}

export async function getJobStatus(jobId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/analysis/${jobId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Job not found");
  const data = await res.json();
  if (data.report) {
    data.report = normalizeReportData(data.report);
  }
  return data;
}

export async function getJobTrace(jobId: string): Promise<JobTraceResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Trace logs not found");
  return res.json();
}

export async function getReport(reportId: string): Promise<ReportData> {
  const res = await fetch(`${API_BASE}/reports/${reportId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Report not found");
  const raw = await res.json();
  return normalizeReportData(raw);
}

export async function getTickerSnapshot(symbol: string): Promise<TickerSnapshotData> {
  const res = await fetch(`${API_BASE}/ticker/${symbol}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Ticker snapshot failed");
  return res.json();
}

export async function getEvaluationMetrics(horizon?: string): Promise<EvaluationMetricsResponse> {
  const url = horizon
    ? `${API_BASE}/evaluation/metrics?horizon=${horizon}`
    : `${API_BASE}/evaluation/metrics`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load evaluation metrics");
  return res.json();
}

export async function getEvaluationOutcomes(limit: number = 20): Promise<EvaluationOutcomeItem[]> {
  const res = await fetch(`${API_BASE}/evaluation/outcomes?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load evaluation outcomes");
  return res.json();
}

export async function triggerBacktest(
  tickers: string[] = ["AAPL", "MSFT", "NVDA"],
  lookbackDays: number = 180,
  horizon: string = "3m"
): Promise<any> {
  const res = await fetch(`${API_BASE}/evaluation/backtest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tickers, lookback_days: lookbackDays, horizon }),
  });
  if (!res.ok) throw new Error("Backtest failed");
  return res.json();
}

export async function getHealthStatus(): Promise<{ status: string; database: string; redis: string }> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    if (!res.ok) return { status: "degraded", database: "disconnected", redis: "disconnected" };
    return res.json();
  } catch {
    return { status: "offline", database: "offline", redis: "offline" };
  }
}
