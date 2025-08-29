"""Groq Chat Interface for document Q&A."""

import os
import logging
from typing import List, Dict, Any, Generator
from groq import Groq
from utils.config import TEMPERATURE

logger = logging.getLogger(__name__)

class GroqChatInterface:
    """Chat interface using Groq API."""
    
    def __init__(self, response_length: str = "balanced"):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("Groq API key not found in environment variables")
        
        try:
            self.client = Groq(api_key=groq_api_key)
        except Exception as e:
            # Fallback initialization without extra parameters
            self.client = Groq()
            self.client.api_key = groq_api_key
        self.model = "llama3-8b-8192"  # Fast and reliable Groq model
        self.temperature = TEMPERATURE
        self.response_length = response_length
        
        # Response length configurations
        self.length_configs = {
            "concise": {"max_tokens": 150, "instruction": "Be concise and direct."},
            "balanced": {"max_tokens": 500, "instruction": "Provide a balanced, informative response."},
            "detailed": {"max_tokens": 1000, "instruction": "Provide a detailed, comprehensive response."}
        }
    
    def set_response_length(self, length: str):
        """Set the response length preference."""
        if length in self.length_configs:
            self.response_length = length
    
    def get_streaming_response(self, query: str, context: List[Dict[str, Any]]) -> Generator[str, None, None]:
        """Generate streaming response using Groq."""
        try:
            # Prepare context from document chunks
            context_text = "\n\n".join([
                f"Document: {chunk['metadata'].get('filename', 'Unknown')}\n{chunk['text']}"
                for chunk in context[:3]  # Limit context to avoid token limits
            ])
            
            config = self.length_configs.get(self.response_length, self.length_configs["balanced"])
            
            # Create system prompt
            system_prompt = f"""You are a helpful AI assistant that answers questions based on provided documents. 
            {config['instruction']}
            
            Use the following document context to answer the user's question. If the answer is not in the documents, say so clearly.
            Always cite which document you're referencing when possible.
            
            Context:
            {context_text}
            """
            
            # Create chat completion with streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=self.temperature,
                max_tokens=config["max_tokens"],
                stream=True
            )
            
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error generating streaming response: {e}")
            yield f"Error: {str(e)}"
    
    def get_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate non-streaming response using Groq."""
        try:
            # Prepare context from document chunks
            context_text = "\n\n".join([
                f"Document: {chunk['metadata'].get('filename', 'Unknown')}\n{chunk['text']}"
                for chunk in context[:3]  # Limit context to avoid token limits
            ])
            
            config = self.length_configs.get(self.response_length, self.length_configs["balanced"])
            
            # Create system prompt
            system_prompt = f"""You are a helpful AI assistant that answers questions based on provided documents. 
            {config['instruction']}
            
            Use the following document context to answer the user's question. If the answer is not in the documents, say so clearly.
            Always cite which document you're referencing when possible.
            
            Context:
            {context_text}
            """
            
            # Create chat completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=self.temperature,
                max_tokens=config["max_tokens"]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
