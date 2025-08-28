"""Document-related API routes."""

import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import StreamingResponse

from schemas.document import (
    DocumentUploadResponse, 
    DocumentUrlRequest, 
    SearchRequest, 
    SearchResponse,
    DatabaseClearResponse
)
from schemas.auth import UserResponse
from usecases.document_usecase import DocumentUseCase
from middleware.auth import get_current_user_optional
from middleware.error_handler import *

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize use case
document_usecase = DocumentUseCase()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Upload and process a document file."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file provided"
            )
        
        # Process document
        result = await document_usecase.upload_file(file_content, file.filename)
        
        logger.info(f"Document uploaded successfully: {file.filename}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in document upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document"
        )


@router.post("/upload-url", response_model=DocumentUploadResponse)
async def upload_document_url(
    request: DocumentUrlRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Process a document from URL."""
    try:
        result = await document_usecase.upload_url(request.url)
        
        logger.info(f"Document from URL processed successfully: {request.url}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in URL upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document from URL"
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Search documents in the vector database."""
    try:
        result = await document_usecase.search_documents(request.query, request.limit)
        
        logger.info(f"Search completed: {request.query} - {len(result.results)} results")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search documents"
        )


@router.delete("/database", response_model=DatabaseClearResponse)
async def clear_database(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Clear the vector database."""
    try:
        result = await document_usecase.clear_database()
        
        logger.info("Database cleared successfully")
        return DatabaseClearResponse(
            message=result["message"],
            chunks_cleared=result["chunks_cleared"]
        )
        
    except ValueError as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error clearing database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear database"
        )
