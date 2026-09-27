import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\customers.csv"
)

OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\customers.parquet"
)


def main():
    print("Reading RAW customers...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "customer_id": "string",
            "customer_unique_id": "string",
            "customer_zip_code_prefix": "string",
            "customer_city": "string",
            "customer_state": "string",
        },
    )

    print(f"RAW rows: {len(df):,}")

    # ZIP prefix must be treated as a code, not a number.
    df["customer_zip_code_prefix"] = (
        df["customer_zip_code_prefix"]
        .str.zfill(5)
    )

    # Validate required fields
    required_columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]

    for column in required_columns:
        if df[column].isna().any():
            raise ValueError(
                f"Required column contains NULL: {column}"
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

    print()
    print("PROCESSED customers created successfully.")
    print(f"Rows: {len(df):,}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size:,} bytes")

    print()
    print("Dtypes:")
    print(df.dtypes)

    print()
    print("First 3 rows:")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()