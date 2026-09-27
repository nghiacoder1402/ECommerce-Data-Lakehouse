from pathlib import Path

import pandas as pd

from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_products_dataset.csv"
)


def check_categories():
    print("Reading products CSV...")

    df = pd.read_csv(
        CSV_PATH,
        usecols=["product_category_name"]
    )

    csv_categories = set(
        df["product_category_name"]
        .dropna()
        .unique()
    )

    print(f"Categories in Products CSV: {len(csv_categories)}")

    conn = get_connection()

    query = """
        SELECT product_category_name
        FROM dbo.ProductCategoryTranslation
    """

    db_categories = pd.read_sql(query, conn)[
        "product_category_name"
    ].dropna()

    db_categories = set(db_categories)

    print(
        f"Categories in SQL Server: {len(db_categories)}"
    )

    missing = sorted(csv_categories - db_categories)

    print(f"Missing categories: {len(missing)}")

    for category in missing:
        print(f"  - {category}")

    conn.close()


if __name__ == "__main__":
    check_categories()