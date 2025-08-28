"""Main Streamlit application for the document parser and RAG pipeline."""

import streamlit as st
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from document_processor import DocumentProcessor
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from chat_gemini import GeminiChatInterface
from utils.config import GOOGLE_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Document Parser & RAG Chat",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.section-header {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2e8b57;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

.info-box {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
    margin: 1rem 0;
}

.success-box {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}

.error-box {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #dc3545;
    margin: 1rem 0;
}

.search-result {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border: 1px solid #dee2e6;
}

.metadata {
    font-size: 0.9em;
    color: #6c757d;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_components():
    """Initialize all components and cache them."""
    try:
        doc_processor = DocumentProcessor()
        embedding_generator = EmbeddingGenerator()
        vector_store = VectorStore()
        
        # Initialize chat interface if API key is available
        chat_interface = None
        if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here":
            try:
                # Get response length from session state or use default
                if 'response_length' not in st.session_state:
                    st.session_state.response_length = "balanced"
                
                chat_interface = GeminiChatInterface(response_length=st.session_state.response_length)
            except Exception as e:
                st.error(f"Failed to initialize chat interface: {str(e)}")
                logger.error(f"Chat interface initialization error: {str(e)}")
        
        return doc_processor, embedding_generator, vector_store, chat_interface
    except Exception as e:
        st.error(f"Failed to initialize components: {str(e)}")
        return None, None, None, None


def process_and_store_document(doc_processor, embedding_generator, vector_store, source):
    """Process a document and store it in the vector database."""
    try:
        with st.status("Processing document...", expanded=True) as status:
            # Process document
            st.write("📄 Converting document...")
            chunks = doc_processor.process_document(source)
            
            if not chunks:
                st.error("No chunks were generated from the document.")
                return False
            
            st.write(f"✅ Generated {len(chunks)} chunks")
            
            # Generate embeddings
            st.write("🔢 Generating embeddings...")
            chunks_with_embeddings = embedding_generator.embed_chunks(chunks)
            st.write("✅ Embeddings generated")
            
            # Store in vector database
            st.write("💾 Storing in vector database...")
            vector_store.add_chunks(chunks_with_embeddings)
            st.write("✅ Stored in database")
            
            status.update(label="✅ Document processed successfully!", state="complete")
            
        return True
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return False


def search_and_display_results(embedding_generator, vector_store, query, num_results=5):
    """Search the vector database and display results."""
    try:
        # Generate query embedding
        query_embedding = embedding_generator.embed_text(query)
        
        # Search vector database
        results = vector_store.search(query_embedding, limit=num_results)
        
        if not results:
            st.warning("No relevant documents found.")
            return []
        
        # Display results
        st.write(f"Found {len(results)} relevant chunks:")
        
        for i, result in enumerate(results, 1):
            with st.expander(f"Result {i} - {result['metadata'].get('filename', 'Unknown')}"):
                metadata = result['metadata']
                
                # Display metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    if metadata.get('filename'):
                        st.write(f"**File:** {metadata['filename']}")
                with col2:
                    if metadata.get('page_numbers'):
                        pages = ", ".join(str(p) for p in metadata['page_numbers'])
                        st.write(f"**Pages:** {pages}")
                with col3:
                    if metadata.get('title'):
                        st.write(f"**Section:** {metadata['title']}")
                
                # Display content
                st.write("**Content:**")
                st.write(result['text'])
                
                # Display similarity score
                st.write(f"**Similarity Score:** {1 - result.get('score', 0):.3f}")
        
        return results
        
    except Exception as e:
        st.error(f"Error searching documents: {str(e)}")
        return []


def main():
    """Main application function."""
    # Header
    st.markdown('<div class="main-header">📚 Document Parser & RAG Chat</div>', unsafe_allow_html=True)
    
    # Initialize components
    doc_processor, embedding_generator, vector_store, chat_interface = initialize_components()
    
    if not all([doc_processor, embedding_generator, vector_store]):
        st.error("Failed to initialize application components. Please check your configuration.")
        return
    
    # Sidebar for configuration and document management
    with st.sidebar:
        st.header("📋 Configuration")
        
        # API Key status
        if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here":
            st.success("✅ Google Gemini API Key configured")
        else:
            st.error("❌ Google Gemini API Key not found")
            st.info("Add your Google Gemini API key to the .env file to enable chat functionality.")
        
        # Database status
        try:
            chunk_count = vector_store.count_chunks()
            st.info(f"📊 Database contains {chunk_count} chunks")
        except:
            st.warning("⚠️ Database not accessible")
        
        # Chat settings
        st.header("💬 Chat Settings")
        
        # Response length control
        response_length = st.selectbox(
            "Response Length",
            options=["brief", "balanced", "detailed"],
            index=1,  # Default to "balanced"
            help="Control how detailed the responses should be:\n• Brief: 1-2 sentences\n• Balanced: Key details\n• Detailed: Thorough explanations"
        )
        
        # Update chat interface if response length changed
        if 'response_length' not in st.session_state:
            st.session_state.response_length = "balanced"
        
        if response_length != st.session_state.response_length:
            st.session_state.response_length = response_length
            if chat_interface:
                chat_interface.set_response_length(response_length)
                st.success(f"Response length updated to: {response_length}")
        
        st.header("📁 Document Management")
        
        # Document input options
        input_type = st.radio("Input Type:", ["URL", "File Upload"])
        
        if input_type == "URL":
            url_input = st.text_input("Enter document URL:", placeholder="https://example.com/document.pdf")
            if st.button("Process URL") and url_input:
                success = process_and_store_document(doc_processor, embedding_generator, vector_store, url_input)
                if success:
                    st.success("Document processed successfully!")
                    st.rerun()
        
        elif input_type == "File Upload":
            uploaded_file = st.file_uploader(
                "Upload document:",
                type=['pdf', 'docx', 'txt', 'md'],
                help="Supported formats: PDF, DOCX, TXT, MD"
            )
            
            if uploaded_file and st.button("Process File"):
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                success = process_and_store_document(doc_processor, embedding_generator, vector_store, temp_path)
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                if success:
                    st.success("Document processed successfully!")
                    st.rerun()
        
        # Database management
        st.header("🗄️ Database Management")
        if st.button("Clear Database", type="secondary"):
            try:
                vector_store.delete_table()
                st.success("Database cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing database: {str(e)}")
    
    # Main content area
    tab1, tab2 = st.tabs(["💬 Chat", "🔍 Search"])
    
    with tab1:
        st.markdown('<div class="section-header">Chat with Your Documents</div>', unsafe_allow_html=True)
        
        if not chat_interface:
            st.error("Chat functionality requires Google Gemini API key. Please add it to your .env file.")
        else:
            # Initialize chat history in session state
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask a question about your documents..."):
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Get relevant context
                with st.spinner("Searching for relevant information..."):
                    query_embedding = embedding_generator.embed_text(prompt)
                    context = vector_store.search(query_embedding, limit=5)
                
                # Generate and display assistant response
                with st.chat_message("assistant"):
                    try:
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        for chunk in chat_interface.get_streaming_response(prompt, context):
                            full_response += chunk
                            response_placeholder.markdown(full_response + "▌")
                        
                        response_placeholder.markdown(full_response)
                        
                    except Exception as e:
                        error_msg = f"Error generating response: {str(e)}"
                        st.error(error_msg)
                        full_response = error_msg
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Show sources used
                if context:
                    with st.expander("📚 Sources used in this response"):
                        for i, chunk in enumerate(context, 1):
                            metadata = chunk['metadata']
                            source_info = []
                            if metadata.get('filename'):
                                source_info.append(f"File: {metadata['filename']}")
                            if metadata.get('page_numbers'):
                                pages = ", ".join(str(p) for p in metadata['page_numbers'])
                                source_info.append(f"Pages: {pages}")
                            
                            st.write(f"**Source {i}:** {' | '.join(source_info)}")
                            st.write(f"_{chunk['text'][:200]}..._")
            
            # Clear chat button
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                if chat_interface:
                    chat_interface.clear_history()
                st.rerun()
    
    with tab2:
        st.markdown('<div class="section-header">Search Documents</div>', unsafe_allow_html=True)
        
        # Search interface
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Enter your search query:", placeholder="What are you looking for?")
        with col2:
            num_results = st.selectbox("Results:", [3, 5, 10], index=1)
        
        if st.button("🔍 Search") and search_query:
            results = search_and_display_results(embedding_generator, vector_store, search_query, num_results)
        
        # Quick search suggestions
        st.markdown("**Quick searches:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Summary"):
                if search_query != "summary overview main points":
                    search_query = "summary overview main points"
                    st.rerun()
        
        with col2:
            if st.button("🔑 Key concepts"):
                if search_query != "key concepts important terms":
                    search_query = "key concepts important terms"
                    st.rerun()
        
        with col3:
            if st.button("📈 Methodology"):
                if search_query != "methodology approach methods":
                    search_query = "methodology approach methods"
                    st.rerun()


if __name__ == "__main__":
    main()
