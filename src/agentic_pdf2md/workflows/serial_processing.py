"""
This workflow is designed to handle serial processing of PDF files, processing each page sequentially.
"""

from typing import List
from ..models.processed_pdf import ProcessedPDF
from ..config import SerialProcessingConfig

class SerialProcessingWorkflow:
    """Workflow for serial processing of PDF files."""

    def __init__(self, config: SerialProcessingConfig):
        """Initialize the workflow with the given configuration."""
        self.config = config

    async def process_pdf(self, pdf: ProcessedPDF) -> List[str]:
        """Process the PDF file using serial processing."""
        # This method will be implemented to handle the serial processing of the PDF

    async def process_one_page(self, page_number: int) -> str:
        """Process a single page of the PDF."""
        # This method will be implemented to process one page at a time