"""
Custom exceptions for the agentic-pdf2md library.
"""


class AgenticPDF2MDError(Exception):
    """Base exception for all agentic-pdf2md errors."""
    pass


class PDFInitializationError(AgenticPDF2MDError):
    """Raised when PDF initialization fails due to invalid parameters."""
    pass


class PDFLoadingError(AgenticPDF2MDError):
    """Raised when PDF loading fails."""
    pass


class PDFContentError(AgenticPDF2MDError):
    """Raised when there are issues with PDF content processing."""
    pass


class PDFNotLoadedError(AgenticPDF2MDError):
    """Raised when trying to access content before loading the PDF."""
    pass


class Base64DecodingError(PDFContentError):
    """Raised when base64 decoding fails."""
    pass


class FileNotFoundError(PDFLoadingError):
    """Raised when PDF file is not found."""
    pass