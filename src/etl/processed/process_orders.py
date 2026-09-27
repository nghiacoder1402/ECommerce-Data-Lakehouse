import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\orders.csv"
)

OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\orders.parquet"
)


TIMESTAMP_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def main():
    print("Reading RAW orders...")
    df = pd.read_csv(INPUT_FILE)

    print(f"RAW rows: {len(df):,}")

    # Convert timestamp columns
    for column in TIMESTAMP_COLUMNS:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Validate required columns
    required_columns = [
        "order_id",
        "customer_id",
        "order_status",
    ]

    for column in required_columns:
        if df[column].isna().any():
            raise ValueError(
                f"Required column contains NULL: {column}"
            )

    # Save as Parquet
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow"
    )

    print()
    print("PROCESSED orders created successfully.")
    print(f"Rows: {len(df):,}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size:,} bytes")

    print()
    print("Processed dtypes:")
    print(df.dtypes)

    print()
    print("Missing values after processing:")
    print(df.isna().sum())


if __name__ == "__main__":
    main()