#!/bin/bash

# Navigate to frontend directory
cd src/frontend

# Install dependencies if node_modules is missing
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start Frontend
echo "Starting React Frontend..."
npm run dev
