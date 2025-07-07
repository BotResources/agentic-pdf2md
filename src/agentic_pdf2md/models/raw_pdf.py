import io
import base64
import fitz
import asyncio
from typing import Optional

from ..exceptions import (
    PDFInitializationError,
    PDFLoadingError,
    PDFContentError,
    PDFNotLoadedError,
    Base64DecodingError,
)


class RawPDF:
    """
    Represents a raw PDF document with its metadata and content.
    Supports both synchronous and asynchronous loading.
    Content is stored as an opened fitz document.
    """
    def __init__(self, file_path: Optional[str] = None, base64_content: Optional[str] = None):
        """
        Initialize the RawPDF with either a file path or a base64 encoded string.

        Args:
            file_path (Optional[str]): Path to the PDF file.
            base64_content (Optional[str]): Base64 encoded string of the PDF content.
            
        Raises:
            PDFInitializationError: If neither file_path nor base64_content is provided.
        """
        if not file_path and not base64_content:
            raise PDFInitializationError("Either file_path or base64_content must be provided.")
        
        self.file_path = file_path
        self.base64_content = base64_content
        self._content = None
        self._loaded = False

    @property
    def content(self):
        """
        Get the PDF content as an opened fitz document. Must be called after loading.
        
        Returns:
            fitz.Document: The opened PDF document.
        
        Raises:
            PDFNotLoadedError: If content hasn't been loaded yet.
        """
        if not self._loaded:
            raise PDFNotLoadedError(
                "PDF content not loaded. Call 'load()' for sync or 'await load_async()' for async loading first."
            )
        return self._content

    @property
    def is_loaded(self) -> bool:
        """Check if the PDF content has been loaded."""
        return self._loaded

    def load(self):
        """
        Synchronously load the PDF content from the file path or base64 string.
        
        Returns:
            RawPDF: Self for method chaining.
            
        Raises:
            PDFLoadingError: If PDF loading fails.
            Base64DecodingError: If base64 decoding fails.
            PDFContentError: If PDF content processing fails.
        """
        if self._loaded:
            return self
            
        try:
            if self.file_path:
                self._content = fitz.open(self.file_path)
            elif self.base64_content:
                # Remove data URL prefix if present
                pdf_base64 = self.base64_content
                if pdf_base64.startswith('data:'):
                    pdf_base64 = pdf_base64.split(',', 1)[1]
                
                try:
                    buffer = base64.b64decode(pdf_base64)
                except Exception as e:
                    raise Base64DecodingError(f"Failed to decode base64 content: {str(e)}") from e
                
                f = io.BytesIO(buffer)
                self._content = fitz.open("pdf", f)
            else:
                raise PDFInitializationError("Either file_path or base64_content must be provided.")
                
        except FileNotFoundError as e:
            raise PDFLoadingError(f"PDF file not found: {self.file_path}") from e
        except fitz.FileDataError as e:
            raise PDFContentError(f"Invalid PDF content: {str(e)}") from e
        except Base64DecodingError:
            raise  # Re-raise our custom exception
        except Exception as e:
            raise PDFLoadingError(f"Failed to load PDF: {str(e)}") from e
        
        self._loaded = True
        return self

    async def load_async(self):
        """
        Asynchronously load the PDF content from the file path or base64 string.
        
        Returns:
            RawPDF: Self for method chaining.
            
        Raises:
            PDFLoadingError: If PDF loading fails.
            Base64DecodingError: If base64 decoding fails.
            PDFContentError: If PDF content processing fails.
        """
        if self._loaded:
            return self
            
        try:
            if self.file_path:
                loop = asyncio.get_event_loop()
                
                def _open_pdf():
                    return fitz.open(self.file_path)
                
                self._content = await loop.run_in_executor(None, _open_pdf)
            elif self.base64_content:
                # Remove data URL prefix if present
                pdf_base64 = self.base64_content
                if pdf_base64.startswith('data:'):
                    pdf_base64 = pdf_base64.split(',', 1)[1]
                
                # Decode base64 and open PDF in executor to avoid blocking
                loop = asyncio.get_event_loop()
                
                def _decode_and_open():
                    try:
                        buffer = base64.b64decode(pdf_base64)
                    except Exception as e:
                        raise Base64DecodingError(f"Failed to decode base64 content: {str(e)}") from e
                    
                    f = io.BytesIO(buffer)
                    return fitz.open("pdf", f)
                
                self._content = await loop.run_in_executor(None, _decode_and_open)
            else:
                raise PDFInitializationError("Either file_path or base64_content must be provided.")
                
        except FileNotFoundError as e:
            raise PDFLoadingError(f"PDF file not found: {self.file_path}") from e
        except fitz.FileDataError as e:
            raise PDFContentError(f"Invalid PDF content: {str(e)}") from e
        except Base64DecodingError:
            raise  # Re-raise our custom exception
        except Exception as e:
            raise PDFLoadingError(f"Failed to load PDF: {str(e)}") from e
        
        self._loaded = True
        return self

    # Async context manager support
    async def __aenter__(self):
        """Async context manager entry - automatically loads content."""
        await self.load_async()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._content and not self._content.is_closed:
            self._content.close()

    # Sync context manager support
    def __enter__(self):
        """Sync context manager entry - automatically loads content."""
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        if self._content and not self._content.is_closed:
            self._content.close()

    def close(self):
        """Close the fitz document if it's open."""
        if self._content and not self._content.is_closed:
            self._content.close()
        self._loaded = False
        self._content = None

    def __del__(self):
        """Destructor to ensure document is closed."""
        self.close()

    def __repr__(self):
        """String representation of the RawPDF object."""
        source = f"file_path='{self.file_path}'" if self.file_path else "base64_content"
        status = "loaded" if self._loaded else "not loaded"
        return f"RawPDF({source}, {status})"