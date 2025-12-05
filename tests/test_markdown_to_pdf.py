#!/usr/bin/env python3
"""Test script for Markdown to PDF conversion."""

import requests
import base64
import sys
from pathlib import Path

# Service URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    print(f"✓ Health check passed: {response.json()}")
    return True

def test_markdown_to_pdf_file_upload():
    """Test Markdown to PDF conversion using file upload."""
    print("\nTesting Markdown to PDF conversion (file upload)...")
    
    test_file = Path(__file__).parent / "test_files" / "sample.md"
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    with open(test_file, 'rb') as f:
        files = {'file': ('sample.md', f, 'text/markdown')}
        data = {
            'from': 'markdown',
            'to': 'pdf',
            'standalone': 'true',
        }
        
        response = requests.post(f"{BASE_URL}/convert", files=files, data=data)
    
    if response.status_code == 200:
        output_file = Path(__file__).parent / "test_files" / "output_markdown_to_pdf.pdf"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"✓ Conversion successful! Output saved to: {output_file}")
        print(f"  Output size: {len(response.content)} bytes")
        return True
    else:
        print(f"✗ Conversion failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False

def test_markdown_to_pdf_json():
    """Test Markdown to PDF conversion using JSON endpoint."""
    print("\nTesting Markdown to PDF conversion (JSON endpoint)...")
    
    test_file = Path(__file__).parent / "test_files" / "sample.md"
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    with open(test_file, 'rb') as f:
        content = f.read()
        content_base64 = base64.b64encode(content).decode('utf-8')
    
    payload = {
        'from': 'markdown',
        'to': 'pdf',
        'content': content_base64,
        'standalone': True,
    }
    
    response = requests.post(f"{BASE_URL}/convert/json", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            output_content = base64.b64decode(result['content'])
            output_file = Path(__file__).parent / "test_files" / "output_markdown_to_pdf_json.pdf"
            with open(output_file, 'wb') as f:
                f.write(output_content)
            print(f"✓ Conversion successful! Output saved to: {output_file}")
            print(f"  Output size: {len(output_content)} bytes")
            return True
        else:
            print(f"✗ Conversion failed: {result.get('error')}")
            return False
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False

def test_markdown_to_pdf_jsonrpc():
    """Test Markdown to PDF conversion using JSON-RPC endpoint."""
    print("\nTesting Markdown to PDF conversion (JSON-RPC endpoint)...")
    
    test_file = Path(__file__).parent / "test_files" / "sample.md"
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    with open(test_file, 'rb') as f:
        content = f.read()
        content_base64 = base64.b64encode(content).decode('utf-8')
    
    payload = {
        'jsonrpc': '2.0',
        'method': 'convert',
        'params': {
            'from': 'markdown',
            'to': 'pdf',
            'content': content_base64,
            'standalone': True,
        },
        'id': 'test-2',
    }
    
    response = requests.post(f"{BASE_URL}/rpc", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if 'error' in result and result['error'] is not None:
            print(f"✗ Conversion failed: {result['error']}")
            return False
        elif 'result' in result:
            output_content = base64.b64decode(result['result']['content'])
            output_file = Path(__file__).parent / "test_files" / "output_markdown_to_pdf_jsonrpc.pdf"
            with open(output_file, 'wb') as f:
                f.write(output_content)
            print(f"✓ Conversion successful! Output saved to: {output_file}")
            print(f"  Output size: {len(output_content)} bytes")
            return True
        else:
            print(f"✗ Unexpected response format: {result}")
            return False
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Markdown to PDF Conversion Tests")
    print("=" * 60)
    
    results = []
    
    # Test health check
    try:
        results.append(("Health Check", test_health()))
    except Exception as e:
        print(f"✗ Health check error: {e}")
        results.append(("Health Check", False))
    
    # Test file upload
    try:
        results.append(("File Upload", test_markdown_to_pdf_file_upload()))
    except Exception as e:
        print(f"✗ File upload test error: {e}")
        results.append(("File Upload", False))
    
    # Test JSON endpoint
    try:
        results.append(("JSON Endpoint", test_markdown_to_pdf_json()))
    except Exception as e:
        print(f"✗ JSON endpoint test error: {e}")
        results.append(("JSON Endpoint", False))
    
    # Test JSON-RPC endpoint
    try:
        results.append(("JSON-RPC Endpoint", test_markdown_to_pdf_jsonrpc()))
    except Exception as e:
        print(f"✗ JSON-RPC endpoint test error: {e}")
        results.append(("JSON-RPC Endpoint", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())

