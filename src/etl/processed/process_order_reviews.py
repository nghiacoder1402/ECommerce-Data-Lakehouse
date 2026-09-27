import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\order_reviews.csv"
)

OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\order_reviews.parquet"
)


def main():
    print("Reading RAW order_reviews...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "review_id": "string",
            "order_id": "string",
            "review_comment_title": "string",
            "review_comment_message": "string",
        },
    )

    print(f"RAW rows: {len(df):,}")

    # ---------------------------------------------------------
    # 1. Convert timestamps
    # ---------------------------------------------------------

    df["review_creation_date"] = pd.to_datetime(
        df["review_creation_date"],
        errors="coerce"
    )

    df["review_answer_timestamp"] = pd.to_datetime(
        df["review_answer_timestamp"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 2. Validate required columns
    # ---------------------------------------------------------

    required_columns = [
        "review_record_id",
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "review_answer_timestamp",
    ]

    for column in required_columns:
        if df[column].isna().any():
            raise ValueError(
                f"{column} contains NULL after processing"
            )

    # ---------------------------------------------------------
    # 3. Validate review_record_id
    # ---------------------------------------------------------

    if df["review_record_id"].duplicated().any():
        raise ValueError(
            "Duplicate review_record_id found"
        )

    # ---------------------------------------------------------
    # 4. Validate review_id / order_id relationship
    # ---------------------------------------------------------

    if df.duplicated(
        subset=["review_id", "order_id"]
    ).any():
        raise ValueError(
            "Duplicate (review_id, order_id) found"
        )

    # review_id itself is allowed to repeat.

    # ---------------------------------------------------------
    # 5. Validate review score
    # ---------------------------------------------------------

    if (
        (df["review_score"] < 1)
        | (df["review_score"] > 5)
    ).any():
        raise ValueError(
            "review_score must be between 1 and 5"
        )

    # ---------------------------------------------------------
    # 6. Create output directory
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # 7. Write Parquet
    # ---------------------------------------------------------

    df.to_parquet(
        OUTPUT_FILE,
        index=False,
        engine="pyarrow"
    )

    # ---------------------------------------------------------
    # 8. Summary
    # ---------------------------------------------------------

    print()
    print("PROCESSED order_reviews created successfully.")
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
        "Duplicate review_id:",
        df["review_id"].duplicated().sum()
    )

    print()
    print(
        "Duplicate (review_id, order_id):",
        df.duplicated(
            subset=["review_id", "order_id"]
        ).sum()
    )


if __name__ == "__main__":
    main()