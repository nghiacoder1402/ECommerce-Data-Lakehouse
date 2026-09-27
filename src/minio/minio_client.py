from minio import Minio

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "ecommerce"


def get_minio_client():
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    return client


if __name__ == "__main__":
    client = get_minio_client()

    if client.bucket_exists(BUCKET_NAME):
        print(f"Connected to MinIO successfully.")
        print(f"Bucket '{BUCKET_NAME}' exists.")
    else:
        print(f"Connected to MinIO, but bucket '{BUCKET_NAME}' does not exist.")