"""Chat interface using LangChain for RAG-based conversations."""

from typing import List, Dict, Any, Optional
import logging
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from utils.config import DEFAULT_MODEL, TEMPERATURE, OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGChatInterface:
    """LangChain-based chat interface for RAG conversations."""
    
    def __init__(self, model_name: str = DEFAULT_MODEL, temperature: float = TEMPERATURE):
        """
        Initialize the chat interface.
        
        Args:
            model_name: Name of the language model to use
            temperature: Temperature for response generation
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self.chat_history: List[BaseMessage] = []
        self._setup_llm()
        self._setup_prompt_template()
    
    def _setup_llm(self):
        """Set up the language model."""
        try:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            logger.info(f"Initializing {self.model_name} with temperature {self.temperature}")
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
                openai_api_key=OPENAI_API_KEY
            )
            logger.info("Language model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize language model: {str(e)}")
            raise
    
    def _setup_prompt_template(self):
        """Set up the prompt template for RAG conversations."""
        self.system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents.

Instructions:
1. Use ONLY the information from the provided context to answer questions
2. If the context doesn't contain relevant information, clearly state that you don't have enough information
3. Always cite the source when providing information (filename, page numbers if available)
4. Be concise but comprehensive in your responses
5. If asked about something not in the context, politely explain that you can only answer based on the provided documents

Context:
{context}

Previous conversation:
{chat_history}"""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{question}")
        ])
    
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
            
            # Create the chain
            chain = (
                RunnablePassthrough.assign(
                    context=lambda _: formatted_context,
                    chat_history=lambda _: formatted_history
                )
                | self.prompt_template
                | self.llm
                | StrOutputParser()
            )
            
            # Get response
            response = chain.invoke({"question": question})
            
            # Update chat history
            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=response))
            
            # Keep only last 10 messages to manage context length
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return response
            
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
            
            # Create the chain
            chain = (
                RunnablePassthrough.assign(
                    context=lambda _: formatted_context,
                    chat_history=lambda _: formatted_history
                )
                | self.prompt_template
                | self.llm
                | StrOutputParser()
            )
            
            # Get streaming response
            full_response = ""
            for chunk in chain.stream({"question": question}):
                full_response += chunk
                yield chunk
            
            # Update chat history after streaming is complete
            self.chat_history.append(HumanMessage(content=question))
            self.chat_history.append(AIMessage(content=full_response))
            
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
            if isinstance(message, HumanMessage):
                formatted_history.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_history.append(f"Assistant: {message.content}")
        
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
        history = []
        for message in self.chat_history:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": message.content})
        
        return history
