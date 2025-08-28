# Quick Start Guide

## 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_actual_key_here
```

## 2. Run the Application

```bash
# Start the Streamlit web interface
streamlit run app.py
```

## 3. Test Programmatically

```bash
# Run the example script
python example_usage.py
```

## 4. Using the Web Interface

1. **Upload Documents**: Use sidebar to upload files or enter URLs
2. **Chat**: Ask questions about your documents in the Chat tab
3. **Search**: Perform similarity search in the Search tab

## 5. Pipeline Components

- **Document Processing**: Docling converts and chunks documents
- **Embeddings**: all-MiniLM-L6-v2 generates vector embeddings
- **Vector Store**: LanceDB stores and searches embeddings
- **Chat**: LangChain provides conversational interface

## 6. Example Usage

```python
from src.document_processor import DocumentProcessor
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore

# Initialize components
doc_processor = DocumentProcessor()
embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()

# Process document
chunks = doc_processor.process_document("document.pdf")
chunks_with_embeddings = embedding_generator.embed_chunks(chunks)
vector_store.add_chunks(chunks_with_embeddings)

# Search
query_embedding = embedding_generator.embed_text("your question")
results = vector_store.search(query_embedding)
```
