# ECommerce Data Lakehouse

Project thực hành Data Engineering trên dữ liệu Brazilian E-Commerce Public Dataset by Olist. Repository hiện có Python ETL để nạp CSV vào SQL Server, trích xuất bảng ra CSV cục bộ, xử lý một số bảng thành Parquet và upload file lên MinIO. Cấu hình Docker cho Spark, Apache Iceberg REST Catalog và Trino cũng có mặt.

Tài liệu này phân biệt mã đã có với phần chỉ mới cấu hình. Việc có file cấu hình không chứng minh service đang chạy hoặc pipeline đầu-cuối đã hoạt động.

## Mục lục

- [Tổng quan](#tong-quan)
- [Khả năng hiện có](#kha-nang-hien-co)
- [Công nghệ](#cong-nghe)
- [Kiến trúc](#kien-truc)
- [Cấu trúc repository](#cau-truc-repository)
- [Luồng dữ liệu](#luong-du-lieu)
- [Điều kiện tiên quyết](#dieu-kien-tien-quyet)
- [Cài đặt và cấu hình](#cai-dat-va-cau-hinh)
- [Cách chạy các bước hiện có](#cach-chay-cac-buoc-hien-co)
- [Dữ liệu và đầu ra](#du-lieu-va-dau-ra)
- [Chất lượng dữ liệu và xử lý lỗi](#chat-luong-du-lieu-va-xu-ly-loi)
- [Xác minh và xử lý sự cố](#xac-minh-va-xu-ly-su-co)
- [Giới hạn hiện tại](#gioi-han-hien-tai)
- [Hướng phát triển](#huong-phat-trien)
- [Tóm tắt portfolio](#tom-tat-portfolio)

<a id="tong-quan"></a>
## Tổng quan

Project khám phá các bước ingest, lưu trữ và chuẩn bị dữ liệu thương mại điện tử cho phân tích. Phần có mã rõ nhất là SQL Server ↔ Python ↔ CSV cục bộ, xử lý CSV bằng pandas để tạo Parquet cục bộ và uploader riêng lẻ để gửi file lên MinIO.

Cấu hình Spark, Iceberg REST Catalog và Trino mô tả các kết nối dự kiến. Repository hiện không có Spark ETL job, notebook hay SQL analytics để xác nhận luồng phân tích hoàn chỉnh.

> README này dựa trên kiểm tra tĩnh mã, cấu hình và sự hiện diện của file. Các lệnh hướng dẫn chưa được chạy/xác minh trong lần viết tài liệu này.

<a id="kha-nang-hien-co"></a>
## Khả năng hiện có

### Được thể hiện trong mã

- Các script src/etl/import_*.py đọc CSV nguồn và chèn vào các bảng SQL Server.
- Các script src/etl/extract_*.py truy vấn bảng SQL Server và ghi CSV vào data/.
- Các processor trong src/etl/processed/ dùng pandas để chuyển đổi/kiểm tra một số bảng và ghi Parquet.
- Các script src/minio/upload_*.py tải từng CSV hoặc Parquet cục bộ lên bucket ecommerce theo object key cố định.
- Một số script kiểm tra null, duplicate, ngày giờ và quy tắc số học; quy tắc khác nhau theo bảng.

### Có cấu hình nhưng chưa xác minh runtime

- Docker Compose mô tả MinIO, Spark, Iceberg REST Catalog và Trino.
- Spark cấu hình S3A và Iceberg REST Catalog; Trino cấu hình Iceberg connector và cùng catalog.
- Các JSON trong docker/iceberg-rest/ mô tả namespace và metadata-location để đăng ký một số bảng.

Các cấu hình này không chứng minh container khởi động được, dịch vụ kết nối thành công, bảng được đăng ký hoặc truy vấn trả kết quả.

<a id="cong-nghe"></a>
## Công nghệ

| Công nghệ | Vai trò | Cách dùng trong repository |
|---|---|---|
| Python | ETL và thao tác file | Các script import/export, processing và upload trong src/. |
| pandas | Đọc CSV, kiểm tra, chuyển đổi | Dùng trong src/etl/ để xử lý file cục bộ và đọc kết quả SQL Server. |
| SQL Server | Cơ sở dữ liệu quan hệ | src/etl/db.py kết nối ECommerceDB trên localhost bằng Windows Trusted Connection và ODBC Driver 18. Không có DDL/schema trong repository. |
| MinIO | S3-compatible object storage | Client Python dùng endpoint localhost:9000, bucket ecommerce; uploader ghi object theo key. |
| Parquet / PyArrow | Định dạng file dạng cột | Processor gọi to_parquet(..., engine="pyarrow"); pyarrow chưa có trong requirements.txt. |
| Apache Spark | Engine xử lý phân tán | Có Dockerfile và cấu hình S3A/Iceberg; chưa có job trong src/spark/ hoặc notebook. |
| Apache Iceberg | Table format và metadata | Có REST Catalog/Spark/Trino config và JSON đăng ký; chưa có quy trình tạo/đăng ký bảng có thể chạy lại trong code. |
| Trino | SQL query engine | Có Compose và Iceberg catalog config; không có SQL analytics trong repository. |
| Docker Compose | Khai báo dịch vụ cục bộ | Có Compose root và Compose theo thành phần; phụ thuộc network/image ngoài được mô tả bên dưới. |

requirements.txt khai báo pandas, pyodbc, minio và python-dotenv, không ghim phiên bản. Các processor Parquet còn cần pyarrow, hiện chưa được khai báo.

<a id="kien-truc"></a>
## Kiến trúc

Mũi tên liền biểu thị đường đi được thể hiện trong code; mũi tên nét đứt là tích hợp được cấu hình nhưng chưa xác minh.

~~~mermaid
flowchart TD
    A["CSV Olist bên ngoài repository"] -->|"import_*.py: INSERT"| B["SQL Server: ECommerceDB"]
    B -->|"extract_*.py: SELECT → CSV"| C["CSV cục bộ: data/"]
    C -->|"process_*.py: pandas"| D["Parquet cục bộ: data/processed/"]
    C -->|"upload_*.py riêng lẻ"| E["MinIO bucket ecommerce / raw/"]
    D -->|"upload_processed_*.py riêng lẻ"| F["MinIO bucket ecommerce / processed/"]

    E -. "S3A được cấu hình; chưa có Spark job" .-> G["Spark"]
    G -. "REST catalog được cấu hình" .-> H["Iceberg REST Catalog"]
    H -. "Iceberg connector được cấu hình" .-> I["Trino"]
    I -. "chưa có SQL analytics" .-> J["Phân tích / báo cáo"]
~~~

Compose mount data/ vào container Spark; spark-defaults.conf cũng cấu hình S3A. Do không có job/notebook, chưa xác định Spark thực tế đọc local file hay MinIO.

<a id="cau-truc-repository"></a>
## Cấu trúc repository

~~~text
.
├── data/                         # CSV cục bộ và Parquet hiện có
│   └── processed/
├── docker/
│   ├── iceberg-rest/             # Compose và JSON namespace/đăng ký bảng
│   ├── spark/                    # Dockerfile, Compose, spark-defaults.conf
│   └── trino/                    # Compose và cấu hình catalog/server
├── src/
│   ├── etl/                      # import_*, extract_*, check_*
│   │   └── processed/            # pandas CSV → Parquet
│   ├── minio/                    # client và uploader theo từng object
│   ├── spark/                    # hiện rỗng
│   ├── utils/                    # hiện rỗng
│   └── validation/               # hiện rỗng
├── sql/                          # thư mục con rỗng; chưa có DDL/query
├── notebooks/                    # hiện rỗng
├── tests/                        # hiện rỗng
├── docker-compose.yml            # Compose tổng hợp trong working tree
├── PROJECT_CONTEXT.md            # ghi chú kiến trúc/checkpoint trước đây
└── requirements.txt              # Python dependencies được khai báo
~~~

backup/ có bản sao cục bộ của object/data và Iceberg artifacts nhưng bị .gitignore loại khỏi Git. config/, thư mục con trong docs/, docker/minio/ và docker/sqlserver/ hiện không có file.

Tại thời điểm viết README, docker-compose.yml ở root đang **untracked** theo Git. File sẽ không có trong clone từ remote cho đến khi được thêm vào Git.

<a id="luong-du-lieu"></a>
## Luồng dữ liệu

### 1. Nạp CSV nguồn vào SQL Server

Các script src/etl/import_*.py đọc CSV từ đường dẫn dataset bên ngoài được khai báo trong script (hiện là F:\Nghia_download\dataset) rồi chèn vào SQL Server qua pyodbc. Đây là thao tác ghi; repository không có DDL để dựng database/schema mới.

### 2. Trích xuất ra CSV cục bộ

Các script src/etl/extract_*.py chạy SELECT trên bảng dbo.* và ghi vào data/. Ví dụ:

- extract_customers.py: dbo.Customers → data/customers.csv.
- extract_orders.py: dbo.Orders → data/orders.csv.

Nhiều script dùng đường dẫn tuyệt đối gắn với F:\ECommerce-Data-Lakehouse; cần chỉnh nếu project được đặt ở nơi khác.

### 3. Xử lý thành Parquet

Các script src/etl/processed/process_*.py dùng pandas trên file cục bộ, không phải Spark. process_customers.py đọc ID/ZIP dạng chuỗi, đệm ZIP prefix thành 5 ký tự và kiểm tra null ở trường bắt buộc. process_orders.py chuyển timestamp với errors="coerce" và kiểm tra order_id, customer_id, order_status. Riêng process_product_category_translation.py đọc dbo.ProductCategoryTranslation trực tiếp từ SQL Server rồi ghi Parquet.

### 4. Upload lên MinIO

Các script src/minio/upload_*.py độc lập gửi file cục bộ đến bucket ecommerce. Ví dụ raw Customers là raw/customers/customers.csv; processed Customers là processed/customers/customers.parquet. Extract, processing và upload chưa được kết nối bởi orchestrator.

MinIO lưu object bytes theo bucket/key. Object trong MinIO tự nó không phải SQL table; muốn truy vấn dạng bảng cần table format/catalog và query engine kết nối đúng.

### 5. Spark, Iceberg và Trino

spark-defaults.conf cấu hình S3A/REST catalog; docker/iceberg-rest/ có Compose và JSON metadata-location; docker/trino/etc/catalog/iceberg.properties cấu hình Iceberg connector. Chưa có Spark job, script đăng ký bảng tự động hay SQL analytics để chạy lại phần này.

backup/minio/ có file data/metadata Iceberg cục bộ, gồm raw và một số bảng curated. Đây chỉ là artifact trong backup, không xác nhận service hiện tại phục vụ được chúng. backup/ bị Git ignore.

<a id="dieu-kien-tien-quyet"></a>
## Điều kiện tiên quyết

### Python và xử lý file

- Python trên Windows; repository không ghim phiên bản.
- SQL Server local, database ECommerceDB, Windows authentication và ODBC Driver 18 for SQL Server để dùng src/etl/db.py.
- pyarrow để chạy các processor Parquet; dependency này hiện thiếu khỏi requirements.txt.
- Các đường dẫn đầu vào/đầu ra hardcode trong script phải tồn tại hoặc được cập nhật.

### Docker

- Docker Desktop/Compose nếu chạy container.
- Root Compose khai báo external network ecommerce-lakehouse; network phải tồn tại trước khi khởi động.
- Root Compose tham chiếu image Spark ecommerce-spark:3.5.5-hadoop-aws nhưng không có build:. Dockerfile có sẵn; build chưa được xác minh.
- MinIO bind mount từ F:/DOCKER/minio_data sang /data; xác nhận đúng thư mục dữ liệu trước khi chạy.
- Cổng host được cấu hình: MinIO 9000, Console 9001, Iceberg REST 8182, Trino 8081; Spark 8080, 8888, 10000, 10001.

SQL Server không có trong Compose; docker/sqlserver/ rỗng. Trạng thái container chưa được kiểm tra.

<a id="cai-dat-va-cau-hinh"></a>
## Cài đặt và cấu hình

Các bước sau dựa trên file hiện có và chưa được chạy kiểm chứng. Chạy trong PowerShell tại thư mục gốc repository:

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
~~~

Processor dùng PyArrow nhưng dependency này chưa khai báo. Nếu định chạy chúng, cài riêng trong virtual environment:

~~~powershell
python -m pip install pyarrow
~~~

src/etl/db.py dùng localhost, ECommerceDB, ODBC Driver 18 và Windows Trusted Connection. Cần tạo database/bảng trước; không có DDL trong repository.

Root docker-compose.yml khai báo MinIO, Iceberg REST, Trino và Spark cùng dependencies. Compose trong docker/spark/, docker/iceberg-rest/, docker/trino/ là cấu hình thành phần, phụ thuộc external network và không tự dựng toàn bộ stack.

Một số cấu hình chứa credential hardcode. .gitignore loại .env, nhưng các file hiện tại không thay giá trị tĩnh bằng biến môi trường và không đọc .env. Hãy xử lý credential an toàn ngoài README, không commit secret, đồng thời xác nhận network, image Spark và bind mount trước khi chạy Compose.

Sau khi đã xác nhận các điều kiện trên, lệnh Compose tổng hợp dự kiến là:

~~~powershell
docker compose -f docker-compose.yml up -d
~~~

Lệnh này **chưa được chạy/xác minh** và làm thay đổi trạng thái Docker; nó khởi động MinIO với bind mount dữ liệu đã khai báo. Chỉ chạy khi đã xác nhận đúng service và thư mục dữ liệu. Compose root đang untracked nên chưa có trong clone remote.

<a id="cach-chay-cac-buoc-hien-co"></a>
## Cách chạy các bước hiện có

Các lệnh ví dụ phải chạy từ PowerShell ở thư mục gốc. Chưa có lệnh nào được chạy trong lần viết tài liệu này. Script dùng path tuyệt đối; xác nhận path, database và service trước khi chạy.

### Kiểm tra kết nối SQL Server

~~~powershell
python .\src\etl\db.py
~~~

Script thực hiện SELECT DB_NAME(); cần SQL Server, database và ODBC Driver sẵn sàng.

### Xuất Customers/Orders ra CSV

~~~powershell
python .\src\etl\extract_customers.py
python .\src\etl\extract_orders.py
~~~

Đọc dbo.Customers/dbo.Orders, ghi data/customers.csv/data/orders.csv. Chạy lại sẽ ghi file đích.

### Xử lý CSV thành Parquet

~~~powershell
python .\src\etl\processed\process_customers.py
python .\src\etl\processed\process_orders.py
~~~

Đọc CSV trong data/, ghi vào data/processed/. Cần PyArrow; output được ghi trực tiếp vào path đã cấu hình.

### Upload CSV raw lên MinIO

~~~powershell
python .\src\minio\upload_customers.py
python .\src\minio\upload_orders.py
~~~

Gửi file lên localhost:9000, bucket ecommerce, theo object key cố định. Cần xác nhận MinIO, bucket và credential trước khi chạy; upload có thể ghi lại cùng key.

import_*.py ghi SQL Server và cần CSV nguồn/schema đích. Repository không có DDL hay orchestrator để dựng/điều phối toàn quy trình. src/minio/test_upload.py thực hiện put_object lên MinIO; đây không phải unit test chỉ đọc.

<a id="du-lieu-va-dau-ra"></a>
## Dữ liệu và đầu ra

| Khu vực | Ví dụ | Ghi chú |
|---|---|---|
| CSV cục bộ | data/customers.csv, data/orders.csv và các bảng khác | Có 8 CSV; không thấy product_category_translation.csv trong data/. |
| Parquet cục bộ | data/processed/customers.parquet, data/processed/orders.parquet và các bảng khác | Có 9 Parquet; sự hiện diện không xác nhận schema hoặc nguồn sinh file. |
| MinIO raw | ecommerce/raw/customers/customers.csv, ecommerce/raw/orders/orders.csv | Object key từ uploader; chưa xác minh trên service hiện tại. |
| MinIO processed | ecommerce/processed/customers/customers.parquet, ecommerce/processed/orders/orders.parquet | Object key từ uploader; chưa tự động hóa upload. |
| Iceberg warehouse | s3://ecommerce/iceberg/ trong REST config | Vị trí cấu hình, không phải bằng chứng bảng truy vấn được. |
| Iceberg backup | backup/minio/ecommerce/iceberg/ | Artifact cục bộ, bị Git ignore; không đọc nội dung dữ liệu. |

Trong MinIO, raw/... và processed/... là object key/prefix, không phải folder vật lý hay SQL table. Các đường dẫn trên dựa trên code/config và không khẳng định object hiện tồn tại trên server.

<a id="chat-luong-du-lieu-va-xu-ly-loi"></a>
## Chất lượng dữ liệu và xử lý lỗi

Một số kiểm tra trong processor:

- Customers: giữ ID/ZIP dạng chuỗi, đệm ZIP prefix và dừng bằng ValueError nếu trường bắt buộc có null.
- Orders: chuyển timestamp với errors="coerce" và kiểm tra các trường ID/status bắt buộc. Timestamp lỗi có thể thành null; không có reject output riêng.
- Products: kiểm tra product_id null/trùng, đổi weight không hợp lệ thành null và dừng khi trường số âm.
- Order items: kiểm tra trường bắt buộc, khóa kép (order_id, order_item_id), item ID, price và freight.
- Một số check_*.py là script kiểm tra độc lập, không phải test suite tự động.

Chưa thấy logging có cấu trúc, data contract dùng chung, reject report, run ID, đối soát xuyên tầng hoặc publish output nguyên tử. Importer INSERT rồi commit; rerun có thể xung đột khóa. Uploader dùng key cố định. Chưa có bằng chứng pipeline idempotent hoặc phục hồi an toàn.

<a id="xac-minh-va-xu-ly-su-co"></a>
## Xác minh và xử lý sự cố

Có thể dùng các kiểm tra read-only sau khi môi trường đã sẵn sàng; chúng chưa được chạy trong lần viết README:

~~~powershell
docker compose -f docker-compose.yml config --services
git status --short
~~~

Repository không có SQL analytics để đưa ra lệnh truy vấn Trino.

- **SQL Server connection error:** xác nhận SQL Server local, ECommerceDB, Windows authentication và ODBC Driver 18. db.py không đọc connection config từ environment.
- **CSV không tìm thấy:** import dùng đường dẫn dataset bên ngoài; extract/process/upload dùng path local hardcode. Xác nhận thư mục/tên file.
- **Ghi Parquet thất bại:** processor cần pyarrow, dependency này không được cài qua requirements.txt.
- **MinIO connection error:** client dùng localhost:9000, bucket ecommerce, HTTP không TLS; Compose cần external network/mount đúng. Không in credential ra log/terminal.
- **Spark image/service không khởi động:** root Compose chỉ tham chiếu image, không build; Dockerfile tải connector JAR khi build. Xác nhận image và external network.

Không dùng lệnh xóa volume/container hoặc thay đổi dữ liệu để xử lý lỗi. src/minio/test_upload.py ghi object và chỉ nên chạy khi chấp nhận tác động lên MinIO.

<a id="gioi-han-hien-tai"></a>
## Giới hạn hiện tại

- Chưa có Spark ETL job/notebook; chưa xác định Spark thực tế đọc local file hay MinIO.
- Chưa có SQL DDL, query analytics hoặc hướng dẫn dựng database sạch.
- Script chạy độc lập, dùng path tuyệt đối và chưa có orchestration.
- pyarrow thiếu trong dependency manifest; phiên bản dependency chưa ghim.
- Compose phụ thuộc external network, image Spark riêng và credential config; Compose root đang untracked.
- Không có test suite; file dữ liệu/backup không thay thế kiểm tra đầu-cuối.
- Chưa có bằng chứng runtime cho Spark–MinIO–Iceberg–Trino, truy vấn, snapshot/time travel hoặc backup/restore.
- PROJECT_CONTEXT.md chứa checkpoint cũ không khớp hoàn toàn với code/config hiện có; README này ưu tiên hiện trạng code/config.

<a id="huong-phat-trien"></a>
## Hướng phát triển

1. Đưa credential ra khỏi source/config được version control và thống nhất cách cấu hình Python/Docker.
2. Hoàn thiện một vertical slice Customers: extract → raw object → Spark đọc MinIO → Parquet/Iceberg → truy vấn Trino đối chiếu số dòng.
3. Bổ sung DDL/schema, khai báo PyArrow, fixture/test chất lượng dữ liệu và quy tắc rerun an toàn.
4. Cập nhật hướng dẫn bằng kết quả chạy trên môi trường sạch, phiên bản đã xác nhận và giới hạn thực tế.

Đây là đề xuất tương lai, không phải chức năng đã hoàn thành.

<a id="tom-tat-portfolio"></a>
## Tóm tắt portfolio

ECommerce Data Lakehouse là project thực hành Data Engineering dùng dữ liệu Olist để khám phá ingest CSV vào SQL Server, trích xuất bằng Python/pandas, chuyển đổi sang Parquet và upload object lên MinIO. Repository cũng chứa cấu hình thử nghiệm cho Spark, Iceberg REST Catalog và Trino. Orchestration, Spark transformation và truy vấn analytics đầu-cuối vẫn cần được bổ sung và xác minh trước khi mô tả project như một lakehouse vận hành hoàn chỉnh.
