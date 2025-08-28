"""Chat-related API routes."""

import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse

from schemas.document import ChatRequest, ChatResponse
from usecases.chat_usecase import ChatUseCase
from middleware.auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize use case
chat_usecase = ChatUseCase()


@router.post("/", response_model=ChatResponse)
async def chat_with_documents(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Chat with documents using RAG."""
    try:
        if not chat_usecase.is_chat_available():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chat functionality requires Google Gemini API key"
            )
        
        result = await chat_usecase.chat_with_documents(
            request.message, 
            request.response_length
        )
        
        logger.info(f"Chat response generated for message: {request.message[:50]}...")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate chat response"
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Stream chat response."""
    try:
        if not chat_usecase.is_chat_available():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chat functionality requires Google Gemini API key"
            )
        
        async def generate_response():
            try:
                async for chunk in chat_usecase.chat_stream(
                    request.message, 
                    request.response_length
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming chat: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error in streaming chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in streaming chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream chat response"
        )
