#!/bin/bash

# Super Bowl Props Web App - Setup Script
# Run this script on a fresh Ubuntu installation

set -e

echo "========================================"
echo "Super Bowl Props Web App Setup"
echo "========================================"

# Update system packages
echo "[1/6] Updating system packages..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nginx

# Create application directory
APP_DIR="/opt/superbowl-props"
echo "[2/6] Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files
echo "[3/6] Copying application files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR"/* $APP_DIR/

# Create virtual environment
echo "[4/6] Creating Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "[5/6] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize the database
echo "[6/6] Initializing database..."
python init_db.py

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/superbowl-props.service > /dev/null <<EOF
[Unit]
Description=Super Bowl Props Web App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx
echo "Configuring nginx..."
sudo tee /etc/nginx/sites-available/superbowl-props > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 1d;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/superbowl-props /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable superbowl-props
sudo systemctl start superbowl-props

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "The application is now running at http://localhost"
echo ""
echo "Default admin credentials:"
echo "  Email: admin@example.com"
echo "  Password: admin123"
echo ""
echo "IMPORTANT: Change the admin password after first login!"
echo ""
echo "To view logs: sudo journalctl -u superbowl-props -f"
echo "To restart: sudo systemctl restart superbowl-props"
echo ""
