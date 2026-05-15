#!/usr/bin/env bash
# install.sh — Install twat-mp locally
# Parallel processing utilities using Pathos mpprocessing library
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing twat-mp..."
uv pip install -e . 2>/dev/null || pip install -e .
echo "Done."
