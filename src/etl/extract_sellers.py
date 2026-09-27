import pandas as pd
from db import get_connection

OUTPUT_PATH = r"F:\ECommerce-Data-Lakehouse\data\sellers.csv"


def main():
    conn = get_connection()

    query = """
        SELECT
            seller_id,
            seller_zip_code_prefix,
            seller_city,
            seller_state
        FROM dbo.Sellers
    """

    print("Extracting Sellers from SQL Server...")

    df = pd.read_sql(query, conn)

    conn.close()

    print(f"Rows extracted: {len(df)}")

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()