"""Document data models."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Represents a chunk of a processed document."""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class Document:
    """Represents a processed document."""
    id: str
    filename: str
    source: str
    full_text: str
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any]
    chunks_count: int
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.chunks_count == 0:
            self.chunks_count = len(self.chunks)


@dataclass
class SearchResult:
    """Represents a search result from vector database."""
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    similarity_score: float
    document_id: Optional[str] = None


@dataclass
class ChatMessage:
    """Represents a chat message."""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    sources: List[SearchResult] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.sources is None:
            self.sources = []


@dataclass
class User:
    """Represents a user."""
    id: str
    email: str
    username: str
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
