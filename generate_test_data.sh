#!/bin/bash

# Generate Test Data Script
# Generates sample recipes for testing the application

set -e

echo "🧪 Generating test data for Recipe Application"
echo "=============================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Parse command line arguments
RECIPES=10
CLEAR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --recipes)
            RECIPES="$2"
            shift 2
            ;;
        --clear)
            CLEAR="--clear"
            shift
            ;;
        -h|--help)
            echo "Usage: ./generate_test_data.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --recipes N    Number of recipes to generate (default: 10)"
            echo "  --clear        Clear existing data before generating"
            echo "  -h, --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./generate_test_data.sh                    # Generate 10 recipes"
            echo "  ./generate_test_data.sh --recipes 20       # Generate 20 recipes"
            echo "  ./generate_test_data.sh --clear            # Clear data and generate 10"
            echo "  ./generate_test_data.sh --recipes 5 --clear # Clear and generate 5"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

if [ -n "$CLEAR" ]; then
    echo "⚠️  Warning: This will delete all existing recipes and ingredients!"
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo "📝 Generating $RECIPES test recipes..."
if [ -n "$CLEAR" ]; then
    echo "🗑️  Clearing existing data..."
fi
echo ""

# Run the Django management command
uv run python manage.py generate_test_data --recipes "$RECIPES" $CLEAR

echo ""
echo "✅ Done!"
echo "🌐 Visit http://localhost:8000 to see the recipes"
echo ""
echo "💡 Tips:"
echo "   - Run ./generate_test_data.sh --recipes 20 to generate more recipes"
echo "   - Run ./generate_test_data.sh --clear to reset and regenerate data"
