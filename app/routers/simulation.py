import hashlib
import uuid as uuid_lib
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
import yfinance as yf

from app.simulation.data_fetcher import fetch_historical_data, fetch_live_price, fetch_data
from app.simulation.lump_sum import LumpSumSimulator
from app.simulation.dca import simulate_dca
from app.simulation.commentary import get_commentary

router = APIRouter()


# -----------------------------------------------
# Helpers
# -----------------------------------------------

def _make_result_id(ticker: str, start_date: str, amount: float, sim_type: str) -> str:
    """Deterministic result_id so the same simulation always gets the same ID."""
    raw = f"{ticker}|{start_date}|{amount}|{sim_type}"
    return "res_" + hashlib.sha256(raw.encode()).hexdigest()[:16]


# -----------------------------------------------
# Request Models
# -----------------------------------------------

class LumpSumRequest(BaseModel):
    ticker: str
    start_date: str
    amount: float

    @field_validator("ticker")
    @classmethod
    def sanitise_ticker(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("Ticker cannot be empty")
        if len(v) > 15:
            raise ValueError("Ticker too long (max 15 characters)")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v < 1:
            raise ValueError("Amount must be at least $1")
        if v > 10_000_000:
            raise ValueError("Amount cannot exceed $10,000,000")
        return v


class DCARequest(BaseModel):
    ticker: str
    start_date: str
    monthly_investment: float

    @field_validator("ticker")
    @classmethod
    def sanitise_ticker(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("Ticker cannot be empty")
        if len(v) > 15:
            raise ValueError("Ticker too long (max 15 characters)")
        return v

    @field_validator("monthly_investment")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v < 1:
            raise ValueError("Monthly investment must be at least $1")
        if v > 1_000_000:
            raise ValueError("Monthly investment cannot exceed $1,000,000")
        return v


# -----------------------------------------------
# Ticker Validation Endpoint
# -----------------------------------------------

@router.get("/validate-ticker")
def validate_ticker(ticker: str = Query(..., description="Yahoo Finance ticker symbol")):
    """
    Lightweight check: confirms that a ticker resolves in yfinance
    before running a full (expensive) simulation.
    """
    try:
        t = ticker.strip().upper()
        asset = yf.Ticker(t)
        df = asset.history(period="5d")
        if df.empty:
            return {"valid": False, "ticker": t, "message": f"No data found for '{t}'"}
        return {"valid": True, "ticker": t, "message": "Ticker is valid"}
    except Exception as e:
        return {"valid": False, "ticker": ticker, "message": str(e)}


# -----------------------------------------------
# Lump Sum Endpoint
# -----------------------------------------------

@router.post("/simulate/lump-sum")
def simulate_lump_sum(request: LumpSumRequest):
    print("Received amount:", request.amount)
    try:
        data = fetch_historical_data(request.ticker, request.start_date)
        live_price = fetch_live_price(request.ticker)

        sim = LumpSumSimulator(
            ticker=request.ticker,
            start_date=request.start_date,
            price_data=data,
            live_price=live_price,
            initial_amount=request.amount
        )
        result = sim.run()

        growth_pct = result["growth_percentage"]
        commentary = get_commentary(growth_pct, request.ticker, request.start_date)
        result_id = _make_result_id(request.ticker, request.start_date, request.amount, "lump_sum")

        return {
            **result,
            "result_id": result_id,
            "commentary": commentary,
            "sim_type": "lump_sum",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------
# DCA Endpoint — normalized response shape
# -----------------------------------------------

@router.post("/simulate/dca")
def simulate_dca_api(request: DCARequest):
    try:
        data = fetch_data(request.ticker, request.start_date)

        df = simulate_dca(data, request.monthly_investment)

        # Build chart_data from the DataFrame
        chart_data = []
        for date, row in df.iterrows():
            chart_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": round(float(row["portfolio"]), 2)
            })

        if not chart_data:
            raise ValueError("No simulation data produced — check the ticker and start date.")

        final_portfolio = chart_data[-1]["value"]
        final_invested = round(float(df.iloc[-1]["invested"]), 2)
        difference = round(final_portfolio - final_invested, 2)
        growth_pct = round(((difference / final_invested) * 100) if final_invested > 0 else 0.0, 2)

        commentary = get_commentary(growth_pct, request.ticker, request.start_date)
        result_id = _make_result_id(request.ticker, request.start_date, request.monthly_investment, "dca")

        return {
            "result_id": result_id,
            "alternate_value": final_portfolio,
            "real_value": final_invested,
            "difference": difference,
            "growth_percentage": growth_pct,
            "chart_data": chart_data,
            "commentary": commentary,
            "sim_type": "dca",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))