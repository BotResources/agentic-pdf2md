"""
Agentic PDF to Markdown Converter

An AI-powered PDF to Markdown converter optimized for LLM agents.
"""

__version__ = "0.1.0"

from .models.raw_pdf import RawPDF
from .models.processed_pdf import ProcessedPDF, PDFProcessedPage, ImageReference
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
    "RawPDF",
    "ProcessedPDF",
    "PDFProcessedPage", 
    "ImageReference",
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