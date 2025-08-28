"""Example usage of the document parser and RAG pipeline."""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from document_processor import DocumentProcessor
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from chat import RAGChatInterface


def main():
    """Example of how to use the pipeline programmatically."""
    
    # Initialize components
    print("Initializing components...")
    doc_processor = DocumentProcessor()
    embedding_generator = EmbeddingGenerator()
    vector_store = VectorStore()
    
    # Example document URL (you can change this)
    document_url = "https://arxiv.org/pdf/2408.09869"  # Docling paper
    
    try:
        # Process document
        print(f"Processing document: {document_url}")
        chunks = doc_processor.process_document(document_url)
        print(f"Generated {len(chunks)} chunks")
        
        # Generate embeddings
        print("Generating embeddings...")
        chunks_with_embeddings = embedding_generator.embed_chunks(chunks)
        print("Embeddings generated")
        
        # Store in vector database
        print("Storing in vector database...")
        vector_store.add_chunks(chunks_with_embeddings)
        print("Stored successfully")
        
        # Example search
        print("\nTesting search...")
        query = "What is Docling?"
        query_embedding = embedding_generator.embed_text(query)
        results = vector_store.search(query_embedding, limit=3)
        
        print(f"Search results for '{query}':")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Source: {result['metadata'].get('filename', 'Unknown')}")
            print(f"Text: {result['text'][:200]}...")
        
        # Example chat (requires OpenAI API key)
        try:
            print("\nTesting chat interface...")
            chat_interface = RAGChatInterface()
            response = chat_interface.get_response(query, results)
            print(f"Chat response: {response}")
        except Exception as e:
            print(f"Chat interface requires OpenAI API key: {e}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
