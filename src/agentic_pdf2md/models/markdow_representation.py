"""
Object used to store the result of the pdf procressing.
"""
from typing import Optional, List
from .raw_pdf import RawPDF
from .processed_pdf import ProcessedPDF


class MarkdownRepresentation:
    """
    """

    def __init__(self, content: Optional[str], pages: List[str]):
        """
        Initialize the MarkdownRepresentation with content and pages.

        Args:
            md_content (Optional[str]): The main markdown content.
            md_pages (List[str]): List of markdown pages.
        """
        self._content = None
        if content is not None:
            if not isinstance(content, str):
                raise ValueError("Content must be a string.")
            self._content = content.strip()
            self._content = content
        self._pages = None
        if pages is not None:
            if not isinstance(pages, list) and not all(isinstance(page, str) for page in pages):
                raise ValueError("Pages must be a list of strings.")
            self._pages = [page.strip() for page in pages if isinstance(page, str)]
            self._pages = pages
        if not self._pages and not self._content:
            self.loaded = False
        else:
            if self._pages:
                self.paginated = True
            else:
                self.paginated = False
        
        
    async def from_raw_pdf(self, file_path: Optional[str] = None, base64_content: Optional[str] = None):
        """
        Load the MarkdownRepresentation from a RawPDF object.

        Args:
            raw_pdf (RawPDF): The RawPDF object to load from.
        """
        # Load the raw PDF and pre process it
        raw_pdf = RawPDF(file_path=file_path, base64_content=base64_content)
        await raw_pdf.load_async()
        preprocessed_pdf = ProcessedPDF(raw_pdf=raw_pdf)
        await preprocessed_pdf.process_async()


        