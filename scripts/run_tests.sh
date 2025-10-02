#!/bin/bash
# Test runner for NLBT

set -e

echo "🧪 Running NLBT tests..."

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "📦 Installing pytest..."
    pip install pytest pytest-progress
fi

# Run tests with progress bar
echo "Running unit tests..."
pytest -q --tb=short tests/

echo "✅ All tests passed!"
