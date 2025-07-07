"""
Test ProcessedPDF error handling and exception propagation.
"""
import pytest
from unittest.mock import Mock, patch
from agentic_pdf2md import RawPDF, ProcessedPDF
from agentic_pdf2md.exceptions import (
    PDFProcessingError,
    PageProcessingError,
    ImageExtractionError,
    ScreenshotGenerationError,
    TextExtractionError
)


class TestErrorHandling:
    """Test error handling in ProcessedPDF."""
    
    def test_processing_error_on_general_failure(self, simple_pdf_path):
        """Test that PDFProcessingError is raised on general processing failure."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        
        # Ensure RawPDF is loaded to avoid loading errors
        raw_pdf.load()
        
        with patch.object(processed_pdf, '_process_pages', side_effect=Exception("Test error")):
            with pytest.raises(PDFProcessingError) as exc_info:
                processed_pdf.process()
            
            assert "Failed to process PDF" in str(exc_info.value)
            assert "Test error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_processing_error_on_general_failure(self, simple_pdf_path):
        """Test that async PDFProcessingError is raised on general processing failure."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        
        # Ensure RawPDF is loaded to avoid loading errors
        await raw_pdf.load_async()
        
        with patch.object(processed_pdf, '_process_pages', side_effect=Exception("Test error")):
            with pytest.raises(PDFProcessingError) as exc_info:
                await processed_pdf.process_async()
            
            assert "Failed to process PDF" in str(exc_info.value)
            assert "Test error" in str(exc_info.value)
    
    def test_page_processing_error_includes_page_number(self, simple_pdf_path):
        """Test that PageProcessingError includes correct page number but gets wrapped in PDFProcessingError."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        
        # Ensure RawPDF is loaded
        raw_pdf.load()
        
        # Mock _process_single_page to fail on first page
        with patch.object(processed_pdf, '_process_single_page', side_effect=Exception("Page error")):
            with pytest.raises(PDFProcessingError) as exc_info:
                processed_pdf.process()
            
            # The outer exception should be PDFProcessingError
            assert "Failed to process PDF" in str(exc_info.value)
            
            # The cause should be PageProcessingError with correct page number
            cause = exc_info.value.__cause__
            assert isinstance(cause, PageProcessingError)
            assert cause.page_number == 1
            assert "Page 1:" in str(cause)
            assert "Page error" in str(cause)
    
    def test_image_extraction_error_propagation(self, simple_pdf_path):
        """Test that ImageExtractionError is properly propagated."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        
        # Ensure RawPDF is loaded
        raw_pdf.load()
        
        # Mock _extract_images to raise ImageExtractionError directly
        with patch.object(processed_pdf, '_extract_images') as mock_extract:
            mock_extract.side_effect = ImageExtractionError("Image error")
            
            with pytest.raises(PDFProcessingError) as exc_info:
                processed_pdf.process()
            
            # The ImageExtractionError should be wrapped in PDFProcessingError
            assert "Failed to process PDF" in str(exc_info.value)
            assert isinstance(exc_info.value.__cause__, ImageExtractionError)
    
    def test_processing_state_unchanged_on_error(self, simple_pdf_path):
        """Test that processing state remains unchanged when processing fails."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        
        # Ensure RawPDF is loaded
        raw_pdf.load()
        
        with patch.object(processed_pdf, '_process_pages', side_effect=Exception("Test error")):
            with pytest.raises(PDFProcessingError):
                processed_pdf.process()
            
            # State should remain unchanged
            assert not processed_pdf._processed
            assert processed_pdf.page_count == 0
            assert processed_pdf.image_count == 0