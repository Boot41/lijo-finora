"""FastAPI server for the document parser and RAG pipeline."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import document, chat, auth, status
from middleware.error_handler import setup_error_handlers

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Parser & RAG API",
    description="API for document processing, embedding generation, and RAG-based chat",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_error_handlers(app)

# Include routers
app.include_router(status.router)
app.include_router(document.router)
app.include_router(chat.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    logger.info("Server starting up...")
    logger.info("All components initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Server shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
