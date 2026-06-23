#!/bin/bash
echo "===================================="
echo " Backero - Viral Video Production API"
echo "===================================="

# Create venv if missing
if [ ! -d "venv" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install
echo "[2/3] Installing dependencies..."
pip install -r requirements.txt -q

# Start
echo "[3/3] Starting server on http://localhost:8000"
echo ""
echo "  API Docs:   http://localhost:8000/docs"
echo "  Health:     http://localhost:8000/health"
echo "  Frontend:   Open your frontend at http://localhost:5173"
echo ""
echo "  Press Ctrl+C to stop"
echo "===================================="
uvicorn main:app --reload --host 0.0.0.0 --port 8000
