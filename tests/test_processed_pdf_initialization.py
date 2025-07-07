"""
Test ProcessedPDF initialization and processing state management.
"""
import pytest
from unittest.mock import Mock
from agentic_pdf2md import RawPDF, ProcessedPDF
from agentic_pdf2md.config import ProcessingConfig


class TestProcessedPDFInitialization:
    """Test ProcessedPDF initialization."""

    def test_initialization_with_raw_pdf(self, simple_pdf_path):
        """Test ProcessedPDF initializes correctly with RawPDF."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)

        assert processed_pdf.raw_pdf is raw_pdf
        assert processed_pdf.config is not None
        assert isinstance(processed_pdf.config, ProcessingConfig)
        assert not processed_pdf.pages
        assert not processed_pdf.images

    def test_initialization_with_custom_config(self, simple_pdf_path):
        """Test ProcessedPDF initializes with custom config."""
        raw_pdf = RawPDF(simple_pdf_path)
        custom_config = ProcessingConfig(screenshot_dpi=2.0, image_format="jpeg")
        processed_pdf = ProcessedPDF(raw_pdf, custom_config)

        assert processed_pdf.config is custom_config
        assert processed_pdf.config.screenshot_dpi == 2.0
        assert processed_pdf.config.image_format == "jpeg"


class TestProcessingState:
    """Test processing state management."""

    def test_initial_state_not_processed(self, simple_pdf_path):
        """Test that ProcessedPDF starts in unprocessed state."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        assert processed_pdf.page_count == 0
        assert processed_pdf.image_count == 0

    def test_sync_processing_changes_state(self, simple_pdf_path):
        """Test that sync processing changes state correctly."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        processed_pdf.process()

        assert processed_pdf.page_count > 0
    
    @pytest.mark.asyncio
    async def test_async_processing_changes_state(self, simple_pdf_path):
        """Test that async processing changes state correctly."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        await processed_pdf.process_async()
        assert processed_pdf.page_count > 0
    
    def test_double_processing_prevented(self, simple_pdf_path):
        """Test that processing is only done once."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        # Process first time
        processed_pdf.process()
        initial_page_count = processed_pdf.page_count
        # Process second time should not change anything
        processed_pdf.process()
        assert processed_pdf.page_count == initial_page_count
    
    @pytest.mark.asyncio
    async def test_double_async_processing_prevented(self, simple_pdf_path):
        """Test that async processing is only done once."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        # Process first time
        await processed_pdf.process_async()
        initial_page_count = processed_pdf.page_count
        # Process second time should not change anything
        await processed_pdf.process_async()
        assert processed_pdf.page_count == initial_page_count
    
    def test_processing_loads_raw_pdf_if_needed(self, simple_pdf_path):
        """Test that processing loads RawPDF if not already loaded."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        # Ensure raw PDF is not loaded initially
        assert not raw_pdf.is_loaded
        # Processing should load it
        processed_pdf.process()
        assert raw_pdf.is_loaded
    
    @pytest.mark.asyncio
    async def test_async_processing_loads_raw_pdf_if_needed(self, simple_pdf_path):
        """Test that async processing loads RawPDF if not already loaded."""
        raw_pdf = RawPDF(simple_pdf_path)
        processed_pdf = ProcessedPDF(raw_pdf)
        # Ensure raw PDF is not loaded initially
        assert not raw_pdf.is_loaded
        # Processing should load it
        await processed_pdf.process_async()
        assert raw_pdf.is_loaded
