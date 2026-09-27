from pathlib import Path
import pandas as pd


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_order_reviews_dataset.csv"
)


def check_reviews():

    print("Reading reviews CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")
    print()

    # Kiểm tra độ dài các cột text
    title_lengths = (
        df["review_comment_title"]
        .fillna("")
        .astype(str)
        .str.len()
    )

    message_lengths = (
        df["review_comment_message"]
        .fillna("")
        .astype(str)
        .str.len()
    )

    print(
        f"Maximum review_comment_title length: "
        f"{title_lengths.max()}"
    )

    print(
        f"Maximum review_comment_message length: "
        f"{message_lengths.max()}"
    )

    # Kiểm tra timestamp
    date_columns = [
        "review_creation_date",
        "review_answer_timestamp"
    ]

    for column in date_columns:

        dates = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        print()
        print(f"{column}:")
        print(f"  Valid dates: {dates.notna().sum()}")
        print(f"  NULL dates: {dates.isna().sum()}")

        if dates.notna().any():
            print(f"  Minimum: {dates.min()}")
            print(f"  Maximum: {dates.max()}")

    # Kiểm tra duplicate review_id
    duplicate_reviews = df[
        df["review_id"].duplicated(keep=False)
    ]

    print()
    print(
        f"Duplicate review_id rows: "
        f"{len(duplicate_reviews)}"
    )

    if len(duplicate_reviews) > 0:
        print(
            duplicate_reviews[
                ["review_id", "order_id", "review_score"]
            ].head(20).to_string(index=False)
        )


if __name__ == "__main__":
    check_reviews()