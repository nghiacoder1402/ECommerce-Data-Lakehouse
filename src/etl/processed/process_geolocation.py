import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\geolocation.csv"
)

OUTPUT_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\geolocation.parquet"
)


def main():
    print("Reading RAW geolocation...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "geolocation_id": "int64",
            "geolocation_zip_code_prefix": "string",
            "geolocation_city": "string",
            "geolocation_state": "string",
        },
    )

    print(f"RAW rows: {len(df):,}")

    # ZIP code is an identifier, not a numeric value
    df["geolocation_zip_code_prefix"] = (
        df["geolocation_zip_code_prefix"].str.zfill(5)
    )

    # Convert coordinates explicitly to numeric
    df["geolocation_lat"] = pd.to_numeric(
        df["geolocation_lat"],
        errors="coerce"
    )

    df["geolocation_lng"] = pd.to_numeric(
        df["geolocation_lng"],
        errors="coerce"
    )

    required_columns = [
        "geolocation_id",
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    ]

    for column in required_columns:
        if df[column].isna().any():
            raise ValueError(
                f"{column} contains NULL after processing"
            )

    # geolocation_id must be unique
    if df["geolocation_id"].duplicated().any():
        raise ValueError(
            "Duplicate geolocation_id found"
        )

    # Validate latitude / longitude ranges
    if (
        (df["geolocation_lat"] < -90)
        | (df["geolocation_lat"] > 90)
    ).any():
        raise ValueError(
            "Invalid latitude value found"
        )

    if (
        (df["geolocation_lng"] < -180)
        | (df["geolocation_lng"] > 180)
    ).any():
        raise ValueError(
            "Invalid longitude value found"
        )

    # ZIP must contain exactly 5 characters
    if not (df["geolocation_zip_code_prefix"].str.len() == 5).all():
        raise ValueError(
            "Invalid ZIP code length found"
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

    print("Processed geolocation successfully.")
    print(f"Output: {OUTPUT_FILE}")
    print(
        f"Processed rows: {len(df):,}"
    )
    print(
        f"Output size: "
        f"{OUTPUT_FILE.stat().st_size:,} bytes"
    )


if __name__ == "__main__":
    main()