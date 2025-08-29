"""Vector storage and search using ChromaDB."""

from typing import List, Dict, Any, Optional
import logging
import chromadb
from chromadb.config import Settings
from pathlib import Path
from utils.config import MAX_SEARCH_RESULTS, CHROMADB_PATH, COLLECTION_NAME

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Handles vector storage and search operations using ChromaDB."""
    
    def __init__(self, persist_directory: str = None, collection_name: str = None):
        """
        Initialize the ChromaDB vector store.
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
        """
        if persist_directory is None:
            persist_directory = CHROMADB_PATH
        if collection_name is None:
            collection_name = COLLECTION_NAME
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to ChromaDB and initialize collection."""
        try:
            logger.info(f"Connecting to ChromaDB at {self.persist_directory}")
            
            # Create persist directory if it doesn't exist
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Connected to existing collection '{self.collection_name}'")
            except ValueError:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Document chunks for RAG system"}
                )
                logger.info(f"Created new collection '{self.collection_name}'")
            
            logger.info("ChromaDB connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {str(e)}")
            raise
    
    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Add document chunks to the vector store.
        
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
            
            for i, chunk in enumerate(chunks):
                if "vector" not in chunk or "text" not in chunk:
                    logger.warning(f"Chunk {i} missing vector or text, skipping")
                    continue
                
                # Generate unique ID
                chunk_id = f"chunk_{len(ids)}_{hash(chunk['text'][:100])}"
                ids.append(chunk_id)
                
                # Add document text
                documents.append(chunk["text"])
                
                # Add embedding vector
                embeddings.append(chunk["vector"])
                
                # Prepare metadata (ChromaDB handles complex metadata natively)
                metadata = chunk.get("metadata", {})
                # Convert page_numbers list to string for ChromaDB compatibility
                if "page_numbers" in metadata and isinstance(metadata["page_numbers"], list):
                    metadata["page_numbers"] = ",".join(str(p) for p in metadata["page_numbers"])
                
                metadatas.append(metadata)
            
            if not ids:
                logger.warning("No valid chunks to add after preparation")
                return
            
            logger.info(f"Adding {len(ids)} chunks to ChromaDB collection")
            
            # Add to ChromaDB collection
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info("Chunks added successfully to ChromaDB")
            
        except Exception as e:
            logger.error(f"Failed to add chunks to ChromaDB: {str(e)}")
            raise
    
    def search(self, query_vector: List[float], limit: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            
        Returns:
            List of search results with metadata
        """
        try:
            logger.info(f"Searching ChromaDB for {limit} similar chunks")
            
            # Perform vector search
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert results to list of dictionaries
            search_results = []
            
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    # Parse page numbers back to list
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    page_numbers = []
                    if metadata.get("page_numbers"):
                        try:
                            page_numbers = [int(p.strip()) for p in metadata["page_numbers"].split(",") if p.strip()]
                        except:
                            page_numbers = []
                    
                    # Update metadata with parsed page numbers
                    metadata["page_numbers"] = page_numbers
                    
                    result = {
                        "text": results["documents"][0][i],
                        "metadata": metadata,
                        "score": 1 - results["distances"][0][i]  # Convert distance to similarity score
                    }
                    search_results.append(result)
            
            logger.info(f"Found {len(search_results)} results in ChromaDB")
            return search_results
            
        except Exception as e:
            logger.error(f"ChromaDB search failed: {str(e)}")
            raise
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """
        Get all chunks from the vector store.
        
        Returns:
            List of all chunks with metadata
        """
        try:
            logger.info("Retrieving all chunks from ChromaDB")
            
            # Get all documents from collection
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            all_chunks = []
            if results["documents"]:
                for i, document in enumerate(results["documents"]):
                    metadata = results["metadatas"][i] if results["metadatas"] else {}
                    
                    # Parse page numbers back to list
                    page_numbers = []
                    if metadata.get("page_numbers"):
                        try:
                            page_numbers = [int(p.strip()) for p in metadata["page_numbers"].split(",") if p.strip()]
                        except:
                            page_numbers = []
                    
                    metadata["page_numbers"] = page_numbers
                    
                    chunk = {
                        "text": document,
                        "metadata": metadata
                    }
                    all_chunks.append(chunk)
            
            logger.info(f"Retrieved {len(all_chunks)} chunks from ChromaDB")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Failed to get all chunks from ChromaDB: {str(e)}")
            raise
    
    def count_chunks(self) -> int:
        """
        Get the total number of chunks in the store.
        
        Returns:
            Number of chunks
        """
        try:
            count = self.collection.count()
            logger.info(f"ChromaDB collection has {count} chunks")
            return count
            
        except Exception as e:
            logger.error(f"Failed to count chunks in ChromaDB: {str(e)}")
            return 0
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks for RAG system"}
            )
            logger.info(f"ChromaDB collection '{self.collection_name}' cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear ChromaDB collection: {str(e)}")
            raise
    
    def delete_table(self):
        """Delete the collection (for compatibility with existing interface)."""
        self.clear_collection()
    
    def table_exists(self) -> bool:
        """Check if the collection exists."""
        try:
            collections = self.client.list_collections()
            return any(col.name == self.collection_name for col in collections)
        except Exception:
            return False
