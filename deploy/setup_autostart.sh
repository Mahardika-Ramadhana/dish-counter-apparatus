#!/bin/bash
set -e

echo "Menyiapkan DICA Autostart Service..."

# Mendapatkan absolute path dari direktori proyek
PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
USER_NAME=$(whoami)

echo "Project Directory: $PROJECT_DIR"
echo "User: $USER_NAME"

# Menyesuaikan file service dengan path dan user saat ini
cat > /tmp/dica.service << EOF
[Unit]
Description=Dish Counter Apparatus (DICA) Auto-start Service
After=network.target graphical.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$USER_NAME/.Xauthority
WorkingDirectory=$PROJECT_DIR
ExecStart=/bin/bash $PROJECT_DIR/run.sh
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

# Menyalin ke systemd
sudo cp /tmp/dica.service /etc/systemd/system/dica.service
sudo systemctl daemon-reload
sudo systemctl enable dica.service

echo "✅ Autostart DICA berhasil dipasang!"
echo "Untuk menjalankan manual sekarang: sudo systemctl start dica"
echo "Untuk melihat log: sudo journalctl -u dica -f"
