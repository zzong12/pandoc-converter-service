"""Pydantic data models for the Pandoc converter service."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class JSONRPCRequest(BaseModel):
    """JSON-RPC request model."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name")
    params: Dict[str, Any] = Field(..., description="Method parameters")
    id: Optional[str] = Field(default=None, description="Request ID")


class JSONRPCResponse(BaseModel):
    """JSON-RPC response model."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    result: Optional[Any] = Field(default=None, description="Result data")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")
    id: Optional[str] = Field(default=None, description="Request ID")


class ConvertParams(BaseModel):
    """Parameters for document conversion."""
    from_format: str = Field(..., alias="from", description="Input format (e.g., html, markdown, docx)")
    to_format: str = Field(..., alias="to", description="Output format (e.g., docx, pdf, html)")
    content: Optional[str] = Field(default=None, description="Base64 encoded document content")
    standalone: Optional[bool] = Field(default=False, description="Produce standalone document")
    template: Optional[str] = Field(default=None, description="Template file path or name")
    variables: Optional[Dict[str, str]] = Field(default=None, description="Variables for template")
    filters: Optional[List[str]] = Field(default=None, description="Pandoc filters to apply")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Document metadata")
    output_file: Optional[str] = Field(default=None, description="Output file path (optional)")
    extra_args: Optional[List[str]] = Field(default=None, description="Extra pandoc arguments")

    class Config:
        populate_by_name = True


class ConvertRequest(BaseModel):
    """RESTful convert request model."""
    from_format: str = Field(..., alias="from", description="Input format")
    to_format: str = Field(..., alias="to", description="Output format")
    content: Optional[str] = Field(default=None, description="Text content (if not using file upload)")
    standalone: Optional[bool] = Field(default=False, description="Produce standalone document")
    template: Optional[str] = Field(default=None, description="Template file path or name")
    variables: Optional[Dict[str, str]] = Field(default=None, description="Variables for template")
    filters: Optional[List[str]] = Field(default=None, description="Pandoc filters to apply")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Document metadata")
    extra_args: Optional[List[str]] = Field(default=None, description="Extra pandoc arguments")

    class Config:
        populate_by_name = True


class ConvertResponse(BaseModel):
    """Convert response model."""
    success: bool = Field(..., description="Whether conversion was successful")
    from_format: str = Field(..., description="Input format")
    to_format: str = Field(..., description="Output format")
    content: Optional[str] = Field(default=None, description="Base64 encoded output content")
    filename: Optional[str] = Field(default=None, description="Output filename")
    message: Optional[str] = Field(default=None, description="Response message")
    error: Optional[str] = Field(default=None, description="Error message if failed")

