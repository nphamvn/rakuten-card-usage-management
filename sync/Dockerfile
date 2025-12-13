# Sử dụng Python 3.13 image mới nhất
FROM python:3.13-slim

# Cài đặt dependencies cần thiết cho Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Thêm Google Chrome repository và cài đặt Chrome
RUN wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome-stable_current_amd64.deb \
    && rm /tmp/google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy requirements.txt và cài đặt Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy code ứng dụng
COPY . .

# Tạo user non-root để chạy Chrome an toàn hơn
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Command mặc định
CMD ["python", "main.py"]