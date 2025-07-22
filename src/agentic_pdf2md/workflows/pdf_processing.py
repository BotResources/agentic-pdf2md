import asyncio
import logging
from typing import Optional, Union
from ..config import ProcessingConfig
from ..options import ParallelProcessingOptions, SerialProcessingOptions
from ..models.cancellation_token import CancellationToken
from ..models.raw_pdf import RawPDF
from ..models.processed_pdf import ProcessedPDF
from ..models.markdow_representation import MarkdownRepresentation
from ..models.processing_future import ProcessingFuture
from ..models.progress_reporter import ProgressInfo, ProcessingStage
from ..exceptions import OperationCancelledException

logger = logging.getLogger(__name__)


class PDFProcessingWorkflow:
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.main_reporter = config.progress_reporter if config.progress_reporter else None
        self.cancellation_token: CancellationToken = config.cancellation_token
        self.raw_pdf: RawPDF = None
        self.processed_pdf: ProcessedPDF = None
        self.markdown_representation: MarkdownRepresentation = None
        self.default_parallel_processing_options = config.parallel_processing.default_options if config.parallel_processing else None
        self.default_serial_processing_options = config.serial_processing.default_options if config.serial_processing else None

        # Check if we have a parallel processing configuration and or a serial processing configuration
        if config.parallel_processing is None and config.serial_processing is None:
            logger.warning('No processing configuration provided for either parallel or serial processing. The PDF will *NOT* be transformed in a markdown.')

    async def process_pdf(
            self, 
            file_path: str = None, 
            base64_content: str = None,
            parallel_processing_options: Optional[ParallelProcessingOptions] = None,
            serial_processing_options: Optional[SerialProcessingOptions] = None,
        ) -> ProcessingFuture[MarkdownRepresentation]:
        """
        Start processing PDF in background. Returns immediately.
        
        Args:
            file_path: Path to PDF file
            base64_content: Base64 encoded PDF content
            cancel_token: Shared cancellation token (can be used by multiple operations)
            progress_reporter: Progress reporting function
        
        Returns:
            ProcessingFuture: Promise-like object to handle the result
        """
        if not file_path and not base64_content:
            raise ValueError("Either file_path or base64_content must be provided.")
        if file_path:
            operation_name = f"Processing PDF from file: {file_path}"
        else:
            operation_name = "Processing PDF from base64 content"
        future = ProcessingFuture[MarkdownRepresentation](operation_name=operation_name)

        task = asyncio.create_task(
            self._process_pdf_background(
                parallel_processing_options=parallel_processing_options,
                serial_processing_options=serial_processing_options,
                file_path=file_path,
                base64_content=base64_content,
                future=future
            )
        )

        if self.main_reporter:
            self.main_reporter.report_progress(
                operation_name=operation_name,
                progress_info=ProgressInfo(
                    stage=ProcessingStage.INITIALIZATION,
                    message="Starting PDF processing",
                )
            )

        future._task = task  # Set the task in the future object
        return future
        
    async def _process_pdf_background(
            self,
            parallel_processing_options: ParallelProcessingOptions,
            serial_processing_options: SerialProcessingOptions,
            file_path: str = None,
            base64_content: str = None,
            future: ProcessingFuture[MarkdownRepresentation] = None
        ):
        """
        Background task to process the PDF file.
        
        Args:
            file_path: Path to PDF file
            base64_content: Base64 encoded PDF content
            cancel_token: Shared cancellation token
            future: ProcessingFuture object to handle the result
        """
        try:
            # Load the raw PDF
            self.raw_pdf = RawPDF(file_path=file_path, base64_content=base64_content)
            await self.raw_pdf.load_async()

            # Pre-process the PDF
            self.processed_pdf = ProcessedPDF(raw_pdf=self.raw_pdf)
            await self.processed_pdf.process_async()

            # Convert to Markdown representation
            # Not implemented yet, but this is where the conversion logic would go
            
        except asyncio.CancelledError:
            if future:
                await future._fail(OperationCancelledException("PDF processing was cancelled."))
        except Exception as e:
            if future:
                await future._fail(e)
