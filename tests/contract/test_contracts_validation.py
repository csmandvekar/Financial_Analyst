from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError
from packages.contracts.base import ContractBase, DataProvenance, SourceReliability
from packages.contracts.forecast import ForecastSchema, HorizonForecast, SignalBreakdown
from packages.contracts.market_data import MarketDataSchema, TechnicalIndicators


def test_data_provenance_validation():
    now = datetime.now(timezone.utc)
    prov = DataProvenance(
        source="sec_edgar",
        reliability=SourceReliability.HIGH,
        fetched_at=now,
    )
    assert prov.source == "sec_edgar"
    assert prov.is_degraded is False

    # Datetime in the future (>60s) should fail validation
    future_time = now + timedelta(days=2)
    with pytest.raises(ValidationError):
        DataProvenance(
            source="sec_edgar",
            reliability=SourceReliability.HIGH,
            fetched_at=future_time,
        )


def test_market_data_schema_validation():
    now = datetime.now(timezone.utc)
    prov = [
        DataProvenance(
            source="yfinance",
            reliability=SourceReliability.HIGH,
            fetched_at=now,
        )
    ]

    schema = MarketDataSchema(
        schema_version="1.0.0",
        ticker="aapl",
        generated_at=now,
        confidence=0.95,
        provenance=prov,
        current_price=180.5,
        volume=50000000,
        market_cap=2800000000000.0,
        fifty_two_week_high=199.0,
        fifty_two_week_low=165.0,
        indicators=TechnicalIndicators(
            sma_20=178.0,
            sma_50=175.0,
            rsi_14=62.5,
            volatility_30d=0.20,
        ),
    )
    # Check ticker was normalized to uppercase
    assert schema.ticker == "AAPL"

    # Low > High should fail
    with pytest.raises(ValidationError):
        MarketDataSchema(
            schema_version="1.0.0",
            ticker="AAPL",
            generated_at=now,
            confidence=0.95,
            provenance=prov,
            current_price=180.5,
            volume=50000000,
            market_cap=2800000000000.0,
            fifty_two_week_high=150.0,
            fifty_two_week_low=190.0,
            indicators=TechnicalIndicators(
                sma_20=178.0,
                sma_50=175.0,
                rsi_14=62.5,
                volatility_30d=0.20,
            ),
        )


def test_forecast_probabilities_sum():
    now = datetime.now(timezone.utc)
    prov = [
        DataProvenance(
            source="ensemble_engine",
            reliability=SourceReliability.HIGH,
            fetched_at=now,
        )
    ]

    # Valid sum = 1.0
    h_valid = HorizonForecast(
        horizon="3m",
        bull_probability=0.45,
        bear_probability=0.25,
        neutral_probability=0.30,
        expected_volatility=0.18,
        expected_price_low=140.0,
        expected_price_high=190.0,
        confidence=0.85,
    )
    assert h_valid.bull_probability == 0.45

    # Invalid probability sum (e.g. 0.8 + 0.5 = 1.3) should fail
    with pytest.raises(ValidationError):
        HorizonForecast(
            horizon="3m",
            bull_probability=0.80,
            bear_probability=0.50,
            neutral_probability=0.30,
            expected_volatility=0.18,
            expected_price_low=140.0,
            expected_price_high=190.0,
            confidence=0.85,
        )
