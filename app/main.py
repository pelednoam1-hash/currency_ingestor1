from datetime import datetime, timezone
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List

from app.exchangerate import fetch_rates
from app.bq import insert_rows, ensure_table

app = FastAPI(title="Currency Ingestor")

@app.get("/health")
def health():
    return {"status": "ok"}

class IngestResponse(BaseModel):
    inserted: int
    date: str
    base: str
    targets: List[str]

@app.post("/ingest", response_model=IngestResponse)
def ingest(
    base: str = Query(default="USD"),
    targets: str = Query(default="ILS,EUR,GBP")
):
    targets_list = [t.strip().upper() for t in targets.split(",") if t.strip()]
    data = fetch_rates(base, targets_list)
    ensure_table()
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        {"date": data["date"], "base": data["base"], "target": t,
         "rate": float(data["rates"][t]), "ingested_at": now}
        for t in targets_list if t in data["rates"]
    ]
    insert_rows(rows)
    return IngestResponse(inserted=len(rows), date=data["date"], base=data["base"], targets=targets_list)
