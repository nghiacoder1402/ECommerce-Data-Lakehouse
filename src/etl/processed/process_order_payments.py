import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\order_payments.csv"
)

OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\order_payments.parquet"
)


def main():
    print("Reading RAW order_payments...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "order_id": "string",
            "payment_type": "string",
        },
    )

    print(f"RAW rows: {len(df):,}")

    # ---------------------------------------------------------
    # 1. Validate required columns
    # ---------------------------------------------------------

    required_columns = [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ]

    for column in required_columns:
        if df[column].isna().any():
            raise ValueError(
                f"{column} contains NULL"
            )

    # ---------------------------------------------------------
    # 2. Validate composite key
    # ---------------------------------------------------------

    if df.duplicated(
        subset=["order_id", "payment_sequential"]
    ).any():
        raise ValueError(
            "Duplicate (order_id, payment_sequential) found"
        )

    # ---------------------------------------------------------
    # 3. Validate business rules
    # ---------------------------------------------------------

    if (df["payment_sequential"] <= 0).any():
        raise ValueError(
            "payment_sequential contains invalid values"
        )

    if (df["payment_installments"] <= 0).any():
        raise ValueError(
            "payment_installments contains invalid values"
        )

    if (df["payment_value"] < 0).any():
        raise ValueError(
            "payment_value contains negative values"
        )

    # payment_value == 0 is allowed.

    # ---------------------------------------------------------
    # 4. Create output directory
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # 5. Write Parquet
    # ---------------------------------------------------------

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow"
    )

    # ---------------------------------------------------------
    # 6. Summary
    # ---------------------------------------------------------

    print()
    print("PROCESSED order_payments created successfully.")
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
        "payment_value == 0:",
        (df["payment_value"] == 0).sum()
    )

    print()
    print("Payment types:")
    print(
        df["payment_type"]
        .value_counts()
        .to_string()
    )


if __name__ == "__main__":
    main()