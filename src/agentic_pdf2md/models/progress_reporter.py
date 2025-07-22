from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class ProcessingStage(Enum):
    """Enum representing the stages of PDF processing."""
    INITIALIZATION = "initialization"
    LOADING_PDF = "loading_pdf"
    PREPROCESSING = "preprocessing"
    PARALLEL_PROCESSING = "parallel_processing"
    SERIAL_PROCESSING = "serial_processing"
    FINALIZATION = "finalization"
    COMPLETED = "completed"

@dataclass
class ProgressInfo:
    """Information about the progress of PDF processing."""
    stage: ProcessingStage
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    message: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

class ProgressReporter:
    """Protocol for reporting progress during PDF processing."""

    async def report_progress(self, operation_name, progress: ProgressInfo) -> None:
        """Report the current progress of the PDF processing."""
        raise NotImplementedError("Subclasses must implement this method.")