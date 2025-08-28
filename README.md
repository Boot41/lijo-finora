# Document Parser and RAG Pipeline

A comprehensive document parsing and Retrieval-Augmented Generation (RAG) pipeline using modern AI tools.

## Features

- **Document Processing**: Uses Docling for robust document conversion
- **Embeddings**: Sentence Transformers with all-MiniLM-L6-v2 model
- **Vector Database**: LanceDB for efficient similarity search
- **Chat Interface**: LangChain-powered conversational AI
- **Web UI**: Streamlit-based user interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
docparses/
├── app.py                 # Main Streamlit application
├── src/
│   ├── document_processor.py  # Document parsing and chunking
│   ├── embeddings.py          # Embedding generation
│   ├── vector_store.py        # LanceDB operations
│   └── chat.py               # LangChain chat interface
├── utils/
│   └── config.py             # Configuration settings
├── data/                     # Data storage directory
└── requirements.txt
```

## Usage

1. Upload documents through the web interface
2. Documents are automatically processed, chunked, and embedded
3. Ask questions about your documents using natural language
4. Get contextual answers with source citations
