"""
Export routes for document content and parsed data
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
import tempfile
import os
import logging
from typing import Dict, Any

from usecases.document_usecase import DocumentUseCase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["export"])

@router.get("/parsed-content/")
async def export_parsed_content():
    """
    Export all parsed document content as markdown (chunked version)
    """
    try:
        document_usecase = DocumentUseCase()
        
        # Get all chunks from vector store
        chunks = await document_usecase.get_all_chunks()
        
        if not chunks:
            raise HTTPException(status_code=404, detail="No parsed documents found")
        
        # Generate markdown content
        markdown_content = _generate_markdown_from_chunks(chunks)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(markdown_content)
            temp_file_path = temp_file.name
        
        # Return file response
        return FileResponse(
            path=temp_file_path,
            filename="parsed_documents_chunked.md",
            media_type="text/markdown",
            background=lambda: os.unlink(temp_file_path)  # Clean up after sending
        )
        
    except Exception as e:
        logger.error(f"Error exporting parsed content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/raw-docling-content/")
async def export_raw_docling_content():
    """
    Export raw Docling extraction from md folder
    """
    try:
        from pathlib import Path
        
        # Check md folder for saved Docling extractions
        md_folder = Path(__file__).parent.parent / "md"
        logger.info(f"Looking for md folder at: {md_folder}")
        
        if not md_folder.exists():
            # Create md folder and return helpful message
            md_folder.mkdir(exist_ok=True)
            return {
                "message": "No Docling extractions found. Upload a PDF document first.",
                "md_folder_path": str(md_folder),
                "status": "md_folder_created"
            }
        
        # Find all Docling raw extraction files
        md_files = list(md_folder.glob("*_docling_raw.md"))
        logger.info(f"Found {len(md_files)} md files: {[f.name for f in md_files]}")
        
        if not md_files:
            return {
                "message": "No Docling extractions found in md folder. Upload a PDF document first.",
                "md_folder_path": str(md_folder),
                "files_in_folder": [f.name for f in md_folder.iterdir()]
            }
        
        # Get the most recent file
        latest_file = max(md_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Returning latest file: {latest_file}")
        
        # Return file response
        return FileResponse(
            path=str(latest_file),
            filename=latest_file.name,
            media_type="text/markdown"
        )
        
    except Exception as e:
        logger.error(f"Error exporting raw Docling content: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/parsed-content-preview")
async def preview_parsed_content():
    """
    Preview parsed document content as JSON for debugging
    """
    try:
        document_usecase = DocumentUseCase()
        
        # Get all chunks from vector store
        chunks = await document_usecase.get_all_chunks()
        
        if not chunks:
            return {"message": "No parsed documents found", "chunks": []}
        
        # Return first few chunks for preview
        preview_chunks = chunks[:10]  # Show first 10 chunks
        
        return {
            "total_chunks": len(chunks),
            "preview_chunks": len(preview_chunks),
            "chunks": [
                {
                    "text": chunk.get("text", "")[:500] + "..." if len(chunk.get("text", "")) > 500 else chunk.get("text", ""),
                    "metadata": chunk.get("metadata", {})
                }
                for chunk in preview_chunks
            ]
        }
        
    except Exception as e:
        logger.error(f"Error previewing parsed content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

def _generate_markdown_from_chunks(chunks):
    """
    Generate markdown content from document chunks
    """
    markdown_lines = [
        "# Parsed Document Content",
        "",
        f"*Generated from {len(chunks)} document chunks*",
        "",
        "---",
        ""
    ]
    
    # Group chunks by document if metadata available
    documents = {}
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        doc_name = metadata.get("filename", metadata.get("source", "Unknown Document"))
        
        if doc_name not in documents:
            documents[doc_name] = []
        documents[doc_name].append(chunk)
    
    # Generate markdown for each document
    for doc_name, doc_chunks in documents.items():
        markdown_lines.extend([
            f"## {doc_name}",
            "",
            f"*{len(doc_chunks)} chunks*",
            ""
        ])
        
        for i, chunk in enumerate(doc_chunks, 1):
            text = chunk.get("text", "").strip()
            if text:
                markdown_lines.extend([
                    f"### Chunk {i}",
                    "",
                    text,
                    "",
                    "---",
                    ""
                ])
    
    return "\n".join(markdown_lines)
