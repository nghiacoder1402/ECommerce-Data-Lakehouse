import pandas as pd
from db import get_connection

OUTPUT_PATH = r"F:\ECommerce-Data-Lakehouse\data\order_items.csv"


def main():
    conn = get_connection()

    query = """
        SELECT
            order_id,
            order_item_id,
            product_id,
            seller_id,
            shipping_limit_date,
            price,
            freight_value
        FROM dbo.OrderItems
    """

    print("Extracting OrderItems from SQL Server...")

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