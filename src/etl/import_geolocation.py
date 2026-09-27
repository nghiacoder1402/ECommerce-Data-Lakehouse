import pandas as pd
from db import get_connection

CSV_PATH = r"F:\Nghia_download\dataset\olist_geolocation_dataset.csv"

def main():
    df = pd.read_csv(CSV_PATH)

    print(f"Rows found: {len(df)}")

    # Đổi tên cột cho phù hợp với SQL Server
    df = df.rename(columns={
        "geolocation_zip_code_prefix": "geolocation_zip_code_prefix",
        "geolocation_lat": "geolocation_lat",
        "geolocation_lng": "geolocation_lng",
        "geolocation_city": "geolocation_city",
        "geolocation_state": "geolocation_state"
    })

    # Chuyển dữ liệu rỗng thành None
    df = df.where(pd.notnull(df), None)

    rows = list(
        df[
            [
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
                "geolocation_city",
                "geolocation_state"
            ]
        ].itertuples(index=False, name=None)
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.fast_executemany = True

    sql = """
        INSERT INTO dbo.Geolocation
        (
            geolocation_zip_code_prefix,
            geolocation_lat,
            geolocation_lng,
            geolocation_city,
            geolocation_state
        )
        VALUES (?, ?, ?, ?, ?)
    """

    print("Importing...")

    cursor.executemany(sql, rows)

    conn.commit()

    print(f"Imported {len(rows)} geolocation records successfully.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()