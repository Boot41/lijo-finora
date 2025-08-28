"""Business logic for chat operations."""

import sys
import uuid
from pathlib import Path
from typing import List, Dict, Any, Generator
from datetime import datetime

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.chat_gemini import GeminiChatInterface
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from models.document import ChatMessage, SearchResult
from schemas.document import ChatResponse, ChatSource
from utils.config import GOOGLE_API_KEY


class ChatUseCase:
    """Use case for chat operations."""
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.chat_interface = None
        
        # Initialize chat interface if API key is available
        if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here":
            self.chat_interface = GeminiChatInterface(response_length="balanced")
    
    def is_chat_available(self) -> bool:
        """Check if chat functionality is available."""
        return self.chat_interface is not None
    
    async def chat_with_documents(
        self, 
        message: str, 
        response_length: str = "balanced"
    ) -> ChatResponse:
        """Generate chat response with document context."""
        if not self.chat_interface:
            raise ValueError("Chat functionality requires Google Gemini API key")
        
        try:
            # Update response length
            self.chat_interface.set_response_length(response_length)
            
            # Get relevant context
            query_embedding = self.embedding_generator.embed_text(message)
            context = self.vector_store.search(query_embedding, limit=5)
            
            # Generate response
            response = ""
            for chunk in self.chat_interface.get_streaming_response(message, context):
                response += chunk
            
            # Format sources
            sources = []
            for chunk in context:
                metadata = chunk['metadata']
                source = ChatSource(
                    filename=metadata.get('filename', 'Unknown'),
                    pages=metadata.get('page_numbers', []),
                    title=metadata.get('title', ''),
                    text_preview=chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                )
                sources.append(source)
            
            message_id = str(uuid.uuid4())
            
            return ChatResponse(
                response=response,
                sources=[],
                message_id=message_id,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            raise ValueError(f"Error generating chat response: {str(e)}")
    
    async def chat_stream(
        self, 
        message: str, 
        response_length: str = "balanced"
    ) -> Generator[Dict[str, Any], None, None]:
        """Generate streaming chat response."""
        if not self.chat_interface:
            raise ValueError("Chat functionality requires Google Gemini API key")
        
        try:
            # Update response length
            self.chat_interface.set_response_length(response_length)
            
            # Get relevant context
            query_embedding = self.embedding_generator.embed_text(message)
            context = self.vector_store.search(query_embedding, limit=5)
            
            # Stream response chunks
            for chunk in self.chat_interface.get_streaming_response(message, context):
                yield {"chunk": chunk}
            
            # Send sources at the end
            sources = []
            for chunk in context:
                metadata = chunk['metadata']
                source_info = {
                    "filename": metadata.get('filename', 'Unknown'),
                    "pages": metadata.get('page_numbers', []),
                    "title": metadata.get('title', ''),
                    "text_preview": chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                }
                sources.append(source_info)
            
            yield {"sources": sources}
            
        except Exception as e:
            raise ValueError(f"Error in streaming chat: {str(e)}")
