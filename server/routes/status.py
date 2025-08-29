"""Status and health check API routes."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends

from schemas.document import ServerStatus
from usecases.document_usecase import DocumentUseCase
from usecases.chat_usecase import ChatUseCase
from middleware.auth import get_current_user_optional
from utils.config import GROQ_API_KEY

logger = logging.getLogger(__name__)

router = APIRouter(tags=["status"])

# Initialize use cases
document_usecase = DocumentUseCase()
chat_usecase = ChatUseCase()


@router.get("/", response_model=ServerStatus)
async def get_server_status(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Get server status and configuration."""
    try:
        # Get database status
        db_status = await document_usecase.get_database_status()
        
        # Check API key configuration
        api_key_configured = bool(GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here")
        
        return ServerStatus(
            status="running",
            chunk_count=db_status.get("chunk_count", 0),
            api_key_configured=api_key_configured,
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Error getting server status: {str(e)}")
        return ServerStatus(
            status="error",
            chunk_count=0,
            api_key_configured=False,
            version="1.0.0"
        )


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "message": "Server is running"}
