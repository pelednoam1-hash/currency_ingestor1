import os
from google.cloud import bigquery

PROJECT_ID = os.getenv("raven-data-project-467319")
DATASET = os.getenv("BQ_DATASET", "analytics")
TABLE   = os.getenv("BQ_TABLE", "exchange_rates")

SCHEMA = [
    bigquery.SchemaField("date", "DATE"),
    bigquery.SchemaField("base", "STRING"),
    bigquery.SchemaField("target", "STRING"),
    bigquery.SchemaField("rate", "FLOAT"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP"),
]

def ensure_table():
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"
    try:
        client.get_table(table_id)
    except Exception:
        table = bigquery.Table(table_id, schema=SCHEMA)
        client.create_table(table)
    return table_id

def insert_rows(rows):
    client = bigquery.Client(project=PROJECT_ID)
    table_id = ensure_table()
    errors = client.insert_rows_json(table_id, rows)
    if errors:
        # הדפס פירוט ליומן Cloud Run
        import json, sys
        print("BQ insert errors:", json.dumps(errors, ensure_ascii=False), file=sys.stderr)
        raise RuntimeError(errors)

