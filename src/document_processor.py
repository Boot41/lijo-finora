"""Document processing module for parsing and chunking documents."""

from typing import List, Dict, Any, Union
from pathlib import Path
import logging
import pypdf
import docx
from utils.config import MAX_TOKENS, MERGE_PEERS, MIN_CHUNK_SIZE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document conversion and chunking."""
    
    def __init__(self):
        """Initialize the document processor."""
        pass
        
    def _chunk_text(self, text: str, max_tokens: int = MAX_TOKENS, overlap: int = 50) -> List[str]:
        """Simple text chunking by sentences and token count."""
        import re
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(sentence.split())
            
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                overlap_text = " ".join(current_chunk.split()[-overlap:]) if overlap > 0 else ""
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
                current_tokens = len(current_chunk.split())
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n[Page {page_num + 1}]\n{page_text}"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise
    
    def process_document(self, source: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Process a document from file path.
        
        Args:
            source: File path to the document
            
        Returns:
            List of processed chunks with metadata
        """
        try:
            logger.info(f"Processing document: {source}")
            source_path = Path(source)
            
            if not source_path.exists():
                raise FileNotFoundError(f"Document not found: {source}")
            
            # Extract text based on file extension
            file_ext = source_path.suffix.lower()
            
            if file_ext == '.pdf':
                text = self._extract_text_from_pdf(str(source_path))
            elif file_ext == '.docx':
                text = self._extract_text_from_docx(str(source_path))
            elif file_ext in ['.txt', '.md']:
                text = self._extract_text_from_txt(str(source_path))
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            if not text.strip():
                raise ValueError("No text extracted from document")
            
            # Chunk the text
            text_chunks = self._chunk_text(text)
            logger.info(f"Generated {len(text_chunks)} chunks")
            
            # Process chunks into the format we need
            processed_chunks = []
            for i, chunk_text in enumerate(text_chunks):
                # Filter out very small chunks
                if len(chunk_text.strip()) < MIN_CHUNK_SIZE:
                    continue
                    
                chunk_data = {
                    "text": chunk_text.strip(),
                    "metadata": {
                        "filename": source_path.name,
                        "page_numbers": self._extract_page_numbers_from_text(chunk_text),
                        "title": f"Chunk {i+1}",
                        "source": str(source_path)
                    }
                }
                processed_chunks.append(chunk_data)
            
            logger.info(f"Processed {len(processed_chunks)} valid chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing document {source}: {str(e)}")
            raise
    
    def _extract_page_numbers_from_text(self, text: str) -> List[int]:
        """Extract page numbers from text markers."""
        import re
        page_numbers = []
        # Look for [Page X] markers
        page_matches = re.findall(r'\[Page (\d+)\]', text)
        for match in page_matches:
            page_numbers.append(int(match))
        return sorted(list(set(page_numbers))) if page_numbers else []
    
    def process_multiple_documents(self, sources: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        """
        Process multiple documents.
        
        Args:
            sources: List of file paths or URLs
            
        Returns:
            Combined list of processed chunks from all documents
        """
        all_chunks = []
        
        for source in sources:
            try:
                chunks = self.process_document(source)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Failed to process {source}: {str(e)}")
                continue
        
        return all_chunks
