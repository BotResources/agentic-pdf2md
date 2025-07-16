import hashlib
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import asyncio
import fitz

from .raw_pdf import RawPDF
from ..config import PreProcessingConfig
from ..exceptions import (
    PDFProcessingError,
    ImageExtractionError,
    ScreenshotGenerationError,
    TextExtractionError,
    PageProcessingError,
)

# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class ImageReference:
    """Reference to an image with its position on the page."""
    image_id: str  # Unique identifier (hash of image content)
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    page_number: int


@dataclass
class PDFProcessedPage:
    """Represents a processed page from a PDF."""
    page_number: int
    text_content: str
    screenshot: bytes  # PNG bytes of the page screenshot
    image_refs: List[ImageReference] = field(default_factory=list)
    
    def to_llm_input(self, include_layout_hints: bool = False) -> str:
        """
        Generate a text representation of the page for LLM input.
        Minimizes tokens while preserving essential information.
        """
        lines = [f"[Page {self.page_number}]"]

        # Add text content
        if self.text_content.strip():
            lines.append(self.text_content.strip())

        # Add image placeholders
        if self.image_refs:
            lines.append("\n[Images on this page:]")
            for ref in self.image_refs:
                lines.append(f"[IMAGE: {ref.image_id}]")
                if include_layout_hints:
                    lines.append(f"  Position: {ref.bbox}")

        return "\n".join(lines)


