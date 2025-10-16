#!/bin/bash

# Recipe Application - Quick Start Script
# This script sets up the environment and runs the Django development server

set -e  # Exit on error

echo "🚀 Recipe Application - Quick Start"
echo "===================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "✓ uv is installed"
echo ""

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync

echo ""
echo "✓ Dependencies installed"
echo ""

# Check if database exists
if [ ! -f "db.sqlite3" ]; then
    echo "🗄️  Database not found. Running migrations..."
    uv run python manage.py migrate

    echo ""
    echo "👤 Creating superuser..."
    echo "   (You'll be prompted for username, email, and password)"
    echo ""
    uv run python manage.py createsuperuser
else
    echo "✓ Database exists"
    echo ""
    echo "🔄 Running migrations (if any)..."
    uv run python manage.py migrate
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting development server..."
echo "   Access the app at: http://localhost:8000"
echo "   Admin panel at: http://localhost:8000/admin/"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Run the development server
uv run python manage.py runserver
