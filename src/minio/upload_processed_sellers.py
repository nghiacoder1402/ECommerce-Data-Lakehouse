from minio_client import get_minio_client, BUCKET_NAME
from pathlib import Path


LOCAL_FILE = Path(
    r"F:\ECommerce-Data-Lakehouse\data\processed\sellers.parquet"
)

OBJECT_NAME = "processed/sellers/sellers.parquet"


def main():
    client = get_minio_client()

    file_size = LOCAL_FILE.stat().st_size

    print(f"Uploading: {LOCAL_FILE}")
    print(f"File size: {file_size:,} bytes")

    client.fput_object(
        BUCKET_NAME,
        OBJECT_NAME,
        str(LOCAL_FILE),
        content_type="application/octet-stream"
    )

    print("Uploaded successfully:")
    print(f"  Bucket : {BUCKET_NAME}")
    print(f"  Object : {OBJECT_NAME}")


if __name__ == "__main__":
    main()