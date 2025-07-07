"""
Agentic PDF to Markdown Converter

An AI-powered PDF to Markdown converter optimized for LLM agents.
"""

__version__ = "0.1.0"

from .models.raw_pdf import RawPDF
from .exceptions import (
    AgenticPDF2MDError,
    PDFInitializationError,
    PDFLoadingError,
    PDFContentError,
    PDFNotLoadedError,
    Base64DecodingError,
)

__all__ = [
    "RawPDF",
    "AgenticPDF2MDError",
    "PDFInitializationError", 
    "PDFLoadingError",
    "PDFContentError",
    "PDFNotLoadedError",
    "Base64DecodingError",
]