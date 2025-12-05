#!/bin/bash
# Test runner script for Pandoc Converter Service

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "=========================================="
echo "Pandoc Converter Service Test Suite"
echo "=========================================="
echo "Service URL: $BASE_URL"
echo ""

# Check if service is running
echo "Checking service health..."
if ! curl -f -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo "Error: Service is not running at $BASE_URL"
    echo "Please start the service first:"
    echo "  docker-compose up -d"
    echo "  or"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "✓ Service is running"
echo ""

# Install test dependencies if needed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip3 install requests
fi

# Run tests
echo "Running HTML to DOCX tests..."
python3 tests/test_html_to_docx.py

echo ""
echo "Running Markdown to PDF tests..."
python3 tests/test_markdown_to_pdf.py

echo ""
echo "=========================================="
echo "All tests completed!"
echo "=========================================="

