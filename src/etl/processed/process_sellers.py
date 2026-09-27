import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\sellers.csv"
)

OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\sellers.parquet"
)


def main():
    print("Reading RAW sellers...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "seller_id": "string",
            "seller_zip_code_prefix": "string",
            "seller_city": "string",
            "seller_state": "string",
        },
    )

    print(f"RAW rows: {len(df):,}")

    # ZIP prefix is a code, not a numeric value.
    df["seller_zip_code_prefix"] = (
        df["seller_zip_code_prefix"]
        .str.zfill(5)
    )

    required_columns = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
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
    print("PROCESSED sellers created successfully.")
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