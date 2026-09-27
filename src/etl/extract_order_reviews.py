import pandas as pd
from db import get_connection

OUTPUT_FILE = r"F:\ECommerce-Data-Lakehouse\data\order_reviews.csv"


def main():
    conn = get_connection()

    query = """
    SELECT
        review_record_id,
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp
    FROM dbo.OrderReviews
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("OrderReviews extracted successfully.")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")
    print()
    print("Missing values:")
    print(df.isna().sum())
    print()
    print("Review score distribution:")
    print(df["review_score"].value_counts().sort_index())
    print()
    print("First 3 rows:")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()