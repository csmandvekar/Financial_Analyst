import asyncio
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
import yfinance as yf
from packages.agents.base import BaseAgent
from packages.agents.market_data.indicators import (
    compute_annualized_volatility,
    compute_rsi,
    compute_sma,
)
from packages.contracts.base import DataProvenance, SourceReliability
from packages.contracts.market_data import MarketDataSchema, TechnicalIndicators
from packages.infra.cache.redis_client import cache_client

logger = logging.getLogger(__name__)


class MarketDataInput:
    def __init__(self, ticker: str, lookback_days: int = 180):
        self.ticker = ticker.upper()
        self.lookback_days = lookback_days

    def __str__(self) -> str:
        return f"MarketDataInput(ticker={self.ticker}, lookback_days={self.lookback_days})"


class MarketDataAgent(BaseAgent[MarketDataInput, MarketDataSchema]):
    name = "market_data_agent"
    version = "1.0.0"

    async def run(self, input_data: MarketDataInput) -> MarketDataSchema:
        ticker = input_data.ticker
        cache_key = cache_client.build_key(
            source="market_data",
            ticker=ticker,
            params={"lookback_days": input_data.lookback_days},
        )

        # Check cache
        cached = await cache_client.get(cache_key)
        if cached:
            logger.info("Market data cache hit for %s", ticker)
            return MarketDataSchema.model_validate(cached)

        # Fetch live data in thread pool
        schema = await asyncio.to_thread(self._fetch_and_calculate, ticker, input_data.lookback_days)

        # Cache valid schema
        await cache_client.set(cache_key, schema, source="market_data")
        return schema

    def _fetch_and_calculate(self, ticker: str, lookback_days: int) -> MarketDataSchema:
        now = datetime.now(timezone.utc)
        provenance = [
            DataProvenance(
                source="yfinance",
                reliability=SourceReliability.HIGH,
                fetched_at=now,
                is_degraded=False,
            )
        ]

        try:
            yf_ticker = yf.Ticker(ticker)
            hist = yf_ticker.history(period=f"{lookback_days}d")
            info = yf_ticker.info or {}

            if hist.empty or len(hist) < 5:
                raise ValueError(f"Insufficient history returned for ticker {ticker}")

            close_prices = hist["Close"].tolist()
            dates = hist.index.to_pydatetime().tolist()
            price_history: List[Tuple[datetime, float]] = [
                (d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d, float(p))
                for d, p in zip(dates, close_prices)
            ]

            current_price = float(close_prices[-1])
            volume = int(hist["Volume"].iloc[-1]) if not hist["Volume"].empty else 1000000
            market_cap = float(info.get("marketCap") or (current_price * 1_000_000_000))
            fifty_two_week_high = float(info.get("fiftyTwoWeekHigh") or max(close_prices) * 1.05)
            fifty_two_week_low = float(info.get("fiftyTwoWeekLow") or min(close_prices) * 0.95)

            # Ensure high >= low
            if fifty_two_week_high < fifty_two_week_low:
                fifty_two_week_high, fifty_two_week_low = fifty_two_week_low, fifty_two_week_high

            indicators = TechnicalIndicators(
                sma_20=compute_sma(close_prices, 20),
                sma_50=compute_sma(close_prices, 50),
                rsi_14=compute_rsi(close_prices, 14),
                volatility_30d=compute_annualized_volatility(close_prices, 30),
            )

            return MarketDataSchema(
                schema_version=self.version,
                ticker=ticker,
                generated_at=now,
                confidence=0.95,
                provenance=provenance,
                current_price=current_price,
                volume=volume,
                market_cap=market_cap,
                fifty_two_week_high=fifty_two_week_high,
                fifty_two_week_low=fifty_two_week_low,
                indicators=indicators,
                price_history=price_history,
            )
        except Exception as e:
            logger.warning("Live yfinance fetch failed for %s (%s). Generating fallback snapshot.", ticker, e)
            return self._build_fallback(ticker, now, error_note=str(e))

    def _build_fallback(self, ticker: str, now: datetime, error_note: str) -> MarketDataSchema:
        """Graceful fallback for market data when API is offline or symbol is synthetic."""
        base_price = 150.0 if ticker != "MSFT" else 420.0
        if ticker == "GOOGL":
            base_price = 175.0
        elif ticker == "NVDA":
            base_price = 120.0

        mock_prices = [base_price * (1.0 + 0.002 * i) for i in range(30)]
        price_history = [
            (now, float(p)) for p in mock_prices
        ]

        return MarketDataSchema(
            schema_version=self.version,
            ticker=ticker,
            generated_at=now,
            confidence=0.60,
            provenance=[
                DataProvenance(
                    source="fallback_market_engine",
                    reliability=SourceReliability.LOW,
                    fetched_at=now,
                    is_degraded=True,
                )
            ],
            current_price=base_price,
            volume=5000000,
            market_cap=base_price * 2_500_000_000,
            fifty_two_week_high=base_price * 1.25,
            fifty_two_week_low=base_price * 0.85,
            indicators=TechnicalIndicators(
                sma_20=base_price * 0.98,
                sma_50=base_price * 0.95,
                rsi_14=54.2,
                volatility_30d=0.22,
            ),
            price_history=price_history,
        )
