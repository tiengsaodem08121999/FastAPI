## FastAPI Suppliers API

Ứng dụng FastAPI quản lý `Supplier` và `Products` sử dụng SQLite và Tortoise ORM, có hỗ trợ gửi email thông báo.

### 1. Cấu trúc chính

- `app.py`: Khai báo app FastAPI, router API, cấu hình Tortoise ORM và gửi email.
- `models.py`: Định nghĩa model `Products`, `Supplier` và các Pydantic schema.
- `database.sqlite3`: Database SQLite (được mount ra host khi chạy Docker Compose).
- `.env.example`: Mẫu file cấu hình email.
- `Dockerfile`: Cấu hình build image Docker cho app.
- `docker-compose.yml`: Cấu hình chạy app bằng Docker Compose.

### 2. Chuẩn bị biến môi trường

Tạo file `.env` cùng thư mục, dựa trên `.env.example`:

```env
EMAIL=your_gmail@gmail.com
PASSWORD=your_app_password   # App password của Gmail, KHÔNG phải password login thường
```

File `.env`:
- Khi chạy **local**: được đọc bằng `python-dotenv`.
- Khi chạy **Docker Compose**: được nạp thông qua `env_file` trong `docker-compose.yml`.

### 3. Chạy local (không dùng Docker)

Yêu cầu Python 3.10+.

```bash
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Truy cập:
- API root: `http://localhost:8000/`
- Tài liệu Swagger: `http://localhost:8000/docs`

### 4. Chạy bằng Docker trực tiếp

Build image:

```bash
docker build -t fastapi-suppliers .
```

Chạy container (dùng `.env` trên host):

```bash
docker run -d --name fastapi-suppliers `
  -p 8000:8000 `
  --env-file .env `
  fastapi-suppliers
```

Truy cập:
- `http://localhost:8000/`
- `http://localhost:8000/docs`

### 5. Chạy bằng Docker Compose

Trong thư mục dự án (`d:\fastAPI` trên Windows):

```powershell
docker compose up -d --build
```

Docker Compose sẽ:
- Build image từ `Dockerfile`.
- Chạy service `web` trên port `8000`.
- Nạp biến môi trường từ file `.env`.
- Mount file `database.sqlite3` ra host: dữ liệu không bị mất khi recreate container.

Dừng container:

```powershell
docker compose down
```

### 6. Lưu ý

- Không commit file `.env` lên git.
- `database.sqlite3` được mount ra host, có thể backup/thay thế trực tiếp trên máy.
- Khi thay đổi code Python, nên chạy:

```powershell
docker compose up -d --build
```

để rebuild image với code mới.
