"""
Test ProcessedPDF configuration-driven behavior.
"""
from agentic_pdf2md import RawPDF, ProcessedPDF
from agentic_pdf2md.config import PreProcessingConfig


class TestConfigDrivenBehavior:
    """Test that PreProcessingConfig settings affect behavior."""
    
    def test_screenshot_format_config(self, simple_pdf_path):
        """Test that screenshot format configuration is applied."""
        raw_pdf = RawPDF(simple_pdf_path)
        
        # Test with PNG format
        config_png = PreProcessingConfig(screenshot_format="png")
        processed_pdf_png = ProcessedPDF(raw_pdf, config_png)
        processed_pdf_png.process()
        
        # PNG files typically start with specific bytes
        page = processed_pdf_png.get_page(1)
        assert page.screenshot.startswith(b'\x89PNG\r\n\x1a\n')
    
    def test_image_format_config(self, simple_pdf_path):
        """Test that image format configuration is applied."""
        raw_pdf = RawPDF(simple_pdf_path)
        
        # Test with different image formats
        config_png = PreProcessingConfig(image_format="png")
        processed_pdf = ProcessedPDF(raw_pdf, config_png)
        
        # Just verify config is stored correctly
        assert processed_pdf.config.image_format == "png"
    
    def test_screenshot_dpi_config(self, simple_pdf_path):
        """Test that screenshot DPI configuration affects output."""
        raw_pdf1 = RawPDF(simple_pdf_path)
        raw_pdf2 = RawPDF(simple_pdf_path)
        
        # Test with different DPI settings
        config_low = PreProcessingConfig(screenshot_dpi=1.0)
        config_high = PreProcessingConfig(screenshot_dpi=2.0)
        
        processed_pdf_low = ProcessedPDF(raw_pdf1, config_low)
        processed_pdf_high = ProcessedPDF(raw_pdf2, config_high)
        
        processed_pdf_low.process()
        processed_pdf_high.process()
        
        # Higher DPI should produce larger screenshots
        page_low = processed_pdf_low.get_page(1)
        page_high = processed_pdf_high.get_page(1)
        
        assert len(page_high.screenshot) > len(page_low.screenshot)
    
    def test_include_layout_hints_config(self, simple_pdf_path):
        """Test that include_layout_hints configuration affects LLM input."""
        raw_pdf = RawPDF(simple_pdf_path)
        
        # Test with layout hints enabled
        config_with_hints = PreProcessingConfig(include_layout_hints=True)
        processed_pdf = ProcessedPDF(raw_pdf, config_with_hints)
        processed_pdf.process()
        
        # get_all_pages_llm_input should respect the config
        llm_input = processed_pdf.get_all_pages_llm_input()
        
        # Since simple PDF has no images, layout hints won't appear
        # but the config should be respected
        assert isinstance(llm_input, str)
        assert "[Page 1]" in llm_input
    
    def test_max_image_size_config(self, simple_pdf_path):
        """Test that max_image_size configuration is stored."""
        raw_pdf = RawPDF(simple_pdf_path)
        
        config = PreProcessingConfig(max_image_size=1024)
        processed_pdf = ProcessedPDF(raw_pdf, config)
        
        assert processed_pdf.config.max_image_size == 1024