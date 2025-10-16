#!/usr/bin/env bash
# Compatibility wrapper to the main test runner script
# Allows invoking `./run_test.sh` as requested in documentation or tasks
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/test_run.sh" "$@"
