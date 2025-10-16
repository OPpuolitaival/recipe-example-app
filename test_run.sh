#!/bin/bash

# Test Runner Script for Recipe Application
# Runs Django unit tests with various options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Recipe Application - Test Runner${NC}"
echo "====================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv is not installed.${NC}"
    echo "📦 Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Default values
TEST_PATH="recipes"
VERBOSITY="2"
PARALLEL=""
KEEPDB=""
FAILFAST=""
COVERAGE=""
COVERAGE_HTML=""

# Parse command line arguments
E2E=""
HEADED=""
SLOWMO_MS=""
FUZZ=""
FUZZ_ITERATIONS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            TEST_PATH=""
            shift
            ;;
        --models)
            TEST_PATH="recipes.tests.test_models"
            shift
            ;;
        --views)
            TEST_PATH="recipes.tests.test_views"
            shift
            ;;
        --forms)
            TEST_PATH="recipes.tests.test_forms"
            shift
            ;;
        --urls)
            TEST_PATH="recipes.tests.test_urls"
            shift
            ;;
        --integration)
            TEST_PATH="recipes.tests.test_integration"
            shift
            ;;
        --e2e)
            E2E="true"
            shift
            ;;
        --headed)
            HEADED="--headed"
            shift
            ;;
        --slowmo)
            SLOWMO_MS="$2"
            shift 2
            ;;
        --path)
            TEST_PATH="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL="--parallel"
            shift
            ;;
        --keepdb)
            KEEPDB="--keepdb"
            shift
            ;;
        --failfast)
            FAILFAST="--failfast"
            shift
            ;;
        --coverage)
            COVERAGE="true"
            shift
            ;;
        --coverage-html)
            COVERAGE="true"
            COVERAGE_HTML="true"
            shift
            ;;
        --quiet)
            VERBOSITY="0"
            shift
            ;;
        --verbose)
            VERBOSITY="3"
            shift
            ;;
        --fuzz)
            FUZZ="true"
            shift
            ;;
        --fuzz-iterations)
            FUZZ_ITERATIONS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./test_run.sh [OPTIONS]"
            echo ""
            echo "Test Selection:"
            echo "  --all              Run all tests (default: recipes app only)"
            echo "  --models           Run only model tests"
            echo "  --views            Run only view tests"
            echo "  --forms            Run only form tests"
            echo "  --urls             Run only URL tests"
            echo "  --integration      Run only integration tests"
            echo "  --e2e              Run Playwright end-to-end tests (pytest)"
            echo "  --path PATH        Run specific test path"
            echo ""
            echo "Test Options:"
            echo "  --parallel         Run tests in parallel"
            echo "  --keepdb           Keep test database between runs"
            echo "  --failfast         Stop on first failure"
            echo "  --quiet            Minimal output (verbosity 0)"
            echo "  --verbose          Maximum output (verbosity 3)"
            echo ""
            echo "E2E Viewing Options:"
            echo "  --headed           Show browser UI during Playwright runs (headed mode)"
            echo "  --slowmo MS        Slow down Playwright actions by MS milliseconds (e.g., 250)"
            echo ""
            echo "Coverage Options:"
            echo "  --coverage         Run with coverage report"
            echo "  --coverage-html    Run with HTML coverage report"
            echo ""
            echo "Fuzz Options:"
            echo "  --fuzz             Run Radamsa-based fuzz tests for recipe form input"
            echo "  --fuzz-iterations N   Number of iterations per seed (default: 200)"
            echo ""
            echo "Examples:"
            echo "  ./test_run.sh                          # Run all recipes tests"
            echo "  ./test_run.sh --models                 # Run only model tests"
            echo "  ./test_run.sh --e2e                    # Run Playwright e2e tests (headless)"
            echo "  ./test_run.sh --e2e --headed           # Run Playwright e2e tests with visible browser"
            echo "  ./test_run.sh --e2e --headed --slowmo 250  # Headed with slower actions"
            echo "  ./test_run.sh --coverage               # Run with coverage"
            echo "  ./test_run.sh --parallel --failfast    # Fast parallel testing"
            echo "  ./test_run.sh --coverage-html          # Generate HTML report"
            echo "  ./test_run.sh --fuzz                   # Run Radamsa fuzzing with defaults"
            echo "  ./test_run.sh --fuzz --fuzz-iterations 1000   # Run fuzzing with 1000 iterations/seed"
            echo "  ./test_run.sh --path recipes.tests.test_models.RecipeModelTest"
            echo ""
            echo "Adding New Tests:"
            echo "  1. Create test file in recipes/tests/"
            echo "  2. Run: ./test_run.sh --path recipes.tests.your_test_file"
            echo "  E2E: Create tests in tests_e2e/ and run with --e2e"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# If Fuzz mode, run Radamsa-based fuzzing and exit
if [ -n "$FUZZ" ]; then
    echo -e "${BLUE}🧬 Running Radamsa fuzz tests for recipe form input...${NC}"
    echo ""

    # Ensure project dependencies are installed
    if ! uv run python -c "import django" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Syncing project dependencies (pyproject.toml)...${NC}"
        uv sync
        echo ""
    fi

    # Allow customization of iterations per seed
    if [ -n "$FUZZ_ITERATIONS" ]; then
        export ITERATIONS_PER_SEED="$FUZZ_ITERATIONS"
    fi

    # Run fuzzing inside uv environment so the harness can import Django
    if uv run bash fuzz/radamsa_recipe_forms_fuzz.sh; then
        echo -e "${GREEN}✅ Fuzzing completed without crashes.${NC}"
        exit 0
    else
        status=$?
        echo -e "${RED}❌ Fuzzing detected a crash. See reproducer(s) under fuzz/crashes/.${NC}"
        exit $status
    fi
