import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\order_items.csv"
)

OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\order_items.parquet"
)


def main():
    print("Reading RAW order_items...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "order_id": "string",
            "product_id": "string",
            "seller_id": "string",
        },
    )

    print(f"RAW rows: {len(df):,}")

    # ---------------------------------------------------------
    # 1. Convert shipping date to datetime
    # ---------------------------------------------------------

    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 2. Validate required columns
    # ---------------------------------------------------------

    required_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ]

    for column in required_columns:
        if df[column].isna().any():
            raise ValueError(
                f"{column} contains NULL after processing"
            )

    # ---------------------------------------------------------
    # 3. Validate composite key
    # ---------------------------------------------------------

    if df.duplicated(
        subset=["order_id", "order_item_id"]
    ).any():
        raise ValueError(
            "Duplicate (order_id, order_item_id) found"
        )

    # ---------------------------------------------------------
    # 4. Validate numeric business rules
    # ---------------------------------------------------------

    if (df["order_item_id"] <= 0).any():
        raise ValueError(
            "order_item_id contains invalid values"
        )

    if (df["price"] <= 0).any():
        raise ValueError(
            "price contains invalid values"
        )

    if (df["freight_value"] < 0).any():
        raise ValueError(
            "freight_value contains negative values"
        )

    # freight_value == 0 is allowed.

    # ---------------------------------------------------------
    # 5. Create output directory
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # 6. Write Parquet
    # ---------------------------------------------------------

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow"
    )

    # ---------------------------------------------------------
    # 7. Summary
    # ---------------------------------------------------------

    print()
    print("PROCESSED order_items created successfully.")
    print(f"Rows: {len(df):,}")
    print(f"Output: {OUTPUT_FILE}")
    print(
        f"File size: "
        f"{OUTPUT_FILE.stat().st_size:,} bytes"
    )

    print()
    print("Dtypes:")
    print(df.dtypes)

    print()
    print("Missing values:")
    print(df.isna().sum())

    print()
    print(
        "freight_value == 0:",
        (df["freight_value"] == 0).sum()
    )


if __name__ == "__main__":
    main()