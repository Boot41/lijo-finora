# Finora - AI-Powered Document Parser & Expense Categorizer

A comprehensive document processing and expense categorization system built with FastAPI, React, and AI integration. Finora intelligently parses financial documents, extracts transaction data, and categorizes expenses using advanced AI models.

## 🎥 Video Demonstration

Watch the complete system demonstration: [Finora Demo Video](https://www.loom.com/share/2a811de2e353407fa00d9e518bbdf98b?sid=9154dc0a-9ffd-4a28-aaa4-8f10adaebcf8)

## ✨ Features

### 📄 Document Processing
- **Multi-format Support**: PDF, DOCX, TXT, MD files
- **Advanced OCR**: Powered by Docling for accurate text extraction
- **Table Detection**: Intelligent parsing of financial tables and statements
- **Vector Storage**: ChromaDB for semantic search and retrieval

### 💰 Expense Categorization
- **AI-Powered Analysis**: Automatic transaction categorization using Groq LLM
- **Smart Categories**: Food & Dining, Transportation, Shopping, Bills & Utilities, Healthcare, Entertainment, Travel, Income, Transfers, Others
- **Manual Correction**: Edit and refine AI categorizations
- **Visual Analytics**: Interactive pie charts and spending summaries
- **Real-time Updates**: Live categorization as documents are uploaded

### 🤖 RAG Chat System
- **Document Q&A**: Ask questions about uploaded documents
- **Context-Aware**: Semantic search across document chunks
- **Fast Responses**: Groq integration for quick AI responses
- **Chat History**: Persistent conversation tracking

### 🔐 Security & Export
- **JWT Authentication**: Secure user sessions
- **Data Export**: Export categorized transactions to CSV/Excel
- **Error Handling**: Comprehensive error management and logging

## 🏗️ Architecture

### Backend (FastAPI)
```
server/
├── routes/           # API endpoints
├── usecases/         # Business logic
├── models/           # Data models
├── src/              # Core processing modules
├── middleware/       # Auth & error handling
└── utils/           # Configuration & utilities
```

### Frontend (React + TypeScript)
```
client/
├── src/
│   ├── components/   # Reusable UI components
│   ├── api/         # API service layer
│   └── assets/      # Static resources
└── public/          # Public assets
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/lijo41/lijo-finora.git
cd docparses/server
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
# or using poetry
poetry install
```

3. **Environment Configuration**
Create a `.env` file in the server directory:
```env
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key
CHROMADB_PATH=./chroma_db
COLLECTION_NAME=documents
MAX_SEARCH_RESULTS=10
```

4. **Start the server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to client directory**
```bash
cd ../client
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### API Keys
- **Groq API**: Get your free API key from [Groq Console](https://console.groq.com/)
- **JWT Secret**: Generate a secure random string for JWT token signing

### Database
- **ChromaDB**: Automatically initialized on first run
- **Persistence**: Data stored in `./chroma_db` directory

## 📊 API Endpoints

### Document Management
- `POST /documents/upload` - Upload and process documents
- `GET /documents/search` - Search document content
- `GET /documents/` - List all documents

### Expense Analysis
- `POST /expenses/analyze` - Analyze document for transactions
- `PUT /expenses/transactions/{id}/category` - Update transaction category
- `GET /expenses/summary` - Get expense summary

### Chat System
- `POST /chat/` - Send chat message
- `GET /chat/history` - Get chat history

### System
- `GET /` - Server status and health check
- `GET /health` - Simple health check

## 🧠 AI Integration

### Groq LLM
- **Model**: llama3-8b-8192
- **Features**: Fast inference, 14,400 requests/day free tier
- **Use Cases**: Transaction categorization, document Q&A

### Document Processing Pipeline
1. **Upload** → Document received via API
2. **Parse** → Docling extracts text and tables
3. **Chunk** → Content split into semantic chunks
4. **Embed** → Generate vector embeddings
5. **Store** → Save to ChromaDB vector database
6. **Analyze** → AI categorizes transactions
7. **Present** → Results displayed in UI

## 🎯 Use Cases

- **Personal Finance**: Track and categorize personal expenses
- **Business Accounting**: Process business receipts and statements
- **Document Analysis**: Extract insights from financial documents
- **Expense Reporting**: Generate categorized expense reports
- **Financial Planning**: Analyze spending patterns and trends

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Docling**: Advanced document processing
- **ChromaDB**: Vector database for embeddings
- **Groq**: Fast LLM inference
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Recharts**: Data visualization
- **Tailwind CSS**: Utility-first styling

## 📈 Performance

- **Document Processing**: ~2-5 seconds per PDF
- **Transaction Extraction**: 80%+ accuracy
- **AI Response Time**: <2 seconds with Groq
- **Concurrent Users**: Supports multiple simultaneous uploads

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Docling**: For excellent document processing capabilities
- **Groq**: For fast and reliable LLM inference
- **ChromaDB**: For efficient vector storage and search
- **FastAPI**: For the robust backend framework

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Watch the [demo video](https://www.loom.com/share/2a811de2e353407fa00d9e518bbdf98b?sid=9154dc0a-9ffd-4a28-aaa4-8f10adaebcf8) for usage examples

---

**Built with ❤️ for intelligent document processing and expense management**
