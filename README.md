# Hệ Thống Quản Lý Chi Tiêu Cá Nhân & Gia Đình (Expense Tracker)

> **Môn học:** Triển khai và Quản trị Hệ thống Phần mềm  
> **Đề tài 38:** Hệ thống Quản lý Chi tiêu / Expense Tracker  
> **Sinh viên thực hiện:** [Họ và tên Sinh viên] - **MSSV:** [Mã số SV]  
> **Công nghệ triển khai:** Node.js, PostgreSQL 16, pgAdmin 4, Nginx Reverse Proxy, Prometheus, Grafana, Loki, Promtail, cAdvisor, Docker Compose.

---

## 📑 Mục Lục
1. [Giới Thiệu Đề Tài](#-giới-thiệu-đề-tài)
2. [Kiến Trúc Tổng Thể Hệ Thống](#-kiến-trúc-tổng-thể-hệ-thống)
3. [Danh Sách Các Dịch Vụ & Cổng Truy Cập](#-danh-sách-các-dịch-vụ--cổng-truy-cập)
4. [Các Biện Pháp Hardening & An Toàn Hệ Thống](#-các-biện-pháp-hardening--an-toàn-hệ-thống)
5. [Hướng Dẫn Cài Đặt & Khởi Chạy](#-hướng-dẫn-cài-đặt--khởi-chạy)
6. [Hướng Dẫn Giám Sát Với Prometheus & Grafana](#-hướng-dẫn-giám-sát-với-prometheus--grafana)
7. [Hướng Dẫn Truy Vấn Log Tập Trung Với Loki & LogQL](#-hướng-dẫn-truy-vấn-log-tập-trung-với-loki--logql)
8. [Cấu Trúc Thư Mục Dự Án](#-cấu-trúc-thư-mục-dự-án)
9. [Lịch Sử Commit Git (Chuẩn Đồ Án)](#-lịch-sử-commit-git-chuẩn-đồ-án)

---

## 🌟 Giới Thiệu Đề Tài
Đề tài xây dựng và triển khai một nền tảng **Quản lý Chi tiêu (Expense Tracker)** toàn diện dành cho cá nhân và gia đình. Ứng dụng cung cấp các tính năng:
- **Quản lý giao dịch:** Ghi nhận thu/chi, phân loại danh mục, ngày thực hiện, số tiền, ghi chú chi tiết.
- **Quản lý danh mục:** Hỗ trợ đa dạng danh mục (Ăn uống, Nhà ở, Mua sắm, Di chuyển, Lương, Đầu tư...).
- **Báo cáo & Phân tích trực quan:** Biểu đồ cơ cấu chi tiêu dạng Donut Chart và biểu đồ xu hướng dòng tiền theo tháng dạng Bar Chart (tích hợp Chart.js).
- **Xuất dữ liệu:** Hỗ trợ xuất toàn bộ lịch sử giao dịch ra định dạng file CSV.
- **Hạ tầng quản trị hiện đại:** Toàn bộ hệ thống được container hóa qua Docker Compose, tích hợp giám sát hiệu năng (Prometheus, Grafana, cAdvisor, postgres-exporter), quản lý log tập trung (Loki, Promtail) và bảo mật nhiều lớp (Nginx SSL, Network Isolation, Non-root containers, Least privilege DB).

---

## 🏗 Kiến Trúc Tổng Thể Hệ Thống

```mermaid
graph TD
    User([Khách hàng / Quản trị viên])
    
    subgraph DMZ_Frontend ["Vùng Mạng Frontend (frontend_net)"]
        Nginx["Nginx Reverse Proxy & SSL Gateway<br>(Ports 80 -> 443 HTTPS)"]
    end
    
    subgraph App_Tier ["Tầng Xử Lý Ứng Dụng"]
        App["Expense Tracker Web App<br>(Node.js Non-root User 10001)"]
    end
    
    subgraph Data_Tier ["Vùng Mạng Nội Bộ Cơ Sở Dữ Liệu (backend_net)"]
        Postgres[("PostgreSQL 16 DB<br>(Internal 5432 - NO Host Port)")]
        pgAdmin["pgAdmin 4 Web UI<br>(Subpath /pgadmin)"]
    end
    
    subgraph Monitoring_Tier ["Vùng Mạng Giám Sát & Logs (monitoring_net)"]
        Prometheus["Prometheus Time-series DB<br>(Port 9090)"]
        Grafana["Grafana Dashboards<br>(Port 3001)"]
        cAdvisor["cAdvisor Container Exporter<br>(Port 8080)"]
        PgExporter["Postgres Exporter<br>(Internal 9187)"]
        Loki["Loki Log Store<br>(Port 3100)"]
        Promtail["Promtail Log Shipper<br>(Port 9080)"]
    end

    User -->|HTTP :80 Redirect| Nginx
    User -->|HTTPS :443| Nginx
    Nginx -->|Reverse Proxy /| App
    Nginx -->|Reverse Proxy /pgadmin/| pgAdmin
    
    App -->|DML Queries (expense_user)| Postgres
    pgAdmin -->|Admin Access| Postgres
    PgExporter -->|Scrape DB Metrics| Postgres
    
    Prometheus -->|Scrape :3000/metrics| App
    Prometheus -->|Scrape :9187/metrics| PgExporter
    Prometheus -->|Scrape :8080/metrics| cAdvisor
    Prometheus -->|Scrape :80/stub_status| Nginx
    
    Grafana -->|Query Metrics| Prometheus
    Grafana -->|Query Logs (LogQL)| Loki
    
    Promtail -->|Parse /var/log/nginx/*.log| Nginx
    Promtail -->|Tail Container Logs| App
    Promtail -->|Push Streams| Loki
```

---

## 🌐 Danh Sách Các Dịch Vụ & Cổng Truy Cập

| Dịch vụ | Cổng Host | Cổng Container | Giao thức / Đường dẫn | Mô tả chức năng |
| :--- | :--- | :--- | :--- | :--- |
| **Nginx Web Gateway** | `80` (Redirect) / `443` | `80`, `443` | `https://localhost` | Cổng vào duy nhất của hệ thống, mã hóa SSL/TLS, Security Headers |
| **Expense Tracker App** | *Internal* | `3000` | Thông qua Nginx (`/`) | Giao diện theo dõi chi tiêu, API nghiệp vụ và `/metrics` |
| **pgAdmin 4** | *Internal* | `80` | Thông qua Nginx (`https://localhost/pgadmin`) | Quản trị giao diện đồ họa cơ sở dữ liệu PostgreSQL |
| **PostgreSQL Database** | *None* | `5432` | `backend_net` only | Cơ sở dữ liệu quan hệ lưu trữ dữ liệu tài chính (cách ly hoàn toàn) |
| **Grafana Monitoring** | `3001` | `3000` | `http://localhost:3001` | Bảng điều khiển giám sát trực quan container, app, database và logs |
| **Prometheus** | `9090` | `9090` | `http://localhost:9090` | Thu thập và lưu trữ time-series metrics |
| **cAdvisor** | `8080` | `8080` | `http://localhost:8080` | Giám sát tài nguyên phần cứng (CPU, RAM, Disk, Network) của container |
| **Loki** | `3100` | `3100` | `http://localhost:3100` | Công cụ lưu trữ và lập chỉ mục nhật ký tập trung |
| **Promtail** | `9080` | `9080` | `http://localhost:9080` | Agent đọc và chuyển tiếp log sang Loki |

### 🔑 Thông Tin Đăng Nhập Mặc Định

- **Hệ thống Web:** Truy cập tự do tại `https://localhost`
- **pgAdmin 4:**
  - Email: `admin@expensetracker.local`
  - Mật khẩu: `PgAdminSecurePass2026!#$`
  - *Lưu ý:* Kết nối Server đến PostgreSQL đã được cấu hình tự động (không cần add thủ công).
- **Grafana:**
  - Tài khoản: `admin`
  - Mật khẩu: `GrafanaAdminSecure2026!`
  - *Lưu ý:* Datasource (Prometheus, Loki) và Dashboard đã được provisioning sẵn.

---

## 🛡 Các Biện Pháp Hardening & An Toàn Hệ Thống

1. **Non-Root Containers:**
   - Image ứng dụng Node.js được build với user chuyên dụng `appuser` (UID: 10001, GID: 10001), loại bỏ hoàn toàn đặc quyền root trong container.
   - Prometheus chạy với UID `65534:65534` (nobody), Loki chạy với UID `10001:10001`.
2. **Network Isolation (Phân Vùng Mạng Độc Lập):**
   - `frontend_net`: Chỉ cho phép `nginx` và `app`.
   - `backend_net`: Chỉ cho phép `app`, `postgres`, `pgadmin`, `postgres-exporter`.
   - `monitoring_net`: Tách biệt các thành phần giám sát.
   - **Đặc biệt:** PostgreSQL không mở bất kỳ cổng nào ra máy host (không có `ports: 5432:5432`), triệt tiêu rủi ro tấn công trực tiếp từ bên ngoài.
3. **Least Privilege Database Access (Đặc Quyền Tối Thiểu):**
   - Ứng dụng kết nối DB bằng tài khoản nghiệp vụ `expense_user`.
   - Chỉ được cấp quyền DML cơ bản (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) trên các bảng nghiệp vụ, không có quyền can thiệp hệ thống hay DDL trái phép.
4. **Bảo Mật Nginx & Security Headers:**
   - Tự động chuyển hướng toàn bộ HTTP (Port 80) sang HTTPS (Port 443).
   - `Strict-Transport-Security (HSTS)` bắt buộc trình duyệt dùng HTTPS.
   - `X-Content-Type-Options: nosniff` chống MIME-sniffing.
   - `X-Frame-Options: SAMEORIGIN` chống Clickjacking.
   - `X-XSS-Protection: 1; mode=block` ngăn chặn tấn công XSS.
   - `Content-Security-Policy (CSP)` kiểm soát chặt chẽ nguồn nạp tài nguyên.
   - `server_tokens off;` ẩn hoàn toàn phiên bản Nginx trong HTTP Header.
5. **Resource Limits & Security Flags:**
   - Toàn bộ service đều được cấu hình `security_opt: [no-new-privileges:true]`.
   - Thiết lập ngưỡng `deploy.resources.limits` về CPU và RAM cho từng container, chống cạn kiệt tài nguyên máy chủ khi bị quá tải hoặc tấn công từ chối dịch vụ (DoS).
6. **Bảo Mật Biến Môi Trường (.env):**
   - Toàn bộ mật khẩu, port cấu hình được tách riêng vào `.env` (được đưa vào `.gitignore`), có file mẫu `.env.example` an toàn.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### Yêu Cầu Tiên Quyết
- Docker Engine & Docker Compose (v2.x trở lên).
- Git.

### Bước 1: Clone Repository
```bash
git clone <URL_REPOSITORY_GITHUB_CỦA_BẠN>
cd expense-tracker-system
```

### Bước 2: Thiết Lập Biến Môi Trường & Chứng Chỉ SSL
```bash
# Tạo file môi trường từ file mẫu
cp .env.example .env

# (Nếu chưa có chứng chỉ SSL trong nginx/certs, tạo bằng lệnh sau)
# Linux/macOS:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/server.key -out nginx/certs/server.crt \
  -subj "/C=VN/ST=HCM/L=HCM/O=ExpenseTracker/OU=IT/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

# Windows PowerShell:
& "C:\Program Files\Git\usr\bin\openssl.exe" req -x509 -nodes -days 365 -newkey rsa:2048 `
  -keyout nginx/certs/server.key -out nginx/certs/server.crt `
  -subj "/C=VN/ST=HCM/L=HCM/O=ExpenseTracker/OU=IT/CN=localhost" `
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

### Bước 3: Khởi Động Toàn Bộ Hệ Thống
```bash
docker compose up -d --build
```

Kiểm tra trạng thái các container:
```bash
docker compose ps
```
*Tất cả 10 container phải ở trạng thái `Up` hoặc `Up (healthy)`.*

### Bước 4: Tạo Lưu Lượng Mẫu & Kiểm Thử (Optional)
```bash
# Chạy script gửi traffic và giao dịch mẫu
# Trên Windows:
.\scripts\test_traffic.bat
# Hoặc thực hiện các thao tác thêm/xóa giao dịch trên giao diện Web https://localhost
```

---

## 📊 Hướng Dẫn Giám Sát Với Prometheus & Grafana

1. Truy cập Grafana tại địa chỉ: **`http://localhost:3001`**
2. Đăng nhập với tài khoản: `admin` / `GrafanaAdminSecure2026!`
3. Điều hướng vào menu **Dashboards** -> Mở dashboard **"Expense Tracker - System & Performance Overview"**.
4. Các vùng theo dõi chính:
   - **Khu vực 1: Ứng dụng & Nghiệp vụ (App & Business Metrics):**
     - Tổng số giao dịch (`expense_tracker_total_transactions`)
     - Tổng thu nhập & Tổng chi tiêu (`expense_tracker_total_income`, `expense_tracker_total_expense`)
     - Số dư ròng thời gian thực (`expense_tracker_net_balance`)
     - Tần suất HTTP Request và Độ trễ trung bình (`http_requests_total`, `http_request_duration_seconds`)
   - **Khu vực 2: Giám sát Container (cAdvisor):**
     - Biểu đồ % CPU của từng container
     - Mức tiêu thụ RAM của các container
   - **Khu vực 3: Hiệu năng Cơ sở dữ liệu (PostgreSQL):**
     - Số lượng kết nối đang hoạt động (`pg_stat_activity_count`)
     - Tỷ lệ Cache Hit Ratio (thường đạt trên 95%)
     - Tốc độ Commit / Rollback giao dịch
   - **Khu vực 4: Nhật ký thời gian thực (Loki Logs Stream):**
     - Luồng log trực tiếp được đẩy về từ Promtail

---

## 📜 Hướng Dẫn Truy Vấn Log Tập Trung Với Loki & LogQL

Truy cập Grafana -> Mục **Explore** -> Chọn nguồn dữ liệu **Loki**. Nhập các câu truy vấn LogQL mẫu dưới đây:

### Truy Vấn 1: Xem toàn bộ log của ứng dụng Expense Tracker
```logql
{service="expense-app"}
```
*Ý nghĩa:* Thu thập tất cả các luồng log do container ứng dụng sinh ra dưới dạng JSON có cấu trúc.

### Truy Vấn 2: Lọc các sự kiện tạo giao dịch nghiệp vụ thành công
```logql
{service="expense-app"} |= "transaction_created"
```
*Ý nghĩa:* Sử dụng toán tử `|=` để tìm chính xác các bản ghi log khi người dùng thực hiện thêm mới một khoản thu/chi.

### Truy Vấn 3: Giám sát và phát hiện các request lỗi (HTTP Status >= 400) từ Nginx
```logql
{job="nginx"} | json | status >= 400
```
*Ý nghĩa:* Promtail bóc tách log JSON của Nginx, trích xuất trường `status` và lọc các mã lỗi 4xx (Client Error) hoặc 5xx (Server Error).

### Truy Vấn 4: Tính tốc độ ghi nhận log của máy chủ web Nginx
```logql
rate({job="nginx"}[1m])
```
*Ý nghĩa:* Tính toán số lượng dòng log được sinh ra trên mỗi giây trong cửa sổ thời gian 1 phút.

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
expense-tracker-system/
├── app/                               # Mã nguồn ứng dụng Expense Tracker
│   ├── public/                        # Giao diện tĩnh (HTML5, CSS3, JS, Chart.js)
│   │   ├── css/style.css
│   │   ├── js/app.js
│   │   └── index.html
│   ├── src/                           # Backend server
│   │   ├── db.js                      # Kết nối PostgreSQL & Connection Pool
│   │   ├── metrics.js                 # Cấu hình Prometheus metrics
│   │   └── server.js                  # Express API & JSON Logging
│   ├── Dockerfile                     # Multi-stage Hardened Dockerfile (Non-root)
│   ├── package.json
│   └── .dockerignore
├── nginx/                             # Reverse Proxy & SSL Gateway
│   ├── certs/                         # Thư mục chứa chứng chỉ SSL tự ký
│   │   ├── server.crt
│   │   └── server.key
│   ├── conf.d/
│   │   └── default.conf               # Cấu hình Virtual Host HTTPS & Security Headers
│   └── nginx.conf                     # Cấu hình Nginx gốc & format log JSON
├── postgres/                          # Cơ sở dữ liệu PostgreSQL
│   └── init/
│       ├── 01-schema.sql              # Schema DDL & phân quyền least privilege
│       └── 02-seed.sql                # Dữ liệu mẫu danh mục và giao dịch ban đầu
├── pgadmin/                           # Cấu hình công cụ quản trị Database
│   └── servers.json                   # Auto-import connection vào pgAdmin 4
├── prometheus/                        # Hệ thống thu thập số liệu giám sát
│   └── prometheus.yml                 # Cấu hình scrape targets (App, DB, cAdvisor, Nginx)
├── grafana/                           # Giao diện hiển thị Dashboard
│   ├── provisioning/
│   │   ├── datasources/datasources.yaml
│   │   └── dashboards/dashboards.yaml
│   └── dashboards/
│       └── expense-tracker-overview.json # Dashboard thiết kế sẵn 4 vùng giám sát
├── loki/                              # Hệ thống lưu trữ Log tập trung
│   └── loki-config.yaml
├── promtail/                          # Agent thu thập log
│   └── promtail-config.yaml
├── scripts/                           # Các script hỗ trợ kiểm thử và tự động hóa
│   ├── test_traffic.bat
│   └── query_logql.bat
├── docs/                              # Tài liệu & Báo cáo tổng hợp
│   └── REPORT.md                      # Báo cáo chi tiết tối thiểu 10 trang
├── .env.example                       # Mẫu cấu hình biến môi trường
├── .env                               # Cấu hình chính thức
├── .gitignore
├── docker-compose.yml                 # File điều phối toàn bộ 10 dịch vụ
└── README.md                          # Tài liệu hướng dẫn sử dụng chính thức
```

---

## 📌 Lịch Sử Commit Git (Chuẩn Đồ Án)

Để đáp ứng chính xác tiêu chí đánh giá đề tài (đủ 3 commit lớn rõ ràng theo từng giai đoạn), dự án được phân chia commit như sau:

- **Commit 1:** `feat: implement Expense Tracker web app, PostgreSQL, pgAdmin and Nginx reverse proxy with HTTPS`
  - *Mô tả:* Triển khai ứng dụng theo dõi chi tiêu, kết nối PostgreSQL, nạp seed data, tích hợp pgAdmin 4 và Nginx reverse proxy với HTTPS tự ký + Security Headers.
- **Commit 2:** `feat: integrate Prometheus and Grafana monitoring with container and DB metrics`
  - *Mô tả:* Tích hợp Prometheus, cAdvisor, postgres-exporter, tự động provisioning Grafana Datasource và Dashboard toàn diện.
- **Commit 3:** `feat: implement Loki and Promtail centralized logging with LogQL and complete system hardening`
  - *Mô tả:* Hoàn thiện hệ sinh thái log tập trung Loki + Promtail, kịch bản truy vấn LogQL, đóng gói bảo mật (non-root, network isolation, least privilege).
