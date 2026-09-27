from pathlib import Path
import pandas as pd
from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_orders_dataset.csv"
)


def import_orders():

    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Đổi tên cột source → tên cột SQL Server
    df = df.rename(columns={
        "order_purchase_timestamp": "order_purchase_timestamp",
        "order_approved_at": "order_approved_at",
        "order_delivered_carrier_date": "order_delivered_carrier_date",
        "order_delivered_customer_date": "order_delivered_customer_date",
        "order_estimated_delivery_date": "order_estimated_delivery_date"
    })

    # Chuyển timestamp
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Chuyển NaN → None để pyodbc xử lý thành SQL NULL
    df = df.where(pd.notnull(df), None)

    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO dbo.Orders
        (
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    data = [
        (
            row.order_id,
            row.customer_id,
            row.order_status,
            row.order_purchase_timestamp,
            row.order_approved_at,
            row.order_delivered_carrier_date,
            row.order_delivered_customer_date,
            row.order_estimated_delivery_date
        )
        for row in df.itertuples(index=False)
    ]

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, data)

    conn.commit()

    print(f"Imported {len(data)} orders successfully.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    import_orders()