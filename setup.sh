#!/bin/bash

# Zenafide HR AI Tool Setup Script
echo "🚀 Setting up Zenafide HR AI Tool..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please update backend/.env with your API keys:"
    echo "   - AIRTABLE_API_KEY"
    echo "   - AIRTABLE_BASE_ID"
    echo "   - OPENAI_API_KEY"
fi

cd ..

# Setup frontend
echo "📦 Setting up frontend..."
cd frontend

# Install Node.js dependencies
npm install

# Copy environment file
if [ ! -f ".env.local" ]; then
    cp .env.local.example .env.local
fi

cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your API keys"
echo "2. Create Airtable base with the required tables (see README.md)"
echo "3. Start the backend: cd backend && source venv/bin/activate && uvicorn app:app --reload"
echo "4. Start the frontend: cd frontend && npm run dev"
echo "5. Run seed data: cd backend && python seed_data.py"
echo ""
echo "🌐 Access the application at http://localhost:3000"
