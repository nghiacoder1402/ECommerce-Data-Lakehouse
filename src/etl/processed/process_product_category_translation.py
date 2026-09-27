import sys
from pathlib import Path

import pandas as pd

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from db import get_connection


OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\product_category_translation.parquet"
)


def main():
    print("Reading ProductCategoryTranslation from SQL Server...")

    conn = get_connection()

    query = """
        SELECT
            product_category_name,
            product_category_name_english
        FROM dbo.ProductCategoryTranslation
    """

    df = pd.read_sql(query, conn)

    conn.close()

    print(f"Rows extracted: {len(df):,}")

    required_columns = [
        "product_category_name",
        "product_category_name_english",
    ]

    for column in required_columns:
        if df[column].isna().any():
            print(
                f"Warning: {column} contains NULL values."
            )

    if df["product_category_name"].duplicated().any():
        raise ValueError(
            "Duplicate product_category_name found"
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow"
    )

    print("Processed ProductCategoryTranslation successfully.")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Rows: {len(df):,}")
    print(
        f"Output size: "
        f"{OUTPUT_FILE.stat().st_size:,} bytes"
    )


if __name__ == "__main__":
    main()