#!/bin/bash
# 🏈 Super Bowl Props - One-Click Install Script
# Run this on a fresh Ubuntu/Debian server

set -e  # Exit on any error

echo "🏈 Super Bowl Props - Installation Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Installing to: $APP_DIR${NC}"

# Check if running as root for system packages
if [ "$EUID" -ne 0 ]; then
    SUDO='sudo'
else
    SUDO=''
fi

# Step 1: Install system dependencies
echo -e "\n${GREEN}[1/6] Installing system packages...${NC}"
$SUDO apt update
$SUDO apt install -y python3 python3-pip python3-venv nginx

# Step 2: Create virtual environment
echo -e "\n${GREEN}[2/6] Setting up Python virtual environment...${NC}"
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: Configure environment
echo -e "\n${GREEN}[3/6] Configuring environment...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        # Generate a random secret key
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        sed -i "s/your-secret-key-change-this-in-production/$SECRET_KEY/" .env
        echo -e "${YELLOW}Created .env file with random secret key${NC}"
        echo -e "${YELLOW}Edit .env to set MASTER_KEY${NC}"
    else
        echo -e "${RED}Warning: No .env.example found${NC}"
    fi
else
    echo -e "${YELLOW}.env already exists, skipping${NC}"
fi

# Step 4: Initialize database
echo -e "\n${GREEN}[4/6] Initializing database...${NC}"
python init_db.py

# Step 5: Set up systemd service
echo -e "\n${GREEN}[5/6] Setting up systemd service...${NC}"
SERVICE_FILE="/etc/systemd/system/superbowl-props.service"

# Update the service file with correct paths
$SUDO cp "$SCRIPT_DIR/superbowl-props.service" "$SERVICE_FILE"
$SUDO sed -i "s|/opt/superbowl-props|$APP_DIR|g" "$SERVICE_FILE"
$SUDO sed -i "s|User=www-data|User=$USER|g" "$SERVICE_FILE"
$SUDO sed -i "s|Group=www-data|Group=$USER|g" "$SERVICE_FILE"

$SUDO systemctl daemon-reload
$SUDO systemctl enable superbowl-props
$SUDO systemctl start superbowl-props

# Step 6: Configure nginx (optional)
echo -e "\n${GREEN}[6/6] Configuring nginx...${NC}"
NGINX_CONF="/etc/nginx/sites-available/superbowl-props"
$SUDO cp "$SCRIPT_DIR/nginx.conf" "$NGINX_CONF"
$SUDO sed -i "s|/opt/superbowl-props|$APP_DIR|g" "$NGINX_CONF"

if [ -L "/etc/nginx/sites-enabled/superbowl-props" ]; then
    $SUDO rm "/etc/nginx/sites-enabled/superbowl-props"
fi
$SUDO ln -s "$NGINX_CONF" /etc/nginx/sites-enabled/

# Test nginx config
if $SUDO nginx -t; then
    $SUDO systemctl restart nginx
    echo -e "${GREEN}Nginx configured successfully${NC}"
else
    echo -e "${RED}Nginx config test failed - check configuration${NC}"
fi

# Done!
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Installation complete!${NC}"
echo "=========================================="
echo ""
echo "The app is now running at:"
echo -e "  ${GREEN}http://localhost:5000${NC} (direct)"
echo -e "  ${GREEN}http://localhost${NC} (via nginx)"
echo ""
echo "Next steps:"
echo "  1. Edit .env to set your MASTER_KEY (admin password)"
echo "  2. Restart the service: sudo systemctl restart superbowl-props"
echo "  3. (Optional) Set up SSL with: sudo certbot --nginx"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status superbowl-props  # Check status"
echo "  sudo systemctl restart superbowl-props # Restart app"
echo "  sudo journalctl -u superbowl-props -f  # View logs"
