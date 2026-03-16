from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

from services import fetch_receipt_data, process_receipts, EMPRESAS_CONFIG

app = FastAPI(title="Receipt Report API", version="2.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/api/companies")
async def get_companies():
    """Returns the list of configured companies."""
    return [
        {"id": k, **v} for k, v in EMPRESAS_CONFIG.items()
    ]

@app.get("/api/receipts")
async def get_receipts(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    company_id: str = Query(..., description="Company ID (ML, VALLE, etc.)")
):
    """
    Fetches and processes receipt data for a given company and date range.
    """
    try:
        # Validate and convert dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    df = fetch_receipt_data(start_dt, end_dt, company_id)
    
    if df is None:
        raise HTTPException(status_code=500, detail="Error fetching data from database")
        
    if df.empty:
        return {
            "chart_data": [],
            "stats": {"total": 0, "average": 0, "count": 0, "max": 0},
            "records": []
        }
    
    chart_data, stats, records = process_receipts(df)
    
    return {
        "chart_data": chart_data,
        "stats": stats,
        "records": records
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
