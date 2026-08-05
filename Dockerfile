FROM python:3.11-slim-bookworm

# Instal dependensi sistem yang dibutuhkan untuk OpenCV dan PyTorch
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    v4l-utils \
    libv4l-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Salin requirements dan instal (menggunakan pip biasa karena uv mungkin belum terinstal di container)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode proyek
COPY . .

# Beri akses eksekusi ke shell script
RUN chmod +x run.sh

# Port untuk Web Dashboard
EXPOSE 5000

# Jalankan aplikasi (kita pakai python main langsung karena di docker tidak perlu venv)
CMD ["python", "src/main.py"]
