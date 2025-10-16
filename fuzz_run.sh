#!/usr/bin/env bash
set -euo pipefail

# Simple runner for Atheris fuzzing harness
# Usage:
#   ./fuzz_run.sh [additional atheris/libFuzzer flags]
# Examples:
#   ./fuzz_run.sh -runs=0 -max_len=4096 -timeout=5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

export DJANGO_SETTINGS_MODULE=recipe_project.settings

if ! python -c "import atheris" >/dev/null 2>&1; then
  echo "atheris is not installed in this environment. Install with one of:"
  echo "  uv sync --group fuzz    # uses optional deps declared in pyproject.toml"
  echo "  pip install 'atheris>=2.3.0; platform_python_implementation == \"CPython\" and python_version < \"3.13\"'"
  echo "\nNote: Atheris supports CPython only and typically Python < 3.13; building from source may require a C toolchain (e.g., Xcode CLT on macOS)."
  exit 1
fi

python -m atheris "$PROJECT_ROOT/fuzz/atheris_recipe_forms_fuzz.py" -rss_limit_mb=2048 "$@"
