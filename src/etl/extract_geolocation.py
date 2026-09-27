import pandas as pd
from db import get_connection

OUTPUT_FILE = r"F:\ECommerce-Data-Lakehouse\data\geolocation.csv"


def main():
    conn = get_connection()

    query = """
    SELECT
        geolocation_id,
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state
    FROM dbo.Geolocation
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("Geolocation extracted successfully.")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")
    print()
    print("Missing values:")
    print(df.isna().sum())
    print()
    print("First 3 rows:")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()