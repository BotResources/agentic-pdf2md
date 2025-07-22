"""
Agentic PDF to Markdown Converter

An AI-powered PDF to Markdown converter optimized for LLM agents.
"""

__version__ = "0.1.0"

from .models.raw_pdf import RawPDF
from .models.processed_pdf import ProcessedPDF, PDFProcessedPage, ImageReference
from .models.llm_runner import LLMRunner, LLMRunnerFactory, LLMRunnerOrFactory
from .models.llm_messages import BaseLLMMessage, SystemMessage, UserMessage, AIMessage, ToolCall, ToolResponseMessage
from .models.cancellation_token import CancellationToken
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
from .config import PreProcessingConfig, ParallelProcessingConfig, SerialProcessingConfig, ProcessingConfig

__all__ = [
    # Types
    "LLMRunnerFactory",
    "LLMRunnerOrFactory",
    # Models
    "LLMRunner",
    "RawPDF",
    "ProcessedPDF",
    "PDFProcessedPage", 
    "ImageReference",
    "CancellationToken",
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
    # Configurations
    "PreProcessingConfig",
    "ParallelProcessingConfig",
    "SerialProcessingConfig",
    "ProcessingConfig",
]