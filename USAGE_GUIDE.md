# Document Parser & RAG Pipeline - Usage Guide

## 🚀 Quick Start

### 1. Setup OpenAI API Key
```bash
# Edit the .env file
nano .env

# Add your actual OpenAI API key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 2. Run the Application
```bash
# Start the web interface
streamlit run app.py

# Or run the demo
python3 demo.py
```

## 📋 Features Overview

### Document Processing
- **Supported Formats**: PDF, DOCX, TXT, MD
- **Chunking**: Intelligent sentence-based chunking with overlap
- **Metadata**: Preserves filename, page numbers, and source information

### Embedding & Search
- **Model**: all-MiniLM-L6-v2 (384-dimensional vectors)
- **Storage**: LanceDB vector database
- **Search**: Semantic similarity search with scoring

### Chat Interface
- **Framework**: LangChain with OpenAI GPT models
- **Context**: RAG-based responses with source citations
- **Streaming**: Real-time response generation

## 🖥️ Web Interface Usage

### Sidebar - Document Management
1. **Upload Documents**:
   - Choose "File Upload" or "URL" input
   - Supported: PDF, DOCX, TXT files
   - Click "Process" to add to database

2. **Database Status**:
   - View current chunk count
   - Clear database if needed

### Chat Tab
1. **Ask Questions**: Type natural language queries
2. **View Sources**: Expand "Sources used" to see citations
3. **Clear History**: Reset conversation anytime

### Search Tab
1. **Semantic Search**: Enter search queries
2. **Results**: View ranked results with similarity scores
3. **Quick Searches**: Use predefined search buttons

## 💻 Programmatic Usage

```python
from src.document_processor import DocumentProcessor
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.chat import RAGChatInterface

# Initialize components
doc_processor = DocumentProcessor()
embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()
chat_interface = RAGChatInterface()

# Process document
chunks = doc_processor.process_document("document.pdf")
chunks_with_embeddings = embedding_generator.embed_chunks(chunks)
vector_store.add_chunks(chunks_with_embeddings)

# Search
query_embedding = embedding_generator.embed_text("your question")
results = vector_store.search(query_embedding, limit=5)

# Chat
response = chat_interface.get_response("your question", results)
```

## 🔧 Configuration

Edit `utils/config.py` to customize:
- **MAX_TOKENS**: Chunk size (default: 512)
- **CHUNK_OVERLAP**: Overlap between chunks (default: 50)
- **MAX_SEARCH_RESULTS**: Search result limit (default: 5)
- **TEMPERATURE**: Chat response creativity (default: 0.7)

## 📊 Performance Tips

1. **Large Documents**: Process in batches for better memory usage
2. **Search Quality**: Use specific queries for better results
3. **Chunk Size**: Adjust MAX_TOKENS based on your content
4. **GPU Acceleration**: Install CUDA for faster embeddings

## 🛠️ Troubleshooting

### Common Issues
1. **OpenAI API Error**: Check your API key in `.env`
2. **Memory Issues**: Reduce batch size or chunk count
3. **Import Errors**: Ensure all dependencies are installed
4. **Database Issues**: Clear and recreate with `rm -rf data/lancedb`

### Performance Monitoring
- Check logs for processing times
- Monitor vector database size
- Track embedding generation speed

## 🎯 Use Cases

- **Research**: Analyze academic papers and documents
- **Documentation**: Search technical manuals and guides
- **Knowledge Base**: Build internal company knowledge systems
- **Education**: Create interactive learning materials
- **Legal**: Process and query legal documents
