"""
Tests for RawPDF class.
"""
import pytest
from agentic_pdf2md import RawPDF
from agentic_pdf2md.exceptions import PDFInitializationError, PDFLoadingError

class TestRawPDF:
    def test_load_from_file(self, simple_pdf_path):
        """Test loading PDF from file."""
        pdf = RawPDF(file_path=simple_pdf_path)
        pdf.load()
        
        assert pdf.is_loaded
        assert pdf.content.page_count > 0
    
    def test_load_from_base64(self, pdf_base64):
        """Test loading PDF from base64."""
        pdf = RawPDF(base64_content=pdf_base64)
        pdf.load()
        
        assert pdf.is_loaded
        assert pdf.content.page_count > 0
    
    def test_invalid_base64(self, corrupted_base64):
        """Test error handling for invalid base64."""
        pdf = RawPDF(base64_content=corrupted_base64)
        
        with pytest.raises(Exception):  # Will be your custom exception
            pdf.load()