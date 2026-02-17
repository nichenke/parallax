#!/bin/bash
# Quick start script for validation UI

echo "🔍 Starting Parallax Finding Validator..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate

if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt --quiet
fi

# Start the app
echo "Starting UI on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""
python validate_findings.py
