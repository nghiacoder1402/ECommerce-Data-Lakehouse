import sys
from pathlib import Path

import pandas as pd

# Cho phép import db.py từ cùng thư mục
sys.path.append(str(Path(__file__).resolve().parent))

from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\product_category_name_translation.csv"
)


def import_categories():
    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")

    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO dbo.ProductCategoryTranslation
        (
            product_category_name,
            product_category_name_english
        )
        VALUES (?, ?)
    """

    rows = [
        (
            row["product_category_name"],
            row["product_category_name_english"]
        )
        for _, row in df.iterrows()
    ]

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, rows)

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Imported {len(rows)} rows successfully.")


if __name__ == "__main__":
    import_categories()