from pathlib import Path
import pandas as pd
from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_order_items_dataset.csv"
)


def import_order_items():

    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Chuyển timestamp
    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    # NaN -> None
    df = df.where(pd.notnull(df), None)

    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO dbo.OrderItems
        (
            order_id,
            order_item_id,
            product_id,
            seller_id,
            shipping_limit_date,
            price,
            freight_value
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    data = [
        (
            row.order_id,
            int(row.order_item_id),
            row.product_id,
            row.seller_id,
            row.shipping_limit_date,
            float(row.price),
            float(row.freight_value)
        )
        for row in df.itertuples(index=False)
    ]

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, data)

    conn.commit()

    print(f"Imported {len(data)} order items successfully.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    import_order_items()