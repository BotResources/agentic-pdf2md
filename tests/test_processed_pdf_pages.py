"""
Test ProcessedPDF page processing functionality.
"""
import pytest
import fitz
import tempfile
import os
from pathlib import Path
from agentic_pdf2md import RawPDF, ProcessedPDF
from agentic_pdf2md.config import ProcessingConfig


@pytest.fixture
def text_with_images_pdf_path():
    """Create a PDF with text and images for testing page structure."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    
    doc = fitz.open()
    
    # Page with text and image
    page = doc.new_page()
    page.insert_text((50, 50), "This is test content\nwith multiple lines\nof text.", fontsize=12)
    
    # Add an image
    img_pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 30, 30))
    img_pix.set_rect(img_pix.irect, (255, 0, 0))  # Red
    page.insert_image(fitz.Rect(100, 100, 130, 130), pixmap=img_pix)
    
    doc.save(tmp_path)
    doc.close()
    
    yield tmp_path
    
    # Cleanup - force close any handles and retry deletion
    try:
        os.remove(tmp_path)
    except PermissionError:
        import time
        time.sleep(0.1)
        try:
            os.remove(tmp_path)
        except:
            pass  # Best effort cleanup


class TestPageDataStructure:
    """Test PDFProcessedPage data structure and functionality."""
    
    def test_page_contains_expected_data(self, text_with_images_pdf_path):
        """Test that PDFProcessedPage contains expected data."""
        raw_pdf = RawPDF(text_with_images_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        page = processed_pdf.get_page(1)
        
        # Check basic structure
        assert page.page_number == 1
        assert isinstance(page.text_content, str)
        assert isinstance(page.screenshot, bytes)
        assert isinstance(page.image_refs, list)
        
        # Check content
        assert "This is test content" in page.text_content
        assert len(page.screenshot) > 0
        assert len(page.image_refs) == 1
    
    def test_page_numbering_is_one_indexed(self, simple_pdf_path):
        """Test that page numbering is 1-indexed."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        # Should have at least one page
        assert processed_pdf.page_count >= 1
        
        # First page should be numbered 1
        first_page = processed_pdf.pages[0]
        assert first_page.page_number == 1
        
        # get_page should work with 1-indexed numbers
        page = processed_pdf.get_page(1)
        assert page is not None
        assert page.page_number == 1
    
    def test_to_llm_input_without_layout_hints(self, text_with_images_pdf_path):
        """Test to_llm_input method without layout hints."""
        raw_pdf = RawPDF(text_with_images_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        page = processed_pdf.get_page(1)
        llm_input = page.to_llm_input(include_layout_hints=False)
        
        # Should contain page marker
        assert "[Page 1]" in llm_input
        
        # Should contain text content
        assert "This is test content" in llm_input
        
        # Should contain image reference
        assert "[Images on this page:]" in llm_input
        assert "[IMAGE:" in llm_input
        
        # Should NOT contain position information
        assert "Position:" not in llm_input
    
    def test_to_llm_input_with_layout_hints(self, text_with_images_pdf_path):
        """Test to_llm_input method with layout hints."""
        raw_pdf = RawPDF(text_with_images_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        page = processed_pdf.get_page(1)
        llm_input = page.to_llm_input(include_layout_hints=True)
        
        # Should contain page marker
        assert "[Page 1]" in llm_input
        
        # Should contain text content
        assert "This is test content" in llm_input
        
        # Should contain image reference with position
        assert "[Images on this page:]" in llm_input
        assert "[IMAGE:" in llm_input
        assert "Position:" in llm_input
    
    def test_to_llm_input_with_no_images(self, simple_pdf_path):
        """Test to_llm_input method with no images."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        page = processed_pdf.get_page(1)
        llm_input = page.to_llm_input()
        
        # Should contain page marker and text
        assert "[Page 1]" in llm_input
        assert "Test PDF Content" in llm_input
        
        # Should NOT contain image sections
        assert "[Images on this page:]" not in llm_input
        assert "[IMAGE:" not in llm_input
    
    def test_get_all_pages_llm_input(self, simple_pdf_path):
        """Test get_all_pages_llm_input method."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        all_pages_input = processed_pdf.get_all_pages_llm_input()
        
        # Should contain page marker
        assert "[Page 1]" in all_pages_input
        
        # Should contain text content
        assert "Test PDF Content" in all_pages_input
        
        # Should be a string
        assert isinstance(all_pages_input, str)