from google.api_core.exceptions import NotFound, BadRequest
import json, sys

def ensure_table():
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"
    try:
        client.get_table(table_id)  # קיימת? מצוין.
        return table_id
    except NotFound:
        # רק אם באמת לא קיימת – ליצור
        table = bigquery.Table(table_id, schema=SCHEMA)
        try:
            client.create_table(table)
            print(f"BQ ensure_table: created {table_id}", file=sys.stderr)
            return table_id
        except BadRequest as e:
            print(f"BQ ensure_table BadRequest for {table_id}: {e}", file=sys.stderr)
            raise
    except Exception as e:
        print(f"BQ ensure_table unexpected error for {table_id}: {repr(e)}", file=sys.stderr)
        raise

def insert_rows(rows):
    client = bigquery.Client(project=PROJECT_ID)
    table_id = ensure_table()
    if not rows:
        return []  # אין מה להכניס
    try:
        errors = client.insert_rows_json(table_id, rows)
        if errors:
            print("BQ insert errors:", json.dumps(errors, ensure_ascii=False), file=sys.stderr)
            raise RuntimeError(errors)
        return []
    except BadRequest as e:
        print(f"BQ insert BadRequest: {e}", file=sys.stderr)
        raise


