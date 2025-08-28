"""Embedding generation using sentence-transformers."""

from typing import List, Dict, Any
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.config import EMBEDDING_MODEL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Handles text embedding generation using sentence-transformers."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add embeddings to processed chunks.
        
        Args:
            chunks: List of processed chunks from document processor
            
        Returns:
            Chunks with added embedding vectors
        """
        if not chunks:
            return chunks
        
        try:
            # Extract texts for batch embedding
            texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embed_batch(texts)
            
            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk["vector"] = embedding
            
            logger.info(f"Added embeddings to {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error embedding chunks: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        return self.model.get_sentence_embedding_dimension()
    
    def similarity_search(self, query: str, embeddings: List[List[float]], top_k: int = 5) -> List[int]:
        """
        Perform similarity search using cosine similarity.
        
        Args:
            query: Query text
            embeddings: List of embedding vectors to search against
            top_k: Number of top results to return
            
        Returns:
            List of indices of most similar embeddings
        """
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Calculate cosine similarities
            similarities = []
            for i, embedding in enumerate(embeddings):
                similarity = self._cosine_similarity(query_embedding, embedding)
                similarities.append((i, similarity))
            
            # Sort by similarity and return top_k indices
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [idx for idx, _ in similarities[:top_k]]
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
