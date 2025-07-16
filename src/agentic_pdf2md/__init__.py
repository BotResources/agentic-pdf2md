"""
Agentic PDF to Markdown Converter

An AI-powered PDF to Markdown converter optimized for LLM agents.
"""

__version__ = "0.1.0"

from .models.raw_pdf import RawPDF
from .models.processed_pdf import ProcessedPDF, PDFProcessedPage, ImageReference
from .models.llm_runner import LLMRunner
from .models.llm_messages import BaseLLMMessage, SystemMessage, UserMessage, AIMessage, ToolCall, ToolResponseMessage
from .exceptions import (
    AgenticPDF2MDError,
    PDFInitializationError,
    PDFLoadingError,
    PDFContentError,
    PDFNotLoadedError,
    Base64DecodingError,
    PDFProcessingError,
    ImageExtractionError,
    ScreenshotGenerationError,
    TextExtractionError,
    PageProcessingError,
    ConfigurationError,
)

__all__ = [
    # Models
    "LLMRunner",
    "RawPDF",
    "ProcessedPDF",
    "PDFProcessedPage", 
    "ImageReference",
    # Messages
    "BaseLLMMessage",
    "SystemMessage",
    "UserMessage",
    "AIMessage",
    "ToolCall",
    "ToolResponseMessage",
    # Exceptions
    "AgenticPDF2MDError",
    "PDFInitializationError", 
    "PDFLoadingError",
    "PDFContentError",
    "PDFNotLoadedError",
    "Base64DecodingError",
    "PDFProcessingError",
    "ImageExtractionError",
    "ScreenshotGenerationError",
    "TextExtractionError",
    "PageProcessingError",
    "ConfigurationError",
]