from pathlib import Path
import pandas as pd
from db import get_connection


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_order_reviews_dataset.csv"
)


def import_order_reviews():

    print("Reading CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # =========================
    # 1. Convert timestamps
    # =========================

    date_columns = [
        "review_creation_date",
        "review_answer_timestamp"
    ]

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # =========================
    # 2. Prepare data
    # =========================

    data = []

    for row in df.itertuples(index=False):

        review_creation_date = (
            row.review_creation_date.strftime("%Y-%m-%d %H:%M:%S")
            if pd.notna(row.review_creation_date)
            else None
        )

        review_answer_timestamp = (
            row.review_answer_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if pd.notna(row.review_answer_timestamp)
            else None
        )

        review_comment_title = (
            None
            if pd.isna(row.review_comment_title)
            else row.review_comment_title
        )

        review_comment_message = (
            None
            if pd.isna(row.review_comment_message)
            else row.review_comment_message
        )

        data.append(
            (
                row.review_id,
                row.order_id,
                int(row.review_score),
                review_comment_title,
                review_comment_message,
                review_creation_date,
                review_answer_timestamp
            )
        )

    print(f"Prepared rows: {len(data)}")

    # =========================
    # 3. Connect SQL Server
    # =========================

    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # 4. Insert data
    # =========================

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
        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            CONVERT(datetime2, ?, 126),
            CONVERT(datetime2, ?, 126)
        )
    """

    cursor.fast_executemany = True

    cursor.executemany(
        insert_sql,
        data
    )

    # =========================
    # 5. Commit
    # =========================

    conn.commit()

    print(
        f"Imported {len(data)} order reviews successfully."
    )

    cursor.close()
    conn.close()


if __name__ == "__main__":
    import_order_reviews()