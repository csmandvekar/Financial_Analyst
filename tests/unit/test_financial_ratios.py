from datetime import datetime, timezone
from packages.agents.financials.agent import FinancialAgent, FinancialInput
from packages.contracts.financials import BalanceSheetLine, FinancialRatios, IncomeStatementLine


def test_financial_ratios_calculation():
    now = datetime.now(timezone.utc)
    income = IncomeStatementLine(
        period_end=now,
        revenue=100_000_000.0,
        gross_profit=45_000_000.0,
        operating_income=25_000_000.0,
        net_income=20_000_000.0,
    )
    bs = BalanceSheetLine(
        period_end=now,
        total_assets=200_000_000.0,
        total_liabilities=80_000_000.0,
        total_equity=120_000_000.0,
        cash_and_equivalents=40_000_000.0,
        total_debt=30_000_000.0,
    )

    gross_margin = income.gross_profit / income.revenue
    net_margin = income.net_income / income.revenue
    debt_to_equity = bs.total_debt / bs.total_equity

    assert round(gross_margin, 2) == 0.45
    assert round(net_margin, 2) == 0.20
    assert round(debt_to_equity, 2) == 0.25
