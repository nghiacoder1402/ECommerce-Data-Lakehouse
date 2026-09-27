import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_customers_dataset.csv"
)


def import_customers():
    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO dbo.Customers
        (
            customer_id,
            customer_unique_id,
            customer_zip_code_prefix,
            customer_city,
            customer_state
        )
        VALUES (?, ?, ?, ?, ?)
    """

    rows = [
        (
            row["customer_id"],
            row["customer_unique_id"],
            str(row["customer_zip_code_prefix"]).zfill(5),
            row["customer_city"],
            row["customer_state"]
        )
        for _, row in df.iterrows()
    ]

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, rows)

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Imported {len(rows)} customers successfully.")


if __name__ == "__main__":
    import_customers()