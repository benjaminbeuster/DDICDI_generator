#!/bin/bash
set -e

echo "Starting application..."
echo "Environment: $APP_ENV"
echo "Working directory: $(pwd)"
echo "Files in directory:"
ls -la

# Install requirements if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    echo "Dependencies installed successfully."
fi

# Set default timeout (10 minutes)
TIMEOUT=${TIMEOUT:-600}

echo "Starting gunicorn with timeout: $TIMEOUT seconds"
gunicorn --bind=0.0.0.0:8000 --timeout $TIMEOUT --workers=2 --log-level=info app:server