# Base image ổn định cho Flask + eventlet
FROM python:3.11-slim

# Không tạo file .pyc, log thẳng ra stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Thư mục làm việc trong container
WORKDIR /app

# Cài dependency hệ thống (cho Pillow + eventlet)
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements trước (tối ưu cache)
COPY requirements.txt .

# Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Mở cổng Flask
EXPOSE 5000

# Lệnh chạy app
CMD ["python", "app.py"]
