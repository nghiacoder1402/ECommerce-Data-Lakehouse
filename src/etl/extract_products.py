import pandas as pd
from db import get_connection

OUTPUT_PATH = r"F:\ECommerce-Data-Lakehouse\data\products.csv"


def main():
    conn = get_connection()

    query = """
        SELECT
            product_id,
            product_category_name,
            product_name_length,
            product_description_length,
            product_photos_qty,
            product_weight_g,
            product_length_cm,
            product_height_cm,
            product_width_cm
        FROM dbo.Products
    """

    print("Extracting Products from SQL Server...")

    df = pd.read_sql(query, conn)

    conn.close()

    print(f"Rows extracted: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()