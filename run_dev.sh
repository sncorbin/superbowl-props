#!/bin/bash

# Quick start script for development
# Run this to quickly start the app locally

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Super Bowl Props - Development Server"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Initialize database if needed
if [ ! -f "data/superbowl_props.db" ]; then
    echo "Initializing database..."
    python init_db.py
fi

echo ""
echo "Starting development server..."
echo "Open http://localhost:5000 in your browser"
echo ""
echo "Default login: admin@example.com / admin123"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"
echo ""

# Run the development server
python app.py
