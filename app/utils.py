"""Utility functions for file handling and encoding."""

import base64
import os
import tempfile
import shutil
from typing import Optional, Tuple
from pathlib import Path


def create_temp_file(content: bytes, suffix: str = "") -> str:
    """Create a temporary file with given content.
    
    Args:
        content: File content as bytes
        suffix: File suffix (e.g., '.html', '.md')
    
    Returns:
        Path to the temporary file
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
        return path
    except Exception:
        os.close(fd)
        raise


def create_temp_dir() -> str:
    """Create a temporary directory.
    
    Returns:
        Path to the temporary directory
    """
    return tempfile.mkdtemp()


def cleanup_temp_file(path: str) -> None:
    """Remove a temporary file.
    
    Args:
        path: Path to the file to remove
    """
    try:
        if os.path.isfile(path):
            os.remove(path)
    except Exception:
        pass


def cleanup_temp_dir(path: str) -> None:
    """Remove a temporary directory and all its contents.
    
    Args:
        path: Path to the directory to remove
    """
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
    except Exception:
        pass


def decode_base64(content: str) -> bytes:
    """Decode base64 encoded content.
    
    Args:
        content: Base64 encoded string
    
    Returns:
        Decoded bytes
    
    Raises:
        ValueError: If content is not valid base64
    """
    try:
        return base64.b64decode(content)
    except Exception as e:
        raise ValueError(f"Invalid base64 content: {str(e)}")


def encode_base64(content: bytes) -> str:
    """Encode content to base64.
    
    Args:
        content: Content as bytes
    
    Returns:
        Base64 encoded string
    """
    return base64.b64encode(content).decode('utf-8')


def read_file_bytes(file_path: str) -> bytes:
    """Read file content as bytes.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File content as bytes
    """
    with open(file_path, 'rb') as f:
        return f.read()


def get_file_extension(format_name: str) -> str:
    """Get file extension for a format name.
    
    Args:
        format_name: Format name (e.g., 'html', 'markdown', 'docx')
    
    Returns:
        File extension with dot (e.g., '.html', '.md', '.docx')
    """
    format_map = {
        'html': '.html',
        'markdown': '.md',
        'md': '.md',
        'docx': '.docx',
        'pdf': '.pdf',
        'latex': '.tex',
        'tex': '.tex',
        'rtf': '.rtf',
        'odt': '.odt',
        'epub': '.epub',
        'txt': '.txt',
        'plain': '.txt',
    }
    return format_map.get(format_name.lower(), f'.{format_name}')


def validate_format(format_name: str) -> bool:
    """Validate if format name is supported by pandoc.
    
    Args:
        format_name: Format name to validate
    
    Returns:
        True if format is likely supported
    """
    # Basic validation - pandoc supports many formats
    # This is a simple check, actual validation happens in pandoc
    if not format_name or len(format_name) < 2:
        return False
    return True

