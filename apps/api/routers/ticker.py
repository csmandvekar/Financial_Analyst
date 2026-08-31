from fastapi import APIRouter, HTTPException
from packages.agents.market_data import MarketDataAgent, MarketDataInput

router = APIRouter(tags=["Ticker"])
market_agent = MarketDataAgent()


@router.get("/ticker/{symbol}", summary="Get latest cached market snapshot for a ticker")
async def get_ticker_snapshot(symbol: str):
    """
    Returns latest price, volume, market cap, and technical indicators for symbol.
    Cache-first retrieval with 15m standard TTL.
    """
    ticker = symbol.strip().upper()
    try:
        data = await market_agent.execute(MarketDataInput(ticker=ticker), persist_run=False)
        return data.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve market snapshot for '{ticker}': {str(e)}",
        )
