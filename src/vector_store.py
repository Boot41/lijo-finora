"""Vector storage and search using LanceDB."""

from typing import List, Dict, Any, Optional
import logging
import lancedb
import pandas as pd
from lancedb.pydantic import LanceModel, Vector
from pydantic import BaseModel
from utils.config import VECTOR_DB_URI, TABLE_NAME, MAX_SEARCH_RESULTS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunk(LanceModel):
    """Schema for document chunks in LanceDB."""
    text: str
    vector: Vector(384)  # all-MiniLM-L6-v2 dimension
    filename: Optional[str] = None
    page_numbers: Optional[str] = None  # Store as string instead of list
    title: Optional[str] = None
    source: Optional[str] = None


class VectorStore:
    """Handles vector storage and search operations using LanceDB."""
    
    def __init__(self, db_uri: str = VECTOR_DB_URI, table_name: str = TABLE_NAME):
        """
        Initialize the vector store.
        
        Args:
            db_uri: URI for the LanceDB database
            table_name: Name of the table to use
        """
        self.db_uri = db_uri
        self.table_name = table_name
        self.db = None
        self.table = None
        self._connect()
    
    def _connect(self):
        """Connect to the LanceDB database."""
        try:
            logger.info(f"Connecting to LanceDB at {self.db_uri}")
            self.db = lancedb.connect(self.db_uri)
            logger.info("Connected to LanceDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to LanceDB: {str(e)}")
            raise
    
    def create_table(self, overwrite: bool = False):
        """
        Create a new table in the database.
        
        Args:
            overwrite: Whether to overwrite existing table
        """
        try:
            mode = "overwrite" if overwrite else "create"
            logger.info(f"Creating table '{self.table_name}' with mode '{mode}'")
            
            self.table = self.db.create_table(
                self.table_name,
                schema=DocumentChunk,
                mode=mode
            )
            logger.info(f"Table '{self.table_name}' created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create table: {str(e)}")
            raise
    
    def open_table(self):
        """Open an existing table."""
        try:
            logger.info(f"Opening table '{self.table_name}'")
            self.table = self.db.open_table(self.table_name)
            logger.info(f"Table '{self.table_name}' opened successfully")
        except Exception as e:
            logger.error(f"Failed to open table: {str(e)}")
            # Try to create the table if it doesn't exist
            self.create_table()
    
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
            # Ensure table exists
            if self.table is None:
                self.open_table()
            
            # Prepare data for LanceDB
            prepared_chunks = []
            for chunk in chunks:
                if "vector" not in chunk:
                    logger.warning("Chunk missing vector, skipping")
                    continue
                
                metadata = chunk.get("metadata", {})
                page_numbers_str = ",".join(str(p) for p in metadata.get("page_numbers", [])) if metadata.get("page_numbers") else None
                
                prepared_chunk = {
                    "text": chunk["text"],
                    "vector": chunk["vector"],
                    "filename": metadata.get("filename"),
                    "page_numbers": page_numbers_str,
                    "title": metadata.get("title"),
                    "source": metadata.get("source")
                }
                prepared_chunks.append(prepared_chunk)
            
            if not prepared_chunks:
                logger.warning("No valid chunks to add after preparation")
                return
            
            logger.info(f"Adding {len(prepared_chunks)} chunks to vector store")
            self.table.add(prepared_chunks)
            logger.info("Chunks added successfully")
            
        except Exception as e:
            logger.error(f"Failed to add chunks: {str(e)}")
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
            if self.table is None:
                self.open_table()
            
            logger.info(f"Searching for {limit} similar chunks")
            
            # Perform vector search
            results = self.table.search(query_vector).limit(limit).to_pandas()
            
            # Convert results to list of dictionaries
            search_results = []
            for _, row in results.iterrows():
                # Parse page numbers back to list
                page_numbers = []
                if row.get("page_numbers"):
                    try:
                        page_numbers = [int(p.strip()) for p in row["page_numbers"].split(",") if p.strip()]
                    except:
                        page_numbers = []
                
                result = {
                    "text": row["text"],
                    "metadata": {
                        "filename": row.get("filename"),
                        "page_numbers": page_numbers,
                        "title": row.get("title"),
                        "source": row.get("source")
                    },
                    "score": row.get("_distance", 0.0)  # LanceDB returns distance
                }
                search_results.append(result)
            
            logger.info(f"Found {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    def get_all_chunks(self) -> pd.DataFrame:
        """
        Get all chunks from the vector store.
        
        Returns:
            DataFrame with all chunks
        """
        try:
            if self.table is None:
                self.open_table()
            
            return self.table.to_pandas()
            
        except Exception as e:
            logger.error(f"Failed to get all chunks: {str(e)}")
            raise
    
    def count_chunks(self) -> int:
        """
        Get the total number of chunks in the store.
        
        Returns:
            Number of chunks
        """
        try:
            if self.table is None:
                self.open_table()
            
            return self.table.count_rows()
            
        except Exception as e:
            logger.error(f"Failed to count chunks: {str(e)}")
            return 0
    
    def delete_table(self):
        """Delete the table from the database."""
        try:
            if self.table_name in self.db.table_names():
                self.db.drop_table(self.table_name)
                logger.info(f"Table '{self.table_name}' deleted")
                self.table = None
            else:
                logger.warning(f"Table '{self.table_name}' does not exist")
                
        except Exception as e:
            logger.error(f"Failed to delete table: {str(e)}")
            raise
    
    def table_exists(self) -> bool:
        """Check if the table exists in the database."""
        try:
            return self.table_name in self.db.table_names()
        except Exception:
            return False
