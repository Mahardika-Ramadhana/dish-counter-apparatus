#!/bin/bash
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    source venv/bin/activate
fi

# Instal/sync dependensi secara rapih otomatis menggunakan uv jika tersedia
if command -v uv &> /dev/null; then
    echo "Mendeteksi uv. Menyelaraskan dependensi (sekejap)..."
    uv pip install -r requirements.txt
    echo "Menjalankan DICA Server..."
fi

PYTHONPATH=src uv run python -m dica.core.app
