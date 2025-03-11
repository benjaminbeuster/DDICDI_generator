#!/bin/bash
set -e

echo "Starting app_service_startup.sh"
echo "Current directory: $(pwd)"
echo "Listing directory contents:"
ls -la

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt
echo "Requirements installed successfully."

# Start gunicorn
echo "Starting gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers=2 --log-level=info app:server 