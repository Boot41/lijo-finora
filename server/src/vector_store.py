"""Vector storage and search using ChromaDB."""

from typing import List, Dict, Any, Optional
import logging
import chromadb
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Handles vector storage and search operations using ChromaDB."""
    
    def __init__(self, collection_name: str = "documents"):
        """
        Initialize the vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to ChromaDB."""
        try:
            logger.info("Connecting to ChromaDB")
            self.client = chromadb.PersistentClient(path="./chroma_db")
            logger.info("Connected to ChromaDB successfully")
            self._get_or_create_collection()
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {str(e)}")
            raise
    
    def _get_or_create_collection(self):
        """Get or create the collection."""
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks for RAG"}
            )
            logger.info(f"Collection '{self.collection_name}' ready")
        except Exception as e:
            logger.error(f"Failed to get/create collection: {str(e)}")
            raise
    
    def create_table(self, overwrite: bool = False):
        """Create collection (ChromaDB equivalent of table)."""
        try:
            if overwrite:
                try:
                    self.client.delete_collection(name=self.collection_name)
                    logger.info(f"Deleted existing collection '{self.collection_name}'")
                except:
                    pass
            self._get_or_create_collection()
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            raise
    
    def open_table(self):
        """Open collection (ChromaDB equivalent)."""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' opened")
        except Exception as e:
            logger.warning(f"Collection not found, creating: {str(e)}")
            self._get_or_create_collection()
    
    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Add document chunks to ChromaDB.
        
        Args:
            chunks: List of chunks with text, vector, and metadata
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        try:
            # Prepare data for ChromaDB
            ids = []
            documents = []
            embeddings = []
            metadatas = []
            
            for chunk in chunks:
                if "vector" not in chunk:
                    logger.warning("Chunk missing vector, skipping")
                    continue
                
                metadata = chunk.get("metadata", {})
                
                ids.append(str(uuid.uuid4()))
                documents.append(chunk["text"])
                embeddings.append(chunk["vector"])
                metadatas.append({
                    "filename": metadata.get("filename", ""),
                    "title": metadata.get("title", ""),
                    "source": metadata.get("source", ""),
                    "page_numbers": str(metadata.get("page_numbers", []))
                })
            
            if not ids:
                logger.warning("No valid chunks to add after preparation")
                return
            
            logger.info(f"Adding {len(ids)} chunks to ChromaDB")
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info("Chunks added successfully")
            
        except Exception as e:
            logger.error(f"Failed to add chunks: {str(e)}")
            raise
    
    def search(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            
        Returns:
            List of search results with metadata
        """
        try:
            logger.info(f"Searching for {limit} similar chunks")
            
            # Perform vector search with ChromaDB
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=limit
            )
            
            # Convert results to list of dictionaries
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0.0
                    
                    # Parse page numbers back to list
                    page_numbers = []
                    if metadata.get("page_numbers"):
                        try:
                            page_numbers = eval(metadata["page_numbers"])
                        except:
                            page_numbers = []
                    
                    result = {
                        "text": doc,
                        "metadata": {
                            "filename": metadata.get("filename", ""),
                            "page_numbers": page_numbers,
                            "title": metadata.get("title", ""),
                            "source": metadata.get("source", "")
                        },
                        "score": 1.0 - distance  # Convert distance to similarity
                    }
                    search_results.append(result)
            
            logger.info(f"Found {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """
        Get all chunks from ChromaDB.
        
        Returns:
            List of all chunks
        """
        try:
            results = self.collection.get()
            chunks = []
            
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    chunks.append({
                        "text": doc,
                        "metadata": metadata
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to get all chunks: {str(e)}")
            raise
    
    def count_chunks(self) -> int:
        """
        Get the total number of chunks in ChromaDB.
        
        Returns:
            Number of chunks
        """
        try:
            count = self.collection.count()
            logger.info(f"ChromaDB has {count} chunks")
            return count
        except Exception as e:
            logger.error(f"Failed to count chunks in ChromaDB: {str(e)}")
            return 0
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            # Delete and recreate the collection to clear all data
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' deleted")
            
            # Recreate the collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks for RAG"}
            )
            logger.info(f"Collection '{self.collection_name}' recreated")
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            raise
    
    def delete_table(self):
        """Delete the collection from ChromaDB."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' deleted")
            self.collection = None
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            raise
    
    def table_exists(self) -> bool:
        """Check if the collection exists in ChromaDB."""
        try:
            collections = self.client.list_collections()
            return any(c.name == self.collection_name for c in collections)
        except Exception:
            return False
