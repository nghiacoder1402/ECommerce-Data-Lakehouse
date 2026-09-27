import pandas as pd
from db import get_connection

OUTPUT_PATH = r"F:\ECommerce-Data-Lakehouse\data\orders.csv"


def main():
    conn = get_connection()

    query = """
        SELECT
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date
        FROM dbo.Orders
    """

    print("Extracting Orders from SQL Server...")

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