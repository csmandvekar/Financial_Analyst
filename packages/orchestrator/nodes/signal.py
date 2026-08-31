import logging
from typing import Any, Dict
from packages.orchestrator.state import OrchestratorState

logger = logging.getLogger(__name__)


def calculate_fundamental_signal(net_margin: float, gross_margin: float, debt_to_equity: float, current_ratio: float) -> float:
    """Calculates normalized fundamental score in [-1.0, 1.0]."""
    # Net margin component: 0.20 = good (+0.5), >0.30 = great (+1.0), <0 = bad (-1.0)
    nm_score = (net_margin - 0.12) / 0.15
    nm_score = max(-1.0, min(1.0, nm_score))

    # Gross margin component
    gm_score = (gross_margin - 0.35) / 0.25
    gm_score = max(-1.0, min(1.0, gm_score))

    # Debt to equity component: lower is better (<0.5 is +1.0, >2.0 is -1.0)
    de_score = (1.2 - debt_to_equity) / 1.0
    de_score = max(-1.0, min(1.0, de_score))

    # Liquidity component: >1.5 is good
    liq_score = (current_ratio - 1.2) / 0.8
    liq_score = max(-1.0, min(1.0, liq_score))

    fund_score = nm_score * 0.40 + gm_score * 0.20 + de_score * 0.25 + liq_score * 0.15
    return float(round(max(-1.0, min(1.0, fund_score)), 3))


def calculate_market_signal(current_price: float, sma_20: float, sma_50: float, rsi_14: float) -> float:
    """Calculates normalized technical market momentum in [-1.0, 1.0]."""
    # Trend relative to moving averages
    trend_20 = (current_price - sma_20) / max(0.01, sma_20)
    trend_50 = (current_price - sma_50) / max(0.01, sma_50)
    ma_score = (trend_20 * 0.6 + trend_50 * 0.4) * 10.0  # +5% above MA translates to +0.5
    ma_score = max(-1.0, min(1.0, ma_score))

    # RSI momentum (RSI 50 is neutral 0.0, 70 is +0.67, 30 is -0.67)
    rsi_score = (rsi_14 - 50.0) / 30.0
    rsi_score = max(-1.0, min(1.0, rsi_score))

    market_score = ma_score * 0.65 + rsi_score * 0.35
    return float(round(max(-1.0, min(1.0, market_score)), 3))


async def signal_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Signal Generation Node:
    Fuses upstream agent outputs into 4 normalized signals [-1.0, 1.0].
    """
    market = state["market_data"]
    fin = state["financials"]
    news = state["news"]
    sent = state["sentiment"]
    sec = state["sector"]

    # 1. Fundamental Signal
    fund_sig = calculate_fundamental_signal(
        net_margin=fin.ratios.net_margin,
        gross_margin=fin.ratios.gross_margin,
        debt_to_equity=fin.ratios.debt_to_equity,
        current_ratio=fin.ratios.current_ratio,
    )

    # 2. Sentiment Signal (weighted between social mentions and news lean)
    sent_sig = sent.aggregate_sentiment * 0.65 + news.sentiment_lean * 0.35
    sent_sig = float(round(max(-1.0, min(1.0, sent_sig)), 3))

    # 3. Sector Signal (relative alpha and sector trend)
    rel_perf = sec.relative_performance  # in percentage points
    sec_trend = sec.sector_price_change_30d
    sec_sig = (rel_perf / 5.0) * 0.7 + (sec_trend / 8.0) * 0.3
    sec_sig = float(round(max(-1.0, min(1.0, sec_sig)), 3))

    # 4. Market Technical Signal
    mkt_sig = calculate_market_signal(
        current_price=market.current_price,
        sma_20=market.indicators.sma_20,
        sma_50=market.indicators.sma_50,
        rsi_14=market.indicators.rsi_14,
    )

    logger.info(
        "Signal Generation for %s: Fundamental=%.2f, Sentiment=%.2f, Sector=%.2f, Market=%.2f",
        state["ticker"],
        fund_sig,
        sent_sig,
        sec_sig,
        mkt_sig,
    )

    return {
        "fundamental_signal": fund_sig,
        "sentiment_signal": sent_sig,
        "sector_signal": sec_sig,
        "market_signal": mkt_sig,
    }
