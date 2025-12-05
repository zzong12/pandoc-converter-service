#!/bin/bash
# Curl test commands for PDF conversion

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "PDF Conversion Curl Tests"
echo "=========================================="
echo ""

# Test 1: Health check
echo "1. Health Check:"
echo "curl -X GET \"$BASE_URL/health\""
curl -X GET "$BASE_URL/health" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Test 2: Markdown to PDF - File Upload
echo "2. Markdown to PDF (File Upload):"
echo "curl -X POST \"$BASE_URL/convert\" -F \"file=@tests/test_files/sample.md\" -F \"from=markdown\" -F \"to=pdf\" -F \"standalone=true\" --output tests/test_files/curl_output_md_to_pdf.pdf"
curl -X POST "$BASE_URL/convert" \
  -F "file=@tests/test_files/sample.md" \
  -F "from=markdown" \
  -F "to=pdf" \
  -F "standalone=true" \
  --output tests/test_files/curl_output_md_to_pdf.pdf

if [ -f tests/test_files/curl_output_md_to_pdf.pdf ]; then
    echo "✓ File created: $(ls -lh tests/test_files/curl_output_md_to_pdf.pdf | awk '{print $5}')"
else
    echo "✗ File creation failed"
fi
echo ""
echo "---"
echo ""

# Test 3: HTML to PDF - File Upload
echo "3. HTML to PDF (File Upload):"
echo "curl -X POST \"$BASE_URL/convert\" -F \"file=@tests/test_files/sample.html\" -F \"from=html\" -F \"to=pdf\" -F \"standalone=true\" --output tests/test_files/curl_output_html_to_pdf.pdf"
curl -X POST "$BASE_URL/convert" \
  -F "file=@tests/test_files/sample.html" \
  -F "from=html" \
  -F "to=pdf" \
  -F "standalone=true" \
  --output tests/test_files/curl_output_html_to_pdf.pdf

if [ -f tests/test_files/curl_output_html_to_pdf.pdf ]; then
    echo "✓ File created: $(ls -lh tests/test_files/curl_output_html_to_pdf.pdf | awk '{print $5}')"
else
    echo "✗ File creation failed"
fi
echo ""
echo "---"
echo ""

# Test 4: Markdown to PDF - JSON endpoint
echo "4. Markdown to PDF (JSON endpoint):"
CONTENT_B64=$(base64 -i tests/test_files/sample.md)
echo "curl -X POST \"$BASE_URL/convert/json\" -H \"Content-Type: application/json\" -d '{\"from\":\"markdown\",\"to\":\"pdf\",\"content\":\"...\",\"standalone\":true}'"
curl -X POST "$BASE_URL/convert/json" \
  -H "Content-Type: application/json" \
  -d "{
    \"from\": \"markdown\",
    \"to\": \"pdf\",
    \"content\": \"$CONTENT_B64\",
    \"standalone\": true
  }" | python3 -c "
import sys, json, base64
result = json.load(sys.stdin)
if result.get('success'):
    content = base64.b64decode(result['content'])
    with open('tests/test_files/curl_output_md_to_pdf_json.pdf', 'wb') as f:
        f.write(content)
    print(f\"✓ File created: {len(content)} bytes\")
else:
    print(f\"✗ Conversion failed: {result.get('error')}\")
"
echo ""
echo "---"
echo ""

# Test 5: JSON-RPC endpoint - Markdown to PDF
echo "5. Markdown to PDF (JSON-RPC endpoint):"
CONTENT_B64=$(base64 -i tests/test_files/sample.md)
echo "curl -X POST \"$BASE_URL/rpc\" -H \"Content-Type: application/json\" -d '{\"jsonrpc\":\"2.0\",\"method\":\"convert\",\"params\":{...},\"id\":\"1\"}'"
curl -X POST "$BASE_URL/rpc" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"convert\",
    \"params\": {
      \"from\": \"markdown\",
      \"to\": \"pdf\",
      \"content\": \"$CONTENT_B64\",
      \"standalone\": true
    },
    \"id\": \"test-1\"
  }" | python3 -c "
import sys, json, base64
result = json.load(sys.stdin)
if 'result' in result and result.get('error') is None:
    content = base64.b64decode(result['result']['content'])
    with open('tests/test_files/curl_output_md_to_pdf_jsonrpc.pdf', 'wb') as f:
        f.write(content)
    print(f\"✓ File created: {len(content)} bytes\")
else:
    print(f\"✗ Conversion failed: {result.get('error')}\")
"
echo ""
echo "---"
echo ""

# Test 6: List supported formats
echo "6. List Supported Formats:"
echo "curl -X GET \"$BASE_URL/formats\""
curl -X GET "$BASE_URL/formats" | python3 -m json.tool | head -30
echo ""
echo "=========================================="
echo "All tests completed!"
echo "=========================================="

