"""
Test ProcessedPDF image processing functionality.
"""
import pytest
import fitz
import tempfile
import os
from pathlib import Path
from agentic_pdf2md import RawPDF, ProcessedPDF


@pytest.fixture
def multi_image_pdf_path():
    """Create a PDF with multiple images, including duplicates."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    
    # Create PDF with images
    doc = fitz.open()
    
    # Page 1: Insert same image twice
    page1 = doc.new_page()
    page1.insert_text((50, 50), "Page 1 with duplicate images", fontsize=12)
    
    # Create a simple image (red rectangle)
    img_pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 50, 50))
    img_pix.set_rect(img_pix.irect, (255, 0, 0))  # Red
    
    # Insert the same image twice on page 1
    page1.insert_image(fitz.Rect(100, 100, 150, 150), pixmap=img_pix)
    page1.insert_image(fitz.Rect(200, 200, 250, 250), pixmap=img_pix)
    
    # Page 2: Insert the same image again + a different image
    page2 = doc.new_page()
    page2.insert_text((50, 50), "Page 2 with mixed images", fontsize=12)
    
    # Insert same red image
    page2.insert_image(fitz.Rect(100, 100, 150, 150), pixmap=img_pix)
    
    # Create different image (blue rectangle)
    img_pix2 = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 50, 50))
    img_pix2.set_rect(img_pix2.irect, (0, 0, 255))  # Blue
    page2.insert_image(fitz.Rect(200, 200, 250, 250), pixmap=img_pix2)
    
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


class TestImageDeduplication:
    """Test image deduplication functionality."""
    
    def test_identical_images_get_same_id(self, multi_image_pdf_path):
        """Test that identical images across pages get the same image_id."""
        raw_pdf = RawPDF(multi_image_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        # Should have 2 unique images despite multiple instances
        assert processed_pdf.image_count == 2
        
        # Collect all image IDs from all pages
        all_image_ids = []
        for page in processed_pdf.pages:
            for img_ref in page.image_refs:
                all_image_ids.append(img_ref.image_id)
        
        # Should have multiple references but only 2 unique IDs
        assert len(all_image_ids) > 2  # Multiple references
        assert len(set(all_image_ids)) == 2  # Only 2 unique IDs
    
    def test_different_images_get_different_ids(self, multi_image_pdf_path):
        """Test that different images get unique image_ids."""
        raw_pdf = RawPDF(multi_image_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        # Get all unique image IDs
        unique_ids = set()
        for page in processed_pdf.pages:
            for img_ref in page.image_refs:
                unique_ids.add(img_ref.image_id)
        
        # Should have exactly 2 different IDs
        assert len(unique_ids) == 2
        
        # All images should be retrievable
        for image_id in unique_ids:
            image_bytes = processed_pdf.get_image(image_id)
            assert image_bytes is not None
            assert len(image_bytes) > 0


class TestImageReferenceMapping:
    """Test image reference mapping functionality."""
    
    def test_image_references_have_correct_page_numbers(self, multi_image_pdf_path):
        """Test that ImageReference objects have correct page numbers."""
        raw_pdf = RawPDF(multi_image_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        # Check page 1 image references
        page1 = processed_pdf.get_page(1)
        assert len(page1.image_refs) == 2  # Two instances of same image
        for img_ref in page1.image_refs:
            assert img_ref.page_number == 1
        
        # Check page 2 image references
        page2 = processed_pdf.get_page(2)
        assert len(page2.image_refs) == 2  # One red, one blue
        for img_ref in page2.image_refs:
            assert img_ref.page_number == 2
    
    def test_image_references_have_valid_bounding_boxes(self, multi_image_pdf_path):
        """Test that ImageReference objects have valid bounding boxes."""
        raw_pdf = RawPDF(multi_image_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        for page in processed_pdf.pages:
            for img_ref in page.image_refs:
                # Bounding box should be a tuple of 4 floats
                assert isinstance(img_ref.bbox, tuple)
                assert len(img_ref.bbox) == 4
                
                x0, y0, x1, y1 = img_ref.bbox
                assert isinstance(x0, (int, float))
                assert isinstance(y0, (int, float))
                assert isinstance(x1, (int, float))
                assert isinstance(y1, (int, float))
                
                # x1 should be greater than x0, y1 should be greater than y0
                assert x1 > x0
                assert y1 > y0
    
    def test_image_references_link_to_stored_images(self, multi_image_pdf_path):
        """Test that image references correctly link to stored images."""
        raw_pdf = RawPDF(multi_image_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()
        
        for page in processed_pdf.pages:
            for img_ref in page.image_refs:
                # Should be able to retrieve the image
                image_bytes = processed_pdf.get_image(img_ref.image_id)
                assert image_bytes is not None
                assert len(image_bytes) > 0
                
                # Image ID should exist in the images dictionary
                assert img_ref.image_id in processed_pdf.images