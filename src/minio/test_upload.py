from minio_client import get_minio_client, BUCKET_NAME
from io import BytesIO

client = get_minio_client()

content = b"customer_id,name\nTEST001,Test Customer\n"

object_name = "raw/test/test_customers.csv"

client.put_object(
    BUCKET_NAME,
    object_name,
    BytesIO(content),
    length=len(content),
    content_type="text/csv"
)

print(f"Uploaded successfully: {object_name}")