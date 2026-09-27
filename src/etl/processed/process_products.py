import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\products.csv"
)

OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\products.parquet"
)


def main():
    print("Reading RAW products...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "product_id": "string",
            "product_category_name": "string",
        },
    )

    print(f"RAW rows: {len(df):,}")

    # ---------------------------------------------------------
    # 1. Validate product_id
    # ---------------------------------------------------------

    if df["product_id"].isna().any():
        raise ValueError("product_id contains NULL")

    if df["product_id"].duplicated().any():
        raise ValueError("product_id contains duplicates")

    # ---------------------------------------------------------
    # 2. Handle invalid product weight
    # ---------------------------------------------------------

    invalid_weight = (df["product_weight_g"] <= 0).sum()

    print(f"Invalid weight values (<= 0): {invalid_weight}")

    df.loc[df["product_weight_g"] <= 0, "product_weight_g"] = pd.NA

    # ---------------------------------------------------------
    # 3. Validate numeric fields
    # ---------------------------------------------------------

    numeric_columns = [
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    # These fields must never contain negative values.
    for column in numeric_columns:
        if (df[column] < 0).any():
            raise ValueError(
                f"{column} contains negative values"
            )

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
    print("PROCESSED products created successfully.")
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
    print("Missing values after processing:")
    print(df.isna().sum())


if __name__ == "__main__":
    main()