FROM python:3.11-slim-bookworm

# Instal dependensi sistem yang dibutuhkan untuk OpenCV dan PyTorch
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    v4l-utils \
    libv4l-0 \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instal uv lalu install requirements secara system-wide
COPY requirements.txt .
RUN pip install uv && uv pip install --system -r requirements.txt

# Salin seluruh kode proyek
COPY . .

# Port untuk Web Dashboard
ENV PYTHONPATH=/app/src
EXPOSE 5000

# Jalankan aplikasi (kita pakai python main langsung karena di docker tidak perlu venv)
CMD ["uv", "run", "python", "-m", "dica.core.app"]