fi

# If E2E mode, run Playwright end-to-end tests via pytest and exit
if [ -n "$E2E" ]; then
    echo -e "${BLUE}🎭 Running Playwright end-to-end tests...${NC}"
    echo ""

    # Ensure project dependencies are installed
    if ! uv run python -c "import pytest" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Syncing project dependencies (pyproject.toml)...${NC}"
        uv sync
        echo ""
    fi

    # Ensure Playwright browsers are installed
    echo -e "${BLUE}📥 Ensuring Playwright browsers are installed...${NC}"
    uv run python -m playwright install --with-deps || uv run python -m playwright install

    # Run pytest for e2e directory
    PYTEST_OPTS="-q"
    if [ "$VERBOSITY" = "3" ]; then
        PYTEST_OPTS="-vv"
    elif [ "$VERBOSITY" = "0" ]; then
        PYTEST_OPTS="-q"
    fi

    # Append headed/slowmo options if provided
    if [ -n "$HEADED" ]; then
        PYTEST_OPTS="$PYTEST_OPTS $HEADED"
    fi
    if [ -n "$SLOWMO_MS" ]; then
        PYTEST_OPTS="$PYTEST_OPTS --slowmo=$SLOWMO_MS"
    fi

    if [ -d "tests_e2e" ]; then
        DJANGO_ALLOW_ASYNC_UNSAFE=true uv run pytest $PYTEST_OPTS tests_e2e
    else
        echo -e "${RED}❌ tests_e2e directory not found.${NC}"
        exit 1
    fi

    echo ""
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ E2E tests passed!${NC}"
    else
        echo -e "${RED}❌ E2E tests failed.${NC}"
        exit 1
    fi
    exit 0
fi

# Build test command
TEST_CMD="uv run python manage.py test"

if [ -n "$TEST_PATH" ]; then
    TEST_CMD="$TEST_CMD $TEST_PATH"
fi

TEST_CMD="$TEST_CMD --verbosity=$VERBOSITY"

if [ -n "$PARALLEL" ]; then
    TEST_CMD="$TEST_CMD $PARALLEL"
fi

if [ -n "$KEEPDB" ]; then
    TEST_CMD="$TEST_CMD $KEEPDB"
fi

if [ -n "$FAILFAST" ]; then
    TEST_CMD="$TEST_CMD $FAILFAST"
fi

# Show test info
echo -e "${YELLOW}Test Configuration:${NC}"
if [ -z "$TEST_PATH" ]; then
    echo "  Target: All tests"
else
    echo "  Target: $TEST_PATH"
fi
echo "  Verbosity: $VERBOSITY"
[ -n "$PARALLEL" ] && echo "  Parallel: Yes"
[ -n "$KEEPDB" ] && echo "  Keep DB: Yes"
[ -n "$FAILFAST" ] && echo "  Fail Fast: Yes"
[ -n "$COVERAGE" ] && echo "  Coverage: Yes"
echo ""

# Run with or without coverage
if [ -n "$COVERAGE" ]; then
    echo -e "${BLUE}📊 Running tests with coverage...${NC}"
    echo ""

    # Check if coverage is installed
    if ! uv run python -c "import coverage" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Coverage.py not installed. Installing...${NC}"
        uv pip install coverage
        echo ""
    fi

    # Run tests with coverage
    COVERAGE_CMD="uv run coverage run --source='recipes' manage.py test"

    if [ -n "$TEST_PATH" ]; then
        COVERAGE_CMD="$COVERAGE_CMD $TEST_PATH"
    fi

    COVERAGE_CMD="$COVERAGE_CMD --verbosity=$VERBOSITY"
    [ -n "$KEEPDB" ] && COVERAGE_CMD="$COVERAGE_CMD $KEEPDB"
    [ -n "$FAILFAST" ] && COVERAGE_CMD="$COVERAGE_CMD $FAILFAST"

    eval $COVERAGE_CMD

    echo ""
    echo -e "${BLUE}📊 Coverage Report:${NC}"
    echo ""
    uv run coverage report

    if [ -n "$COVERAGE_HTML" ]; then
        echo ""
        echo -e "${BLUE}📄 Generating HTML coverage report...${NC}"
        uv run coverage html
        echo -e "${GREEN}✅ HTML report generated: htmlcov/index.html${NC}"
        echo ""
        echo "Open with:"
        echo "  open htmlcov/index.html        # macOS"
        echo "  xdg-open htmlcov/index.html    # Linux"
    fi
else
    echo -e "${BLUE}🧪 Running tests...${NC}"
    echo ""

    # Run tests
    eval $TEST_CMD
fi

# Show results
echo ""
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}💡 Quick Tips:${NC}"
echo "  - Run specific test: ./test_run.sh --models"
echo "  - Fast feedback: ./test_run.sh --failfast"
echo "  - Coverage report: ./test_run.sh --coverage-html"
echo "  - Keep test DB: ./test_run.sh --keepdb (faster re-runs)"
echo ""
