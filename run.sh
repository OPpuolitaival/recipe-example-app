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
    echo "🗄️  Database not found. Creating migrations and running them..."
    uv run python manage.py makemigrations
    uv run python manage.py migrate

    echo ""
    echo "👤 Creating superuser..."

    # Check if environment variables are set for non-interactive creation
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo "   Creating superuser from environment variables..."
        uv run python manage.py createsuperuser --noinput || echo "   Superuser creation failed."
    elif [ -t 0 ]; then
        echo "   (You'll be prompted for username, email, and password)"
        echo ""
        uv run python manage.py createsuperuser || echo "   Superuser creation skipped or failed. You can create one manually later."
    else
        echo "   ⚠️  Not running in interactive mode, skipping superuser creation."
        echo "   Run manually: uv run python manage.py createsuperuser"
        echo "   Or set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, and DJANGO_SUPERUSER_EMAIL"
    fi
else
    echo "✓ Database exists"
    echo ""
    echo "🔄 Checking for new migrations..."
    uv run python manage.py makemigrations
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
