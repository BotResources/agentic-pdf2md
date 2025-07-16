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

class PDFProcessingError(AgenticPDF2MDError):
    """Raised when PDF processing fails."""
    pass


class ImageExtractionError(PDFProcessingError):
    """Raised when image extraction fails."""
    pass


class ScreenshotGenerationError(PDFProcessingError):
    """Raised when screenshot generation fails."""
    pass


class TextExtractionError(PDFProcessingError):
    """Raised when text extraction fails."""
    pass


class PageProcessingError(PDFProcessingError):
    """Raised when processing a specific page fails."""
    def __init__(self, page_number: int, message: str, original_error: Exception = None):
        self.page_number = page_number
        self.original_error = original_error
        super().__init__(f"Page {page_number}: {message}")


class ConfigurationError(AgenticPDF2MDError):
    """Raised when configuration is invalid."""
    pass

class OperationCancelledException(AgenticPDF2MDError):
    """Raised when an operation is cancelled."""
    def __init__(self, message: str = "Operation was cancelled."):
        super().__init__(message)