from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.simulation.data_fetcher import fetch_data
from app.simulation.lump_sum import LumpSumSimulator
from app.simulation.dca import simulate_dca

router = APIRouter()


# -------------------------------
# Request Models
# -------------------------------

class LumpSumRequest(BaseModel):
    ticker: str
    start_date: str
    amount: float


class DCARequest(BaseModel):
    ticker: str
    start_date: str
    monthly_investment: float


# -------------------------------
# Lump Sum Endpoint
# -------------------------------

@router.post("/simulate/lump-sum")
def simulate_lump_sum(request: LumpSumRequest):
    try:
        data = fetch_data(request.ticker, request.start_date)

        sim = LumpSumSimulator(data, request.amount)
        result = sim.run()

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------------
# DCA Endpoint
# -------------------------------

@router.post("/simulate/dca")
def simulate_dca_api(request: DCARequest):
    try:
        data = fetch_data(request.ticker, request.start_date)

        df = simulate_dca(data, request.monthly_investment)

        # Convert DataFrame → JSON
        result = df.reset_index().to_dict(orient="records")

        return {
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))