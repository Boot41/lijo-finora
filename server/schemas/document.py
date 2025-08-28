"""Pydantic schemas for document-related operations."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    filename: str
    chunks_count: int
    metadata: Dict[str, Any]
    document_id: str
    created_at: datetime


class DocumentUrlRequest(BaseModel):
    """Request schema for URL-based document upload."""
    url: str = Field(..., description="URL of the document to process")


class SearchRequest(BaseModel):
    """Request schema for document search."""
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=5, ge=1, le=50, description="Number of results to return")


class SearchResultItem(BaseModel):
    """Individual search result item."""
    text: str
    metadata: Dict[str, Any]
    similarity_score: float


class SearchResponse(BaseModel):
    """Response schema for search results."""
    results: List[SearchResultItem]
    message: str
    total_results: int


class ChatRequest(BaseModel):
    """Request schema for chat."""
    message: str = Field(..., min_length=1, description="Chat message")
    response_length: str = Field(
        default="balanced", 
        pattern="^(brief|balanced|detailed)$",
        description="Response length preference"
    )


class ChatSource(BaseModel):
    """Source information for chat response."""
    filename: str
    pages: List[int] = []
    title: str = ""
    text_preview: str


class ChatResponse(BaseModel):
    """Response schema for chat."""
    response: str
    sources: List[ChatSource]
    message_id: str
    created_at: datetime


class ServerStatus(BaseModel):
    """Server status response."""
    status: str
    chunk_count: int
    api_key_configured: bool
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DatabaseClearResponse(BaseModel):
    """Response for database clear operation."""
    message: str
    chunks_cleared: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
