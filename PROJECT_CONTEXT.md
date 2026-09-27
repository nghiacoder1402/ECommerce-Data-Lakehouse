from pathlib import Path

content = r"""# E-Commerce Data Lakehouse & Data Protection — Project Context

## 1. Mục tiêu project

Xây dựng pipeline E-Commerce Data Lakehouse và Data Protection từ SQL Server OLTP đến MinIO, Spark, Parquet, Apache Iceberg và Trino; đồng thời demo backup/restore, versioning, snapshot, time travel và failure recovery.

Kiến trúc mục tiêu:

SQL Server (OLTP)
    ↓
Python ETL
    ↓
MinIO Data Lake
    RAW → PROCESSED → CURATED
    ↓
Apache Spark
    ↓
Parquet
    ↓
Apache Iceberg
    ↓
Trino
    ↓
SQL Analytics

Data Protection:
- MinIO Versioning
- Backup / Restore
- Iceberg Snapshots
- Time Travel
- Failure Simulation
- Recovery

Tech stack:
- SQL Server 2022 Developer
- Python
- MinIO
- Apache Spark
- Parquet
- Apache Iceberg
- Trino
- Docker
- Git/GitHub

---

## 2. Môi trường

OS: Windows 10 Pro
CPU: Intel i5-6300U
RAM: 8 GB
Python: 3.14.4
Java: OpenJDK 17.0.20.1
Git: 2.53.0.windows.3
Docker Desktop: 29.7.2
Docker Compose: 5.3.1
VMware Workstation Pro: 17.6.4
ESXi: 8.0.3

Ưu tiên lưu project trên ổ F:, không dùng C: cho dữ liệu mới nếu không cần.

MinIO data:
F:\DOCKER\minio_data

Không được xóa dữ liệu MinIO hiện tại.
Không chạy:
- docker system prune --volumes
- docker volume prune
- docker compose down -v
- docker rm minio
- xóa F:\DOCKER\minio_data

---

## 3. Thư mục project

F:\ECommerce-Data-Lakehouse

├── config
├── data
├── docker
│   ├── iceberg
│   ├── minio
│   ├── spark
│   ├── sqlserver
│   └── trino
├── docs
│   ├── architecture
│   ├── database
│   ├── demo
│   └── etl
├── logs
├── notebooks
├── sql
│   ├── 01_database
│   ├── 02_tables
│   ├── 03_indexes
│   └── 04_analytics
├── src
│   ├── etl
│   ├── minio
│   ├── spark
│   └── utils
│   └── validation
└── tests

Dataset nguồn KHÔNG nằm trong GitHub/project data:
F:\Nghia_download\dataset

---

## 4. Dataset

Nguồn: Olist Brazilian E-Commerce Public Dataset.

Các file nguồn:
- olist_customers_dataset.csv
- olist_geolocation_dataset.csv
- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_order_payments_dataset.csv
- olist_order_reviews_dataset.csv
- olist_products_dataset.csv
- olist_sellers_dataset.csv
- product_category_name_translation.csv

Đường dẫn:
F:\Nghia_download\dataset

Các điểm dữ liệu đặc biệt đã xác nhận:
- customer_unique_id không unique.
- geolocation_zip_code_prefix không unique.
- product source có typo: product_name_lenght, product_description_lenght.
- một số timestamp Orders có 0001-01-01 00:00:00; giữ nguyên ở OLTP, sẽ xử lý ở ETL cleaning.
- OrderPayments có 2 dòng payment_installments = 0; import script đã chuẩn hóa <=0 thành 1 để thỏa CHECK constraint.
- OrderReviews có duplicate review_id nhưng các duplicate group tương ứng nhiều order_id và cùng score/content/date; không xóa dữ liệu.

---

## 5. SQL Server

SQL Server 2022 Developer đang chạy.
Database:
ECommerceDB

Kết nối Python:
src\etl\db.py

Nội dung logic:
- SERVER = localhost
- DATABASE = ECommerceDB
- DRIVER = ODBC Driver 18 for SQL Server
- Trusted_Connection=yes
- TrustServerCertificate=yes

Đã test:
Connected to database: ECommerceDB

---

## 6. Schema SQL Server

1. dbo.ProductCategoryTranslation
- product_category_name VARCHAR(100) NOT NULL PRIMARY KEY
- product_category_name_english VARCHAR(100) NULL

2. dbo.Customers
- customer_id CHAR(32) NOT NULL PRIMARY KEY
- customer_unique_id CHAR(32) NOT NULL
- customer_zip_code_prefix CHAR(5) NOT NULL
- customer_city VARCHAR(100) NOT NULL
- customer_state CHAR(2) NOT NULL
- Không UNIQUE customer_unique_id.

3. dbo.Sellers
- seller_id CHAR(32) NOT NULL PRIMARY KEY
- seller_zip_code_prefix CHAR(5) NOT NULL
- seller_city VARCHAR(100) NOT NULL
- seller_state CHAR(2) NOT NULL

4. dbo.Products
- product_id CHAR(32) NOT NULL PRIMARY KEY
- product_category_name VARCHAR(100) NULL
- product_name_length INT NULL
- product_description_length INT NULL
- product_photos_qty INT NULL
- product_weight_g DECIMAL(10,2) NULL
- product_length_cm DECIMAL(10,2) NULL
- product_height_cm DECIMAL(10,2) NULL
- product_width_cm DECIMAL(10,2) NULL
- FK category → ProductCategoryTranslation
- CHECK các trường số không âm.

5. dbo.Orders
- order_id CHAR(32) NOT NULL PRIMARY KEY
- customer_id CHAR(32) NOT NULL FK → Customers
- order_status VARCHAR(30) NOT NULL
- order_purchase_timestamp DATETIME2(0) NOT NULL
- các timestamp còn lại nullable.

6. dbo.OrderItems
- order_id CHAR(32) NOT NULL
- order_item_id INT NOT NULL
- product_id CHAR(32) NOT NULL
- seller_id CHAR(32) NOT NULL
- shipping_limit_date DATETIME2(0) NOT NULL
- price DECIMAL(12,2) NOT NULL
- freight_value DECIMAL(12,2) NOT NULL
- PK (order_id, order_item_id)
- FK Orders, Products, Sellers
- CHECK price/freight >= 0, item_id > 0.

7. dbo.OrderPayments
- order_id CHAR(32) NOT NULL
- payment_sequential INT NOT NULL
- payment_type VARCHAR(30) NOT NULL
- payment_installments INT NOT NULL
- payment_value DECIMAL(12,2) NOT NULL
- PK (order_id, payment_sequential)
- FK Orders
- CHECK sequential/installments > 0, value >= 0.

8. dbo.OrderReviews
- review_record_id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY
- review_id CHAR(32) NOT NULL
- order_id CHAR(32) NOT NULL FK → Orders
- review_score TINYINT NOT NULL CHECK 1–5
- review_comment_title NVARCHAR(500) NULL
- review_comment_message NVARCHAR(MAX) NULL
- review_creation_date DATETIME2(0) NULL
- review_answer_timestamp DATETIME2(0) NULL

Lý do review_record_id làm PK: review_id không unique trong source.

9. dbo.Geolocation
- geolocation_id BIGINT IDENTITY(1,1) PRIMARY KEY
- geolocation_zip_code_prefix CHAR(5) NOT NULL
- geolocation_lat DECIMAL(12,9) NOT NULL
- geolocation_lng DECIMAL(12,9) NOT NULL
- geolocation_city VARCHAR(100)
- geolocation_state CHAR(2)

Geolocation ZIP không unique nên không dùng ZIP làm PK.

---

## 7. Số lượng dữ liệu hiện tại

Checkpoint cuối cùng của ECommerceDB:

- ProductCategoryTranslation: 73
- Customers: 99,441
- Sellers: 3,095
- Products: 32,951
- Orders: 99,441
- OrderItems: 112,650
- OrderPayments: 103,886
- OrderReviews: 99,224
- Geolocation: 1,000,163

Tổng khoảng 2.44 triệu records.

OrderReviews validation:
- TotalReviews = 99,224
- DistinctReviewIDs = 98,410
- DistinctOrders = 98,673
- MinScore = 1
- MaxScore = 5
- DuplicateReviewGroups = 789
- 1,603 duplicate rows ban đầu được xác định theo review_id; duplicate review_id groups có 764 nhóm xuất hiện 2 lần và 25 nhóm xuất hiện 3 lần.
- Không xóa duplicate vì mỗi group liên quan nhiều order_id.

---

## 8. Các script ETL đã tạo

requirements.txt:
- pandas
- pyodbc
- minio
- python-dotenv

Đã kiểm tra dependencies OK.

Đã có:
src\etl\db.py

Các import script đã chạy thành công:
- import_categories.py → 71 source rows, sau đó thêm 2 category thiếu → tổng 73.
- import_customers.py → 99,441
- import_sellers.py → 3,095
- import_products.py → 32,951
- import_orders.py → 99,441
- import_order_items.py → 112,650
- import_order_payments.py → 103,886
- import_order_reviews.py → 99,224
- import_geolocation.py → 1,000,163

Các script kiểm tra:
- check_order_payments.py
- check_order_reviews.py

---

## 9. MinIO

MinIO container hiện tại:
- tên container: minio
- image: minio/minio
- API: http://localhost:9000
- Console: http://localhost:9001
- data mount: F:\DOCKER\minio_data → /data
- command: server /data --console-address :9001

Bucket project:
ecommerce

Các bucket cũ như ltdl và warehouse phải được giữ nguyên.

MinIO hiện đã được bật bằng:
docker start minio

Python connection test thành công:
Connected to MinIO successfully.
Bucket 'ecommerce' exists.

File:
src\minio\minio_client.py

Logic:
- endpoint localhost:9000
- bucket ecommerce
- secure=False
- kiểm tra bucket_exists.

Đã test upload thành công bằng:
src\minio\test_upload.py

Object test:
raw/test/test_customers.csv

Sau đó đã yêu cầu xóa object test.
Không dùng test object làm dữ liệu project.

---

## 10. PHASE hiện tại

PHASE 1 — SQL Server OLTP:
HOÀN THÀNH 100%.

PHASE 2 — Python ETL → MinIO RAW:
ĐANG THỰC HIỆN.

Đã hoàn thành:
1. MinIO chạy.
2. Python kết nối MinIO.
3. Test upload object.
4. Extract Customers từ SQL Server.
5. Lưu:
F:\ECommerce-Data-Lakehouse\data\customers.csv
6. Rows extracted = 99,441.
7. File size = 8,685,707 bytes.
8. Upload thành công vào:
ecommerce/raw/customers/customers.csv

Script:
src\etl\extract_customers.py

Script:
src\minio\upload_customers.py

extract_customers.py hiện dùng pandas.read_sql với pyodbc và có warning:
pandas only supports SQLAlchemy connectable...
Đây là warning, không phải lỗi. Có thể xử lý sau khi pipeline ổn định.

Pipeline Customers hiện tại:

SQL Server dbo.Customers
    ↓
Python extract
    ↓
data/customers.csv
    ↓
Python MinIO upload
    ↓
ecommerce/raw/customers/customers.csv

---

## 11. Cấu trúc Data Lake mục tiêu

MinIO bucket:
ecommerce

Mục tiêu:

ecommerce/
├── raw/
│   ├── customers/
│   ├── sellers/
│   ├── products/
│   ├── orders/
│   ├── order_items/
│   ├── order_payments/
│   ├── order_reviews/
│   ├── product_category_translation/
│   └── geolocation/
├── processed/
└── curated/

Lưu ý: MinIO folder/path là object prefix, không phải folder thật. Không cần tạo 9 folder thủ công. Khi Python upload object như:
raw/customers/customers.csv
MinIO sẽ hiển thị prefix customers.

---

## 12. Tiến độ

Ước tính khoảng 35–40% project.

Theo phase:
- Phase 1: 100%
- Phase 2: đang làm, Customers đã xong bước đầu
- Phase 3: Spark/Parquet: chưa làm
- Phase 4: Iceberg: chưa làm
- Phase 5: Trino/Analytics: chưa làm
- Phase 6: Data Protection + demo + README + GitHub + presentation: chưa làm

---

## 13. Các bước lớn tiếp theo

1. Kiểm tra object customers.csv trên MinIO.
2. Đối chiếu số dòng SQL Server ↔ CSV ↔ MinIO.
3. Tổng quát hóa ETL để extract/upload các bảng còn lại:
   - Sellers
   - Products
   - Orders
   - OrderItems
   - OrderPayments
   - OrderReviews
   - ProductCategoryTranslation
   - Geolocation
4. Thiết kế RAW partition/path và metadata.
5. Spark đọc RAW.
6. Cleaning/validation.
7. Ghi Parquet vào PROCESSED.
8. CURATED.
9. Cài/config Apache Iceberg.
10. Iceberg catalog/tables.
11. Snapshot.
12. Time Travel.
13. Schema Evolution.
14. Trino.
15. SQL analytics.
16. MinIO Versioning.
17. Backup/Restore.
18. Failure simulation.
19. Recovery verification.
20. README, GitHub và demo thuyết trình.

---

## 14. Nguyên tắc làm việc

- Người dùng muốn làm từng bước một.
- Không nhảy nhiều bước cùng lúc.
- Sau mỗi bước, chờ user chạy và gửi kết quả.
- Không yêu cầu chạy lại các bước đã hoàn thành.
- Giải thích đủ để người dùng hiểu và có thể thuyết trình.
- Không xóa dữ liệu MinIO hiện tại.
- Không tạo MinIO container mới nếu container hiện tại hoạt động.
- Dataset gốc ở F:\Nghia_download\dataset.
- Project ở F:\ECommerce-Data-Lakehouse.
- Khi hoàn thiện nên có README và GitHub-ready structure.
- Mục tiêu cuối cùng phải có demo lỗi dữ liệu / mất object / recovery để chứng minh Data Protection.

---

## 15. CHECKPOINT HIỆN TẠI — DỪNG TẠI ĐÂY

Đã upload thành công:
ecommerce/raw/customers/customers.csv

Cần làm tiếp:
**Kiểm tra file Customers trên MinIO và đối chiếu dữ liệu trước khi nhân pipeline cho các bảng còn lại.**
"""

path = Path("/mnt/data/PROJECT_CONTEXT.md")
path.write_text(content, encoding="utf-8")
print(f"Created: {path}")
print(f"Size: {path.stat().st_size:,} bytes")
