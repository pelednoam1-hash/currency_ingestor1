from datetime import datetime, timezone
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List

from app.exchangerate import fetch_rates
from app.bq import insert_rows, ensure_table

from fastapi.responses import JSONResponse
from app.bq import test_insert_one

@app.post("/test_bq")
def test_bq():
    try:
        errors = test_insert_one()
        # אם רשימת errors ריקה – זה אומר שההכנסה הצליחה
        return {"ok": True, "errors": errors}
    except Exception as e:
        # נחזיר 500 עם הודעה, וגם זה יופיע בלוגים
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


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
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )

    
