#!/bin/bash
set -e

# Echo deployment info
echo "Deployment started"
echo "Current directory: $(pwd)"
echo "Python path: $(which python || echo 'Not found')"
echo "Python version: $(python --version 2>&1 || echo 'No Python')"

# Check if we are in the correct directory
if [ ! -f "requirements.txt" ]; then
  echo "Error: requirements.txt not found."
  exit 1
fi

# Find Python executable - try multiple possibilities
PYTHON_EXECUTABLE=""
for python_cmd in python3 python python3.12 python3.11 python3.10 python3.9; do
  if command -v $python_cmd > /dev/null 2>&1; then
    PYTHON_EXECUTABLE=$python_cmd
    echo "Using Python: $PYTHON_EXECUTABLE - $($PYTHON_EXECUTABLE --version 2>&1)"
    break
  fi
done

if [ -z "$PYTHON_EXECUTABLE" ]; then
  echo "Error: Python executable not found."
  echo "Looking in common locations..."
  
  # Try common locations
  for py_path in /usr/bin/python3 /usr/local/bin/python3 /home/site/wwwroot/env/bin/python; do
    if [ -f "$py_path" ]; then
      PYTHON_EXECUTABLE=$py_path
      echo "Found Python at: $PYTHON_EXECUTABLE"
      break
    fi
  done
  
  if [ -z "$PYTHON_EXECUTABLE" ]; then
    echo "Error: Python not found in any common location."
    exit 1
  fi
fi

# Install Python packages
echo "Installing Python packages using $PYTHON_EXECUTABLE..."
$PYTHON_EXECUTABLE -m pip install -r requirements.txt || {
  echo "Failed to install packages using pip. Trying alternative method..."
  $PYTHON_EXECUTABLE -m ensurepip --upgrade
  $PYTHON_EXECUTABLE -m pip install --upgrade pip
  $PYTHON_EXECUTABLE -m pip install -r requirements.txt
}

# Make startup scripts executable
echo "Making startup scripts executable..."
chmod +x startup.sh 2>/dev/null || echo "Note: startup.sh permission change failed (might not exist)"
chmod +x app_service_startup.sh 2>/dev/null || echo "Note: app_service_startup.sh permission change failed (might not exist)"

echo "Deployment completed successfully." 