"""Chat interface using Google Gemini for RAG-based conversations."""

from typing import List, Dict, Any, Optional
import os
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from utils.config import DEFAULT_MODEL, TEMPERATURE, GOOGLE_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiChatInterface:
    """Google Gemini-based chat interface for RAG conversations."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.7, response_length: str = "balanced"):
        """
        Initialize the Gemini chat interface.
        
        Args:
            model_name: Name of the Gemini model to use
            temperature: Temperature for response generation (0.0 to 1.0)
            response_length: Length preference for responses ("brief", "balanced", "detailed")
        """
        self.model_name = model_name
        self.temperature = temperature
        self.response_length = response_length
        self.chat_history = []
        
        # Configure Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        
        # Set max tokens based on response length preference
        max_tokens = {
            "brief": 512,
            "balanced": 1024,
            "detailed": 2048
        }.get(response_length, 1024)
        
        # Initialize the model
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=0.8,
            top_k=40
        )
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        logger.info(f"Initializing {model_name} with temperature {temperature} and {response_length} responses")
        logger.info("Gemini model initialized successfully")
    
    def get_response(self, question: str, context: List[Dict[str, Any]]) -> str:
        """
        Get a response to a question using the provided context.
        
        Args:
            question: User's question
            context: List of relevant document chunks
            
        Returns:
            AI assistant's response
        """
        try:
            # Format context for the prompt
            formatted_context = self._format_context(context)
            
            # Format chat history
            formatted_history = self._format_chat_history()
            
            # Get response length instruction
            length_instruction = self._get_length_instruction()
            
            # Create the prompt
            prompt = f"""You are a helpful AI assistant that answers questions based on the provided context from documents.

Instructions:
1. Use ONLY the information from the provided context to answer questions
2. If the context doesn't contain relevant information, clearly state that you don't have enough information
3. Provide clear, direct answers without mentioning source files or citations
4. Write in complete sentences with proper punctuation (periods, commas, etc.)
5. {length_instruction}
6. If asked about something not in the context, politely explain that you can only answer based on the provided documents

Context:
{formatted_context}

Previous conversation:
{formatted_history}

Question: {question}

Answer (provide a well-formatted answer with proper punctuation and complete sentences):"""
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            if response.text:
                # Clean up the response text
                cleaned_response = self._clean_response(response.text)
                
                # Update chat history
                self.chat_history.append({"role": "user", "content": question})
                self.chat_history.append({"role": "assistant", "content": cleaned_response})
                
                # Keep only last 10 messages to manage context length
                if len(self.chat_history) > 10:
                    self.chat_history = self.chat_history[-10:]
                
                return cleaned_response
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your question. Please try again."
    
    def get_streaming_response(self, question: str, context: List[Dict[str, Any]]):
        """
        Get a streaming response to a question using the provided context.
        
        Args:
            question: User's question
            context: List of relevant document chunks
            
        Yields:
            Chunks of the AI assistant's response
        """
        try:
            # Format context for the prompt
            formatted_context = self._format_context(context)
            
            # Format chat history
            formatted_history = self._format_chat_history()
            
            # Get response length instruction
            length_instruction = self._get_length_instruction()
            
            # Create the prompt
            prompt = f"""You are a helpful AI assistant that answers questions based on the provided context from documents.

Instructions:
1. Use ONLY the information from the provided context to answer questions
2. If the context doesn't contain relevant information, clearly state that you don't have enough information
3. Provide clear, direct answers without mentioning source files or citations
4. Write in complete sentences with proper punctuation (periods, commas, etc.)
5. {length_instruction}
6. If asked about something not in the context, politely explain that you can only answer based on the provided documents

Context:
{formatted_context}

Previous conversation:
{formatted_history}

Question: {question}

Answer (provide a well-formatted answer with proper punctuation and complete sentences):"""
            
            # Get streaming response from Gemini
            full_response = ""
            response = self.model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            # Clean up the response text
            cleaned_response = self._clean_response(full_response)
            
            # Update chat history after streaming is complete
            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "assistant", "content": cleaned_response})
            
            # Keep only last 10 messages to manage context length
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
                
        except Exception as e:
            logger.error(f"Error generating streaming response: {str(e)}")
            yield "I apologize, but I encountered an error while processing your question. Please try again."
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format context chunks for the prompt."""
        if not context:
            return "No relevant context found."
        
        formatted_chunks = []
        for i, chunk in enumerate(context, 1):
            metadata = chunk.get("metadata", {})
            
            # Build source information
            source_info = []
            if metadata.get("filename"):
                source_info.append(f"File: {metadata['filename']}")
            if metadata.get("page_numbers"):
                pages = ", ".join(str(p) for p in metadata["page_numbers"])
                source_info.append(f"Pages: {pages}")
            if metadata.get("title"):
                source_info.append(f"Section: {metadata['title']}")
            
            source_text = " | ".join(source_info) if source_info else "Unknown source"
            
            formatted_chunk = f"[Context {i}]\nSource: {source_text}\nContent: {chunk['text']}\n"
            formatted_chunks.append(formatted_chunk)
        
        return "\n".join(formatted_chunks)
    
    def _format_chat_history(self) -> str:
        """Format chat history for the prompt."""
        if not self.chat_history:
            return "No previous conversation."
        
        formatted_history = []
        for message in self.chat_history[-6:]:  # Only include last 6 messages
            role = message["role"]
            content = message["content"]
            if role == "user":
                formatted_history.append(f"Human: {content}")
            elif role == "assistant":
                formatted_history.append(f"Assistant: {content}")
        
        return "\n".join(formatted_history)
    
    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []
        logger.info("Chat history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the chat history in a formatted way.
        
        Returns:
            List of message dictionaries with role and content
        """
        return self.chat_history.copy()
    
    def _clean_response(self, text: str) -> str:
        """Clean up response text to ensure proper punctuation and formatting."""
        import re
        
        # Remove any remaining source citations in parentheses
        text = re.sub(r'\([^)]*(?:File|Page|Section)[^)]*\)', '', text)
        
        # Ensure sentences end with proper punctuation
        text = text.strip()
        
        # Add period if the text doesn't end with punctuation
        if text and not text.endswith(('.', '!', '?', ':')):
            text += '.'
        
        # Fix spacing issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\s+([.!?])', r'\1', text)  # Remove space before punctuation
        
        # Capitalize first letter of sentences
        sentences = text.split('. ')
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                cleaned_sentences.append(sentence)
        
        return '. '.join(cleaned_sentences)
    
    def _get_length_instruction(self) -> str:
        """Get the appropriate length instruction based on response_length setting."""
        instructions = {
            "brief": "Provide concise, to-the-point answers (1-2 sentences when possible)",
            "balanced": "Provide comprehensive but concise responses with key details",
            "detailed": "Provide thorough, detailed explanations with examples and context when available"
        }
        return instructions.get(self.response_length, instructions["balanced"])
    
    def set_response_length(self, length: str):
        """Update the response length preference."""
        if length in ["brief", "balanced", "detailed"]:
            self.response_length = length
            # Update model configuration
            max_tokens = {
                "brief": 512,
                "balanced": 1024,
                "detailed": 2048
            }.get(length, 1024)
            
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=max_tokens,
                top_p=0.8,
                top_k=40
            )
            
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config
            )
            logger.info(f"Updated response length to: {length}")
