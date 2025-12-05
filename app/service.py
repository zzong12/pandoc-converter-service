"""Pandoc conversion service implementation."""

import subprocess
import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from app.models import ConvertParams
from app.utils import (
    create_temp_file,
    cleanup_temp_file,
    decode_base64,
    read_file_bytes,
    get_file_extension,
    validate_format,
)

logger = logging.getLogger(__name__)


class PandocService:
    """Service for converting documents using Pandoc."""

    def __init__(self, timeout: int = 300):
        """Initialize Pandoc service.
        
        Args:
            timeout: Maximum execution time in seconds (default: 300)
        """
        self.timeout = timeout
        self.pandoc_path = self._find_pandoc()

    def _find_pandoc(self) -> str:
        """Find pandoc executable path.
        
        Returns:
            Path to pandoc executable
        
        Raises:
            RuntimeError: If pandoc is not found
        """
        # Try common locations
        possible_paths = ['pandoc', '/usr/bin/pandoc', '/usr/local/bin/pandoc']
        
        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
                logger.info(f"Found pandoc at: {path}")
                return path
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        raise RuntimeError("Pandoc not found. Please ensure pandoc is installed.")

    def convert(
        self,
        input_content: bytes,
        from_format: str,
        to_format: str,
        params: Optional[ConvertParams] = None,
        input_file_path: Optional[str] = None,
    ) -> bytes:
        """Convert document from one format to another.
        
        Args:
            input_content: Input document content as bytes
            from_format: Input format (e.g., 'html', 'markdown')
            to_format: Output format (e.g., 'docx', 'pdf')
            params: Optional conversion parameters
            input_file_path: Optional path to input file (if None, creates temp file)
        
        Returns:
            Converted document content as bytes
        
        Raises:
            ValueError: If formats are invalid
            RuntimeError: If conversion fails
        """
        if not validate_format(from_format):
            raise ValueError(f"Invalid input format: {from_format}")
        if not validate_format(to_format):
            raise ValueError(f"Invalid output format: {to_format}")

        # Prepare input file
        input_file = input_file_path
        temp_input = False
        
        if input_file is None:
            input_ext = get_file_extension(from_format)
            input_file = create_temp_file(input_content, suffix=input_ext)
            temp_input = True

        try:
            # Prepare output file
            output_ext = get_file_extension(to_format)
            output_file = create_temp_file(b'', suffix=output_ext)
            temp_output = True

            try:
                # Build pandoc command
                cmd = self._build_command(
                    input_file=input_file,
                    output_file=output_file,
                    from_format=from_format,
                    to_format=to_format,
                    params=params,
                )

                # Execute pandoc
                logger.info(f"Executing pandoc: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=self.timeout,
                    check=True,
                )

                # Read output file
                output_content = read_file_bytes(output_file)
                logger.info(f"Conversion successful: {from_format} -> {to_format}, size: {len(output_content)} bytes")
                
                return output_content

            finally:
                if temp_output:
                    cleanup_temp_file(output_file)

        finally:
            if temp_input:
                cleanup_temp_file(input_file)

    def _build_command(
        self,
        input_file: str,
        output_file: str,
        from_format: str,
        to_format: str,
        params: Optional[ConvertParams] = None,
    ) -> List[str]:
        """Build pandoc command line arguments.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            from_format: Input format
            to_format: Output format
            params: Optional conversion parameters
        
        Returns:
            List of command arguments
        """
        cmd = [self.pandoc_path]

        # Basic format options
        cmd.extend(['-f', from_format])
        cmd.extend(['-t', to_format])

        # Standalone option
        if params and params.standalone:
            cmd.append('--standalone')

        # Template
        if params and params.template:
            cmd.extend(['--template', params.template])

        # Variables
        if params and params.variables:
            for key, value in params.variables.items():
                cmd.extend(['--variable', f'{key}={value}'])

        # Filters
        if params and params.filters:
            for filter_name in params.filters:
                cmd.extend(['--filter', filter_name])

        # Metadata
        if params and params.metadata:
            for key, value in params.metadata.items():
                if isinstance(value, str):
                    cmd.extend(['--metadata', f'{key}={value}'])
                else:
                    # For complex metadata, use JSON
                    import json
                    cmd.extend(['--metadata', f'{key}={json.dumps(value)}'])

        # Extra arguments
        if params and params.extra_args:
            cmd.extend(params.extra_args)

        # Input and output files
        cmd.append(input_file)
        cmd.extend(['-o', output_file])

        return cmd

    def get_version(self) -> str:
        """Get pandoc version.
        
        Returns:
            Pandoc version string
        """
        try:
            result = subprocess.run(
                [self.pandoc_path, '--version'],
                capture_output=True,
                timeout=5,
                check=True,
                text=True,
            )
            # First line contains version info
            version_line = result.stdout.split('\n')[0]
            return version_line.strip()
        except Exception as e:
            logger.error(f"Failed to get pandoc version: {e}")
            return "unknown"

    def list_formats(self) -> Dict[str, List[str]]:
        """List supported input and output formats.
        
        Returns:
            Dictionary with 'input' and 'output' format lists
        """
        try:
            result = subprocess.run(
                [self.pandoc_path, '--list-input-formats'],
                capture_output=True,
                timeout=5,
                check=True,
                text=True,
            )
            input_formats = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]

            result = subprocess.run(
                [self.pandoc_path, '--list-output-formats'],
                capture_output=True,
                timeout=5,
                check=True,
                text=True,
            )
            output_formats = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]

            return {
                'input': input_formats,
                'output': output_formats,
            }
        except Exception as e:
            logger.error(f"Failed to list formats: {e}")
            return {'input': [], 'output': []}

