#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SEEDS_DIR="$SCRIPT_DIR/seeds"
HARNESS="$SCRIPT_DIR/radamsa_recipe_forms_harness.py"
CRASH_DIR="$SCRIPT_DIR/crashes"
ITERATIONS_PER_SEED=${ITERATIONS_PER_SEED:-200}
PYTHON_BIN=${PYTHON_BIN:-python}

export DJANGO_SETTINGS_MODULE=recipe_project.settings

if ! command -v radamsa >/dev/null 2>&1; then
  echo "Error: radamsa not found in PATH." >&2
  echo "Install from https://gitlab.com/akihe/radamsa (e.g., brew install radamsa on macOS)" >&2
  exit 127
fi

if [ ! -d "$SEEDS_DIR" ]; then
  echo "Seed directory not found: $SEEDS_DIR" >&2
  exit 1
fi

mkdir -p "$CRASH_DIR"

# Quick import check to ensure Django is available
if ! $PYTHON_BIN -c "import django" >/dev/null 2>&1; then
  echo "Python 'django' package not available in current environment." >&2
  echo "Activate your venv or run: pip install -r requirements or 'uv sync' if used." >&2
  exit 1
fi

# Verify harness is executable
if [ ! -x "$HARNESS" ]; then
  chmod +x "$HARNESS" || true
fi

echo "Running Radamsa fuzzing on recipe form inputs..."
echo "Seeds: $SEEDS_DIR | Iterations per seed: $ITERATIONS_PER_SEED"

total_cases=0
start_ts=$(date +%s)
for seed in "$SEEDS_DIR"/*.txt; do
  [ -e "$seed" ] || continue
  echo "Seed: $(basename "$seed")"
  for ((i=1; i<=ITERATIONS_PER_SEED; i++)); do
    tmp=$(mktemp)
    if ! radamsa "$seed" > "$tmp"; then
      echo "Radamsa failed on iteration $i for $seed" >&2
      rm -f "$tmp"
      exit 2
    fi
    if ! "$HARNESS" < "$tmp"; then
      crash_file="$CRASH_DIR/$(basename "$seed")_iter_${i}_$(date +%s).post"
      mv "$tmp" "$crash_file"
      echo "Crash detected. Reproducer saved to: $crash_file" >&2
      exit 3
    fi
    rm -f "$tmp"
    total_cases=$((total_cases+1))
    # Print a heartbeat every 100 cases
    if (( total_cases % 100 == 0 )); then
      echo "... $total_cases cases ok"
    fi
  done
done
end_ts=$(date +%s)
duration=$((end_ts - start_ts))
echo "Fuzzing completed successfully. Total cases: $total_cases in ${duration}s"
