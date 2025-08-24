import requests
from typing import List, Dict

BASE_URL = "https://api.exchangerate.host/latest"

def fetch_rates(base: str, targets: List[str]) -> Dict:
    params = {"base": base.upper(), "symbols": ",".join(t.upper() for t in targets)}
    r = requests.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    return {"date": data.get("date"), "base": data.get("base"), "rates": data.get("rates", {})}
