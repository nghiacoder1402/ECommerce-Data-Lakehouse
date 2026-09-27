from pathlib import Path
from minio_client import get_minio_client, BUCKET_NAME


LOCAL_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\order_reviews.parquet"
)

OBJECT_NAME = "processed/order_reviews/order_reviews.parquet"


def main():
    client = get_minio_client()

    if not LOCAL_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {LOCAL_FILE}"
        )

    client.fput_object(
        BUCKET_NAME,
        OBJECT_NAME,
        str(LOCAL_FILE),
        content_type="application/octet-stream"
    )

    print("Upload successful.")
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Object: {OBJECT_NAME}")
    print(f"Local file size: {LOCAL_FILE.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()