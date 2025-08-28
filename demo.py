"""Comprehensive demo of the document parser and RAG pipeline."""

import sys
from pathlib import Path
import time

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from document_processor import DocumentProcessor
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from chat import RAGChatInterface


def demo_pipeline():
    """Demonstrate the complete RAG pipeline functionality."""
    
    print("🚀 Document Parser & RAG Pipeline Demo")
    print("=" * 50)
    
    # Initialize components
    print("\n1. Initializing components...")
    doc_processor = DocumentProcessor()
    embedding_generator = EmbeddingGenerator()
    vector_store = VectorStore()
    
    print("✅ All components initialized")
    
    # Process the test document
    print("\n2. Processing test document...")
    chunks = doc_processor.process_document("test_document.txt")
    print(f"✅ Generated {len(chunks)} chunks")
    
    # Show chunk details
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i}:")
        print(f"  Text length: {len(chunk['text'])} characters")
        print(f"  Filename: {chunk['metadata']['filename']}")
        print(f"  Preview: {chunk['text'][:100]}...")
    
    # Generate embeddings
    print("\n3. Generating embeddings...")
    chunks_with_embeddings = embedding_generator.embed_chunks(chunks)
    print(f"✅ Generated embeddings with dimension: {len(chunks_with_embeddings[0]['vector'])}")
    
    # Store in vector database
    print("\n4. Storing in vector database...")
    vector_store.add_chunks(chunks_with_embeddings)
    chunk_count = vector_store.count_chunks()
    print(f"✅ Database now contains {chunk_count} chunks")
    
    # Demonstrate search functionality
    print("\n5. Testing search functionality...")
    test_queries = [
        "What are the key components?",
        "Tell me about the architecture",
        "What is LanceDB used for?",
        "How does the embedding work?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        query_embedding = embedding_generator.embed_text(query)
        results = vector_store.search(query_embedding, limit=1)
        
        if results:
            result = results[0]
            print(f"  Score: {1 - result['score']:.3f}")
            print(f"  Match: {result['text'][:150]}...")
        else:
            print("  No results found")
    
    # Demonstrate chat functionality (if OpenAI key available)
    print("\n6. Testing chat interface...")
    try:
        chat_interface = RAGChatInterface()
        
        # Test chat with context
        query = "What are the main components of this system?"
        query_embedding = embedding_generator.embed_text(query)
        context = vector_store.search(query_embedding, limit=3)
        
        print(f"Chat Query: '{query}'")
        response = chat_interface.get_response(query, context)
        print(f"Chat Response: {response}")
        
    except Exception as e:
        print(f"⚠️  Chat requires OpenAI API key: {e}")
    
    print("\n🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("- Add your OpenAI API key to .env for chat functionality")
    print("- Access the web interface at: http://localhost:8501")
    print("- Upload your own documents and start chatting!")


if __name__ == "__main__":
    demo_pipeline()
