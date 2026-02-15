#!/bin/bash

# Navigate to backend directory
cd src/backend

# check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed (simple check)
if [ ! -f "installed.flag" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch installed.flag
fi

# Run data generation (needs to be run from src/backend or with correct path)
# We will stay in src/backend for data generation as it seems to work there (imports might be relative or it works by accident)
# Actually, let's just set PYTHONPATH correctly for everything.

# Get Project Root (assuming we are in src/backend now)
PROJECT_ROOT=$(cd ../.. && pwd)
export PYTHONPATH=$PROJECT_ROOT

echo "Generating/Refreshing Data..."
python scripts/generate_data.py

# Start Backend
echo "Starting FastAPI Backend..."
# Run from Project Root to ensure imports like 'src.backend.main' work
cd $PROJECT_ROOT
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
