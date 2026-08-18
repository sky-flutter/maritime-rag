import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
from app.repository.config import POSTGRES_CONFIG

from app.repository.postgres.conn_manager import PostgresConnectionManager
from app.repository.postgres.orm_models import ReportDocumentORM

load_dotenv()

DATA_DIR = Path("data/raw")
BATCH_SIZE = 500


def load_csv_files() -> pd.DataFrame:
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

    frames = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(frames, ignore_index=True)
    print(f"Loaded {len(df)} rows from {len(csv_files)} file(s)")
    return df


def row_to_dict(row: pd.Series) -> dict:
    report_json = row["REPORT_JSON"]
    # REPORT_JSON comes in as a JSON string inside the CSV cell — parse it.
    if isinstance(report_json, str):
        report_json = json.loads(report_json)

    return {
        "report_id": str(row["REPORT_ID"]),
        "data_source": row.get("DATA_SOURCE"),
        "customer_name": row.get("CUSTOMER_NAME"),
        "imo": str(row["IMO"]) if pd.notna(row.get("IMO")) else None,
        "report_type": row.get("REPORT_TYPE"),
        "datetime_gmt": pd.to_datetime(row["DATETIME_GMT"]) if pd.notna(row.get("DATETIME_GMT")) else None,
        "report_json": report_json,
        "record_hash": row.get("RECORD_HASH"),
        "operation_type": row.get("OPERATION_TYPE"),
        "updated_at": pd.to_datetime(row["UPDATED_AT"]) if pd.notna(row.get("UPDATED_AT")) else None,
    }


def main() -> None:
    df = load_csv_files()

    connection_manager = PostgresConnectionManager(POSTGRES_CONFIG, os.environ["DATABASE_URL"])

    total_upserted = 0
    with connection_manager.session_scope() as session:
        for start in range(0, len(df), BATCH_SIZE):
            batch_df = df.iloc[start : start + BATCH_SIZE]
            rows = [row_to_dict(row) for _, row in batch_df.iterrows()]

            stmt = insert(ReportDocumentORM).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["report_id"],
                set_={
                    "data_source": stmt.excluded.data_source,
                    "customer_name": stmt.excluded.customer_name,
                    "imo": stmt.excluded.imo,
                    "report_type": stmt.excluded.report_type,
                    "datetime_gmt": stmt.excluded.datetime_gmt,
                    "report_json": stmt.excluded.report_json,
                    "record_hash": stmt.excluded.record_hash,
                    "operation_type": stmt.excluded.operation_type,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            session.execute(stmt)
            total_upserted += len(rows)
            print(f"Upserted batch: {len(rows)} rows (total so far: {total_upserted})")

    print(f"Done. Upserted {total_upserted} report(s) into report_documents.")


if __name__ == "__main__":
    main()