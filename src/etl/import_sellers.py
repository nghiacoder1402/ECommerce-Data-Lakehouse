import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_sellers_dataset.csv"
)


def import_sellers():
    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO dbo.Sellers
        (
            seller_id,
            seller_zip_code_prefix,
            seller_city,
            seller_state
        )
        VALUES (?, ?, ?, ?)
    """

    rows = [
        (
            row["seller_id"],
            str(row["seller_zip_code_prefix"]).zfill(5),
            row["seller_city"],
            row["seller_state"]
        )
        for _, row in df.iterrows()
    ]

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, rows)

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Imported {len(rows)} sellers successfully.")


if __name__ == "__main__":
    import_sellers()