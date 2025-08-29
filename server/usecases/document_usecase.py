"""Business logic for document operations."""

import os
import sys
import uuid
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.document_processor import DocumentProcessor
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from models.document import Document, DocumentChunk, SearchResult
from schemas.document import DocumentUploadResponse, SearchResponse, SearchResultItem


class DocumentUseCase:
    """Use case for document operations."""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
    
    async def upload_file(self, file_content: bytes, filename: str) -> DocumentUploadResponse:
        """Process and store uploaded file."""
        # Validate file extension
        allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
        file_extension = Path(filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise ValueError(f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        try:
            # Process document
            result = self.doc_processor.process_document(temp_path)
            
            if not result or not result.get('chunks'):
                raise ValueError("No content extracted from document")
            
            # Create document model
            document_id = str(uuid.uuid4())
            chunks = []
            embeddings = []
            
            for chunk_data in result['chunks']:
                chunk_id = str(uuid.uuid4())
                embedding = self.embedding_generator.embed_text(chunk_data["text"])
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    text=chunk_data["text"],
                    metadata={**chunk_data.get("metadata", {}), "document_id": document_id},
                    embedding=embedding
                )
                chunks.append(chunk)
                embeddings.append(embedding)
            
            document = Document(
                id=document_id,
                filename=filename,
                source=temp_path,
                full_text=result['full_text'],
                chunks=chunks,
                metadata=result['metadata'],
                chunks_count=len(chunks)
            )
            
            # Store in vector database
            chunk_dicts = [
                {
                    "text": chunk.text,
                    "vector": chunk.embedding,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ]
            self.vector_store.add_chunks(chunk_dicts)
            
            return DocumentUploadResponse(
                filename=filename,
                chunks_count=len(chunks),
                metadata=result['metadata'],
                document_id=document_id,
                created_at=document.created_at
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    async def upload_url(self, url: str) -> DocumentUploadResponse:
        """Process and store document from URL."""
        try:
            # Process document from URL
            result = self.doc_processor.process_document(url)
            
            if not result or not result.get('chunks'):
                raise ValueError("No content extracted from URL")
            
            # Create document model
            document_id = str(uuid.uuid4())
            chunks = []
            embeddings = []
            
            for chunk_data in result['chunks']:
                chunk_id = str(uuid.uuid4())
                embedding = self.embedding_generator.embed_text(chunk_data["text"])
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    text=chunk_data["text"],
                    metadata={**chunk_data.get("metadata", {}), "document_id": document_id},
                    embedding=embedding
                )
                chunks.append(chunk)
                embeddings.append(embedding)
            
            document = Document(
                id=document_id,
                filename=result['metadata'].get('source', url),
                source=url,
                full_text=result['full_text'],
                chunks=chunks,
                metadata=result['metadata'],
                chunks_count=len(chunks)
            )
            
            # Store in vector database
            chunk_dicts = [
                {
                    "text": chunk.text,
                    "vector": chunk.embedding,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ]
            self.vector_store.add_chunks(chunk_dicts)
            
            return DocumentUploadResponse(
                filename=document.filename,
                chunks_count=len(chunks),
                metadata=result['metadata'],
                document_id=document_id,
                created_at=document.created_at
            )
            
        except Exception as e:
            raise ValueError(f"Error processing URL: {str(e)}")
    
    async def search_documents(self, query: str, limit: int = 5) -> SearchResponse:
        """Search documents in vector database."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.embed_text(query)
            
            # Search vector database
            results = self.vector_store.search(query_embedding, limit=limit)
            
            if not results:
                return SearchResponse(
                    results=[],
                    message="No relevant documents found",
                    total_results=0
                )
            
            # Format results
            search_items = []
            for result in results:
                search_items.append(SearchResultItem(
                    text=result['text'],
                    metadata=result['metadata'],
                    similarity_score=1 - result.get('score', 0)
                ))
            
            return SearchResponse(
                results=search_items,
                message=f"Found {len(results)} relevant chunks",
                total_results=len(results)
            )
            
        except Exception as e:
            raise ValueError(f"Error searching documents: {str(e)}")
    
    async def get_database_status(self) -> Dict[str, Any]:
        """Get database status information."""
        try:
            chunk_count = self.vector_store.count_chunks()
            return {
                "chunk_count": chunk_count,
                "status": "healthy"
            }
        except Exception as e:
            return {
                "chunk_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def clear_database(self) -> Dict[str, Any]:
        """Clear the vector database."""
        try:
            # Get count before clearing
            chunk_count = self.vector_store.count_chunks()
            
            # Clear database
            self.vector_store.clear_collection()
            
            return {
                "message": "Database cleared successfully",
                "chunks_cleared": chunk_count
            }
            
        except Exception as e:
            raise ValueError(f"Error clearing database: {str(e)}")
    
    async def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Get all document chunks from vector store for export."""
        try:
            return self.vector_store.get_all_chunks()
        except Exception as e:
            logger.error(f"Error getting all chunks: {str(e)}")
            return []