class ProcessedPDF:
    def __init__(self, raw_pdf: RawPDF, config: Optional[PreProcessingConfig] = None):
        """
        Initialize ProcessedPDF with a RawPDF instance.
        
        :param raw_pdf: An instance of RawPDF containing the loaded PDF content.
        :param config: Processing configuration. If None, uses default config.
        """
        self.raw_pdf = raw_pdf
        self.config = config or PreProcessingConfig()
        self.pages: List[PDFProcessedPage] = []
        self.images: Dict[str, bytes] = {}  # image_id -> image bytes
        self._processed = False

        # Configure logging
        logging.basicConfig(level=getattr(logging, self.config.log_level))

    async def process_async(self):
        """
        Process the loaded PDF content asynchronously.
        Extracts text, images, and generates screenshots for each page.
        """
        if self._processed:
            return

        if not self.raw_pdf.is_loaded:
            await self.raw_pdf.load_async()

        # Process in executor to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self._process_pdf)
            self._processed = True
            logger.info("PDF processing completed successfully")
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise PDFProcessingError(f"Failed to process PDF: {str(e)}") from e

    def process(self):
        """
        Process the loaded PDF content synchronously.
        Extracts text, images, and generates screenshots for each page.
        """
        if self._processed:
            return

        if not self.raw_pdf.is_loaded:
            self.raw_pdf.load()

        try:
            self._process_pdf()
            self._processed = True
            logger.info("PDF processing completed successfully")
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise PDFProcessingError(f"Failed to process PDF: {str(e)}") from e

    def _process_pdf(self):
        """Internal method to process the PDF content."""
        doc = self.raw_pdf.content
        total_pages = len(doc)

        logger.info(f"Starting PDF processing: {total_pages} pages")

        try:
            # First pass: collect all unique images
            logger.info("Extracting images from PDF")
            image_cache = self._extract_images(doc)

            # Second pass: process pages
            logger.info("Processing pages")
            self._process_pages(doc, image_cache)

            logger.info(f"Processing complete: {len(self.pages)} pages, {len(self.images)} unique images")

        except Exception as e:
            logger.error(f"Error during PDF processing: {str(e)}")
            raise

    def _extract_images(self, doc: fitz.Document) -> Dict[int, str]:
        """Extract all unique images from the PDF."""
        image_cache = {}  # xref -> image_id mapping

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]

                try:
                    image_list = page.get_images(full=True)

                    for img in image_list:
                        xref = img[0]

                        if xref not in image_cache:
                            try:
                                image_id = self._extract_single_image(doc, xref)
                                image_cache[xref] = image_id
                            except Exception as e:
                                logger.warning(
                                    "Failed to extract image %s from page %d: %s",
                                    xref, page_num + 1, str(e)
                                )
                                continue

                except Exception as e:
                    logger.warning(
                        "Failed to get images from page %d: %s",
                        page_num + 1, str(e)
                    )
                    continue

        except Exception as e:
            raise ImageExtractionError(f"Failed to extract images: {str(e)}") from e

        return image_cache

    def _extract_single_image(self, doc: fitz.Document, xref: int) -> str:
        """Extract a single image and return its ID."""
        pix = None
        try:
            # Extract image
            pix = fitz.Pixmap(doc, xref)

            # Convert to bytes
            if pix.n - pix.alpha < 4:  # GRAY or RGB
                img_bytes = pix.tobytes(self.config.image_format)
            else:  # CMYK
                pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                img_bytes = pix_rgb.tobytes(self.config.image_format)
                pix_rgb = None  # Clean up converted pixmap

            # Check size limit
            if self.config.max_image_size and len(img_bytes) > self.config.max_image_size:
                logger.warning(f"Image {xref} exceeds size limit ({len(img_bytes)} bytes)")
                return None

            # Generate unique ID based on image content
            image_id = hashlib.sha256(img_bytes).hexdigest()[:16]

            # Store image
            self.images[image_id] = img_bytes

            return image_id

        except Exception as e:
            raise ImageExtractionError(f"Failed to extract image {xref}: {str(e)}") from e
        finally:
            if pix is not None:
                pix = None  # Free memory

    def _process_pages(self, doc: fitz.Document, image_cache: Dict[int, str]):
        """Process all pages in the PDF."""
        for page_num in range(len(doc)):
            try:
                if self.config.log_progress:
                    logger.info(f"Processing page {page_num + 1}/{len(doc)}")
                
                page = doc[page_num]
                processed_page = self._process_single_page(page, page_num, image_cache)
                self.pages.append(processed_page)
                
            except Exception as e:
                logger.error(f"Failed to process page {page_num + 1}: {str(e)}")
                raise PageProcessingError(
                    page_number=page_num + 1,
                    message=str(e),
                    original_error=e
                ) from e

    def _process_single_page(self, page: fitz.Page, page_num: int, image_cache: Dict[int, str]) -> PDFProcessedPage:
        """Process a single page."""
        # Extract text
        try:
            text_content = page.get_text()
        except Exception as e:
            raise TextExtractionError(f"Failed to extract text from page {page_num + 1}: {str(e)}") from e

        # Generate screenshot
        try:
            screenshot_bytes = self._generate_screenshot(page)
        except Exception as e:
            raise ScreenshotGenerationError(f"Failed to generate screenshot for page {page_num + 1}: {str(e)}") from e

        # Get image references for this page
        image_refs = self._get_page_image_refs(page, page_num, image_cache)

        return PDFProcessedPage(
            page_number=page_num + 1,
            text_content=text_content,
            screenshot=screenshot_bytes,
            image_refs=image_refs
        )

    def _generate_screenshot(self, page: fitz.Page) -> bytes:
        """Generate a screenshot of the page."""
        pix = None
        try:
            mat = fitz.Matrix(self.config.screenshot_dpi, self.config.screenshot_dpi)
            pix = page.get_pixmap(matrix=mat)
            screenshot_bytes = pix.tobytes(self.config.screenshot_format)
            return screenshot_bytes
        except Exception as e:
            raise ScreenshotGenerationError(f"Screenshot generation failed: {str(e)}") from e
        finally:
            if pix is not None:
                pix = None  # Free memory

    def _get_page_image_refs(self, page: fitz.Page, page_num: int, image_cache: Dict[int, str]) -> List[ImageReference]:
        """Get image references for a page."""
        image_refs = []

        try:
            image_list = page.get_images(full=True)

            for img in image_list:
                xref = img[0]

                if xref in image_cache and image_cache[xref]:
                    try:
                        bbox = page.get_image_bbox(img)
                        image_refs.append(ImageReference(
                            image_id=image_cache[xref],
                            bbox=(bbox.x0, bbox.y0, bbox.x1, bbox.y1),
                            page_number=page_num + 1
                        ))
                    except Exception as e:
                        logger.warning("Failed to get bbox for image %s on page %d: %s", xref, page_num + 1, str(e))
                        continue

        except Exception as e:
            logger.warning("Failed to get image references for page %d: %s", page_num + 1, str(e))

        return image_refs

    def get_image(self, image_id: str) -> Optional[bytes]:
        """
        Get image bytes by image ID.
        
        :param image_id: The unique identifier of the image
        :return: Image bytes or None if not found
        """
        return self.images.get(image_id)

    def get_page(self, page_number: int) -> Optional[PDFProcessedPage]:
        """
        Get a processed page by page number.
        
        :param page_number: The page number (1-indexed)
        :return: PDFProcessedPage or None if not found
        """
        if 1 <= page_number <= len(self.pages):
            return self.pages[page_number - 1]
        return None

    def get_all_pages_llm_input(self, include_layout_hints: bool = None) -> str:
        """
        Generate LLM input for all pages combined.
        
        :param include_layout_hints: Override config setting for layout hints
        """
        layout_hints = include_layout_hints if include_layout_hints is not None else self.config.include_layout_hints
        return "\n\n".join(
            page.to_llm_input(layout_hints) 
            for page in self.pages
        )

    @property
    def page_count(self) -> int:
        """Get the total number of pages."""
        return len(self.pages)

    @property
    def image_count(self) -> int:
        """Get the total number of unique images."""
        return len(self.images)

    def __repr__(self):
        """String representation of the ProcessedPDF object."""
        status = "processed" if self._processed else "not processed"
        if self._processed:
            return f"ProcessedPDF({status}, pages={self.page_count}, images={self.image_count})"
        return f"ProcessedPDF({status})"
