#!/bin/bash

# REST API Template - Development Startup Script

echo "🚀 REST API Template - Development Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env.local exists, if not copy from .env
if [ ! -f ".env.local" ]; then
    echo "⚙️  Creating .env.local from template..."
    cp .env .env.local
    echo "✅ .env.local created - please update with your configuration"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "🎯 Setup complete! Choose how to run:"
echo "1. Development mode (with reload)"
echo "2. Production mode"
echo "3. Docker mode"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🔄 Starting in development mode with hot reload..."
        export $(cat .env.local | xargs)
        uvicorn main:app --host 0.0.0.0 --port ${SERVER_PORT:-8000} --reload
        ;;
    2)
        echo "🚀 Starting in production mode..."
        export $(cat .env.local | xargs)
        python main.py
        ;;
    3)
        echo "🐳 Starting with Docker..."
        docker-compose up --build
        ;;
    *)
        echo "❌ Invalid choice. Starting in development mode..."
        export $(cat .env.local | xargs)
        uvicorn main:app --host 0.0.0.0 --port ${SERVER_PORT:-8000} --reload
        ;;
esac