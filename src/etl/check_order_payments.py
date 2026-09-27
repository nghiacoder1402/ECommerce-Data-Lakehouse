from pathlib import Path
import pandas as pd


CSV_PATH = Path(
    r"F:\Nghia_download\dataset\olist_order_payments_dataset.csv"
)


def check_payment_installments():

    print("Reading payments CSV...")

    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")

    invalid = df[df["payment_installments"] <= 0]

    print(f"Invalid payment_installments rows: {len(invalid)}")

    print("\nInvalid rows:")
    print(
        invalid[
            [
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value"
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    check_payment_installments()