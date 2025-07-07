"""
Test ProcessedPDF edge cases and minimal PDFs.
"""
import pytest
import fitz
import tempfile
import os
from pathlib import Path
from agentic_pdf2md import RawPDF, ProcessedPDF


@pytest.fixture
def empty_pdf_path():
    """Create a PDF with an empty page."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    
    # Create PDF with empty page
    doc = fitz.open()
    doc.new_page()  # Empty page, no text or images
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


@pytest.fixture
def no_text_pdf_path():
    """Create a PDF with no text content (only images)."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    
    # Create PDF with only an image, no text
    doc = fitz.open()
    page = doc.new_page()
    
    # Add only an image
    img_pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 50, 50))
    img_pix.set_rect(img_pix.irect, (0, 255, 0))  # Green
    page.insert_image(fitz.Rect(100, 100, 150, 150), pixmap=img_pix)
    
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


class TestEmptyPDF:
    """Test processing of PDFs with no images."""
    
    def test_empty_pdf_processing(self, empty_pdf_path):
        """Test processing a PDF with an empty page."""
        raw_pdf = RawPDF(empty_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        # Should complete successfully
        assert processed_pdf._processed
        assert processed_pdf.page_count == 1
        assert processed_pdf.image_count == 0
        
        # Page should exist but be mostly empty
        page = processed_pdf.get_page(1)
        assert page is not None
        assert page.page_number == 1
        assert page.text_content.strip() == ""  # No text content
        assert len(page.screenshot) > 0  # Should still have screenshot
        assert len(page.image_refs) == 0  # No images
    
    def test_empty_pdf_llm_input(self, empty_pdf_path):
        """Test LLM input generation for empty PDF."""
        raw_pdf = RawPDF(empty_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        page = processed_pdf.get_page(1)
        llm_input = page.to_llm_input()
        
        # Should contain page marker but minimal content
        assert "[Page 1]" in llm_input
        assert "[Images on this page:]" not in llm_input
        assert "[IMAGE:" not in llm_input
        
        # Should be relatively short
        assert len(llm_input.strip()) < 20


class TestNoTextPDF:
    """Test processing of PDFs with no text content."""
    
    def test_no_text_pdf_processing(self, no_text_pdf_path):
        """Test processing a PDF with no text content."""
        raw_pdf = RawPDF(no_text_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        # Should complete successfully
        assert processed_pdf._processed
        assert processed_pdf.page_count == 1
        assert processed_pdf.image_count == 1
        
        # Page should have image but no text
        page = processed_pdf.get_page(1)
        assert page is not None
        assert page.page_number == 1
        assert page.text_content.strip() == ""  # No text content
        assert len(page.screenshot) > 0  # Should have screenshot
        assert len(page.image_refs) == 1  # Should have one image
    
    def test_no_text_pdf_llm_input(self, no_text_pdf_path):
        """Test LLM input generation for PDF with no text."""
        raw_pdf = RawPDF(no_text_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        page = processed_pdf.get_page(1)
        llm_input = page.to_llm_input()
        
        # Should contain page marker and image info
        assert "[Page 1]" in llm_input
        assert "[Images on this page:]" in llm_input
        assert "[IMAGE:" in llm_input
        
        # Should not have much text content between page marker and images
        lines = llm_input.split('\n')
        assert len([line for line in lines if line.strip() and not line.startswith('[')]) == 0