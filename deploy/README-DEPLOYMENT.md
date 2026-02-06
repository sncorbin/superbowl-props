# 🏈 Super Bowl Props - Deployment Guide

## Quick Overview

This app can be deployed in several ways:

| Method | Cost | Difficulty | Best For |
|--------|------|------------|----------|
| **Local/VPS** | $5-10/mo | Medium | Full control, privacy |
| **Render.com** | FREE | Easy | Quick cloud deployment |
| **PythonAnywhere** | FREE | Easy | Python-specific hosting |
| **Railway.app** | FREE tier | Easy | Modern cloud platform |

---

## Option 1: Local/Self-Hosted Deployment

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.10+
- nginx (for production)

### One-Command Setup
```bash
# Upload your project folder, then run:
cd /path/to/superbowl-props
chmod +x deploy/install.sh
./deploy/install.sh
```

### Manual Setup Steps

1. **Install Python & dependencies:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx -y
```

2. **Create virtual environment:**
```bash
cd /path/to/superbowl-props
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

4. **Initialize database:**
```bash
python init_db.py
```

5. **Test it works:**
```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

6. **Set up as systemd service** (auto-start on boot):
```bash
sudo cp deploy/superbowl-props.service /etc/systemd/system/
sudo systemctl enable superbowl-props
sudo systemctl start superbowl-props
```

7. **Configure nginx** (optional, for domain/SSL):
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/superbowl-props
sudo ln -s /etc/nginx/sites-available/superbowl-props /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Option 2: Render.com (FREE - Recommended)

Render offers a generous free tier perfect for this app.

### Steps:

1. **Create account** at https://render.com

2. **Connect GitHub:**
   - Push your code to GitHub
   - In Render, click "New" → "Web Service"
   - Connect your GitHub repo

3. **Configure:**
   - **Build Command:** `pip install -r requirements.txt && python init_db.py`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variables:** Add your `.env` values

4. **Deploy!** Render handles everything automatically.

### render.yaml (included)
The `render.yaml` file in this repo auto-configures everything.

---

## Option 3: PythonAnywhere (FREE)

Great for beginners, Python-specific hosting.

### Steps:

1. **Sign up** at https://www.pythonanywhere.com

2. **Upload files:**
   - Go to "Files" tab
   - Upload your project as a zip, or use git:
   ```bash
   git clone https://github.com/yourusername/superbowl-props.git
   ```

3. **Create virtual environment** (in Bash console):
   ```bash
   cd superbowl-props
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python init_db.py
   ```

4. **Configure Web App:**
   - Go to "Web" tab → "Add a new web app"
   - Choose "Flask" and Python 3.10
   - Set source code path: `/home/yourusername/superbowl-props`
   - Set virtualenv path: `/home/yourusername/superbowl-props/venv`

5. **Edit WSGI file:**
   ```python
   import sys
   path = '/home/yourusername/superbowl-props'
   if path not in sys.path:
       sys.path.append(path)
   from app import app as application
   ```

6. **Set environment variables** in Web tab → "Environment variables"

7. **Reload** your web app!

---

## Option 4: Railway.app (FREE tier)

Modern platform with excellent DX.

### Steps:

1. **Sign up** at https://railway.app

2. **Deploy from GitHub:**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repo

3. **Add environment variables** in the dashboard

4. **Done!** Railway auto-detects Python/Flask

---

## Environment Variables

All deployment methods need these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `your-random-secret-key-here` |
| `MASTER_KEY` | Admin login password | `superbowl2026` |
| `MAIL_SERVER` | SMTP server (optional) | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | Email username | `your@email.com` |
| `MAIL_PASSWORD` | Email password/app key | `your-app-password` |

### Generate a Secret Key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Database Notes

- **SQLite** is used for simplicity - the `data/` folder stores `props.db`
- For cloud platforms, the database persists between deploys on Render (with disk) and PythonAnywhere
- Railway requires adding a PostgreSQL database for persistence (or use Render)

---

## SSL/HTTPS

- **Render, Railway, PythonAnywhere**: Automatic HTTPS included
- **Self-hosted**: Use Certbot for free Let's Encrypt certificates:
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d yourdomain.com
  ```

---

## Troubleshooting

### App won't start
```bash
# Check logs
journalctl -u superbowl-props -f

# Test manually
cd /path/to/superbowl-props
source venv/bin/activate
python app.py
```

### Database errors
```bash
# Reinitialize database
rm data/props.db
python init_db.py
```

### Permission issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /path/to/superbowl-props
chmod 755 /path/to/superbowl-props
chmod 664 /path/to/superbowl-props/data/props.db
```
