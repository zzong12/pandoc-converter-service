"""FastAPI application for Pandoc document conversion service."""

import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import ValidationError

from app.models import (
    JSONRPCRequest,
    JSONRPCResponse,
    ConvertRequest,
    ConvertResponse,
    ConvertParams,
)
from app.service import PandocService
from app.utils import decode_base64, encode_base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pandoc Converter Service",
    description="HTTP service for document conversion using Pandoc",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pandoc service
pandoc_service = PandocService()


@app.get("/")
async def root():
    """API information endpoint."""
    return {
        "name": "Pandoc Converter Service",
        "version": "1.0.0",
        "description": "HTTP service for document conversion using Pandoc",
        "pandoc_version": pandoc_service.get_version(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if pandoc is available
        version = pandoc_service.get_version()
        return {
            "status": "healthy",
            "pandoc_version": version,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/formats")
async def list_formats():
    """List supported input and output formats."""
    try:
        formats = pandoc_service.list_formats()
        return formats
    except Exception as e:
        logger.error(f"Failed to list formats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list formats: {str(e)}")


@app.post("/rpc")
async def jsonrpc_endpoint(request: JSONRPCRequest):
    """JSON-RPC endpoint for document conversion.
    
    Compatible with pandoc server mode interface.
    """
    try:
        if request.method != "convert":
            return JSONRPCResponse(
                error={
                    "code": -32601,
                    "message": f"Method not found: {request.method}",
                },
                id=request.id,
            ).model_dump()

        # Parse convert parameters
        try:
            params = ConvertParams(**request.params)
        except ValidationError as e:
            return JSONRPCResponse(
                error={
                    "code": -32602,
                    "message": "Invalid params",
                    "data": str(e),
                },
                id=request.id,
            ).model_dump()

        # Validate content
        if not params.content:
            return JSONRPCResponse(
                error={
                    "code": -32602,
                    "message": "Missing required parameter: content",
                },
                id=request.id,
            ).model_dump()

        # Decode content
        try:
            input_content = decode_base64(params.content)
        except ValueError as e:
            return JSONRPCResponse(
                error={
                    "code": -32602,
                    "message": f"Invalid base64 content: {str(e)}",
                },
                id=request.id,
            ).model_dump()

        # Perform conversion
        try:
            output_content = pandoc_service.convert(
                input_content=input_content,
                from_format=params.from_format,
                to_format=params.to_format,
                params=params,
            )

            # Encode output
            output_base64 = encode_base64(output_content)

            return JSONRPCResponse(
                result={
                    "from": params.from_format,
                    "to": params.to_format,
                    "content": output_base64,
                },
                id=request.id,
            ).model_dump()

        except ValueError as e:
            return JSONRPCResponse(
                error={
                    "code": -32602,
                    "message": f"Invalid format: {str(e)}",
                },
                id=request.id,
            ).model_dump()
        except RuntimeError as e:
            return JSONRPCResponse(
                error={
                    "code": -32000,
                    "message": f"Conversion failed: {str(e)}",
                },
                id=request.id,
            ).model_dump()
        except Exception as e:
            logger.error(f"Unexpected error in conversion: {e}", exc_info=True)
            return JSONRPCResponse(
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
                id=request.id,
            ).model_dump()

    except Exception as e:
        logger.error(f"Unexpected error in JSON-RPC endpoint: {e}", exc_info=True)
        return JSONRPCResponse(
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}",
            },
            id=request.id if hasattr(request, 'id') else None,
        ).model_dump()


@app.post("/convert")
async def convert_endpoint(
    from_format: str = Form(..., alias="from"),
    to_format: str = Form(..., alias="to"),
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None),
    standalone: Optional[bool] = Form(False),
    template: Optional[str] = Form(None),
    variables: Optional[str] = Form(None),  # JSON string
    filters: Optional[str] = Form(None),  # Comma-separated
    metadata: Optional[str] = Form(None),  # JSON string
    extra_args: Optional[str] = Form(None),  # JSON array string
):
    """RESTful endpoint for document conversion.
    
    Supports both file upload and text content.
    """
    try:
        # Get input content
        input_content = None
        if file:
            input_content = await file.read()
        elif content:
            # Try to decode as base64 first, if fails use as plain text
            try:
                input_content = decode_base64(content)
            except ValueError:
                input_content = content.encode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Either 'file' or 'content' must be provided")

        # Parse optional parameters
        import json
        variables_dict = None
        if variables:
            try:
                variables_dict = json.loads(variables)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in 'variables' parameter")

        filters_list = None
        if filters:
            filters_list = [f.strip() for f in filters.split(',') if f.strip()]

        metadata_dict = None
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in 'metadata' parameter")

        extra_args_list = None
        if extra_args:
            try:
                extra_args_list = json.loads(extra_args)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in 'extra_args' parameter")

        # Create params object
        params = ConvertParams(
            from_format=from_format,
            to_format=to_format,
            standalone=standalone,
            template=template,
            variables=variables_dict,
            filters=filters_list,
            metadata=metadata_dict,
            extra_args=extra_args_list,
        )

        # Perform conversion
        output_content = pandoc_service.convert(
            input_content=input_content,
            from_format=from_format,
            to_format=to_format,
            params=params,
        )

        # Get extension from format
        from app.utils import get_file_extension
        ext = get_file_extension(to_format)
        filename = f"output{ext}"

        # Return file response
        return Response(
            content=output_content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid format: {str(e)}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in convert endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/convert/json")
async def convert_json_endpoint(request: ConvertRequest):
    """RESTful JSON endpoint for document conversion."""
    try:
        # Get input content
        if not request.content:
            raise HTTPException(status_code=400, detail="'content' field is required")

        # Try to decode as base64 first, if fails use as plain text
        try:
            input_content = decode_base64(request.content)
        except ValueError:
            input_content = request.content.encode('utf-8')

        # Create params object
        params = ConvertParams(
            from_format=request.from_format,
            to_format=request.to_format,
            standalone=request.standalone,
            template=request.template,
            variables=request.variables,
            filters=request.filters,
            metadata=request.metadata,
            extra_args=request.extra_args,
        )

        # Perform conversion
        output_content = pandoc_service.convert(
            input_content=input_content,
            from_format=request.from_format,
            to_format=request.to_format,
            params=params,
        )

        # Encode output
        output_base64 = encode_base64(output_content)

        return ConvertResponse(
            success=True,
            from_format=request.from_format,
            to_format=request.to_format,
            content=output_base64,
            message="Conversion successful",
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid format: {str(e)}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in convert/json endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

