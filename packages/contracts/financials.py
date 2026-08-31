from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from packages.contracts.base import ContractBase


class IncomeStatementLine(BaseModel):
    period_end: datetime
    revenue: float
    gross_profit: float
    operating_income: float
    net_income: float


class BalanceSheetLine(BaseModel):
    period_end: datetime
    total_assets: float
    total_liabilities: float
    total_equity: float
    cash_and_equivalents: float
    total_debt: float


class CashFlowLine(BaseModel):
    period_end: datetime
    operating_cash_flow: float
    capex: float
    free_cash_flow: float


class FinancialRatios(BaseModel):
    current_ratio: float = Field(..., description="Current Assets / Current Liabilities")
    debt_to_equity: float = Field(..., description="Total Debt / Total Equity")
    gross_margin: float = Field(..., description="Gross Profit / Revenue")
    net_margin: float = Field(..., description="Net Income / Revenue")


class FinancialSchema(ContractBase):
    schema_version: str = "1.0.0"
    income_statements: List[IncomeStatementLine] = Field(default_factory=list, description="Most recent N periods")
    balance_sheets: List[BalanceSheetLine] = Field(default_factory=list)
    cash_flows: List[CashFlowLine] = Field(default_factory=list)
    ratios: FinancialRatios = Field(..., description="Deterministic in-agent calculated ratios")
