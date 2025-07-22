"""
Pytest configuration and fixtures.
"""
import pytest
import fitz
import base64
import tempfile
import os


@pytest.fixture
def simple_pdf_path():
    """Create a simple PDF file and return its path."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    
    # Create PDF after closing the temp file
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Test PDF Content", fontsize=12)
    doc.save(tmp_path)
    doc.close()
    
    yield tmp_path
    
    # Cleanup - force close any handles and retry deletion
    try:
        os.remove(tmp_path)
    except PermissionError:
        # On Windows, sometimes files are still locked
        import time
        time.sleep(0.1)
        try:
            os.remove(tmp_path)
        except:
            pass  # Best effort cleanup

@pytest.fixture
def pdf_base64():
    """Create a PDF and return its base64 encoded content."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Base64 PDF Content", fontsize=12)
    
    pdf_bytes = doc.tobytes()
    doc.close()
    
    return base64.b64encode(pdf_bytes).decode('utf-8')

@pytest.fixture
def corrupted_base64():
    """Return an invalid base64 string for testing error handling."""
    return "invalid_base64_content_!@#$%"