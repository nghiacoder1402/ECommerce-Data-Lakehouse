import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_products_dataset.csv"
)


def import_products():
    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO dbo.Products
        (
            product_id,
            product_category_name,
            product_name_length,
            product_description_length,
            product_photos_qty,
            product_weight_g,
            product_length_cm,
            product_height_cm,
            product_width_cm
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows = [
        (
            row["product_id"],
            row["product_category_name"]
            if pd.notna(row["product_category_name"])
            else None,
            int(row["product_name_lenght"])
            if pd.notna(row["product_name_lenght"])
            else None,
            int(row["product_description_lenght"])
            if pd.notna(row["product_description_lenght"])
            else None,
            int(row["product_photos_qty"])
            if pd.notna(row["product_photos_qty"])
            else None,
            float(row["product_weight_g"])
            if pd.notna(row["product_weight_g"])
            else None,
            float(row["product_length_cm"])
            if pd.notna(row["product_length_cm"])
            else None,
            float(row["product_height_cm"])
            if pd.notna(row["product_height_cm"])
            else None,
            float(row["product_width_cm"])
            if pd.notna(row["product_width_cm"])
            else None,
        )
        for _, row in df.iterrows()
    ]

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, rows)

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Imported {len(rows)} products successfully.")


if __name__ == "__main__":
    import_products()