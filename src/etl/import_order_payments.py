from pathlib import Path
import pandas as pd
from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_order_payments_dataset.csv"
)


def import_order_payments():

    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Data quality rule:
    # payment_installments = 0 is invalid.
    # Replace invalid values with 1.
    invalid_count = (df["payment_installments"] <= 0).sum()

    if invalid_count > 0:
        print(
            f"Found {invalid_count} invalid payment_installments. "
            "Replacing with 1."
        )

        df.loc[
            df["payment_installments"] <= 0,
            "payment_installments"
        ] = 1

    # NaN -> None
    df = df.where(pd.notnull(df), None)

    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO dbo.OrderPayments
        (
            order_id,
            payment_sequential,
            payment_type,
            payment_installments,
            payment_value
        )
        VALUES (?, ?, ?, ?, ?)
    """

    data = [
        (
            row.order_id,
            int(row.payment_sequential),
            row.payment_type,
            int(row.payment_installments),
            float(row.payment_value)
        )
        for row in df.itertuples(index=False)
    ]

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, data)

    conn.commit()

    print(f"Imported {len(data)} order payments successfully.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    import_order_payments()