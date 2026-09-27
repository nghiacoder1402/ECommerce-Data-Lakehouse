from pathlib import Path
import pandas as pd
from db import get_connection

CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_order_reviews_dataset.csv"
)


def debug_reviews():

    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    date_columns = [
        "review_creation_date",
        "review_answer_timestamp"
    ]

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    df = df.where(pd.notnull(df), None)

    conn = get_connection()
    cursor = conn.cursor()

    insert_sql = """
    INSERT INTO dbo.OrderReviews
    (
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp
    )
    VALUES (?, ?, ?, ?, ?, CONVERT(datetime2, ?, 126), CONVERT(datetime2, ?, 126))
"""

    for index, row in enumerate(df.itertuples(index=False), start=1):

        try:
            review_creation_date = (
                row.review_creation_date.to_pydatetime()
                if row.review_creation_date is not None
                else None
            )

            review_answer_timestamp = (
                row.review_answer_timestamp.to_pydatetime()
                if row.review_answer_timestamp is not None
                else None
            )

            print(
                "TYPE creation:",
                type(review_creation_date)
            )

            print(
                "TYPE answer:",
                type(review_answer_timestamp)
            )

            print(
                "VALUE creation:",
                repr(review_creation_date)
            )

            print(
                "VALUE answer:",
                repr(review_answer_timestamp)
            )

            cursor.execute(
    insert_sql,
    row.review_id,
    row.order_id,
    int(row.review_score),
    None if pd.isna(row.review_comment_title) else row.review_comment_title,
    None if pd.isna(row.review_comment_message) else row.review_comment_message,
    review_creation_date.strftime("%Y-%m-%d %H:%M:%S")
        if review_creation_date is not None
        else None,
    review_answer_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if review_answer_timestamp is not None
        else None
)

        except Exception as e:

            print()
            print("=" * 70)
            print(f"ERROR AT CSV ROW: {index}")
            print("=" * 70)

            print("review_id:", row.review_id)
            print("order_id:", row.order_id)
            print("review_score:", row.review_score)
            print("review_comment_title:", row.review_comment_title)
            print("review_comment_message:", row.review_comment_message)
            print("review_creation_date:", row.review_creation_date)
            print("review_answer_timestamp:", row.review_answer_timestamp)

            print()
            print("ERROR:")
            print(e)

            conn.rollback()
            cursor.close()
            conn.close()

            return

    conn.rollback()
    cursor.close()
    conn.close()

    print("No problematic numeric row found.")


if __name__ == "__main__":
    debug_reviews()