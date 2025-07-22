"""
Configuration for PDF processing.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from .exceptions import ConfigurationError
from .options import ParallelProcessingOptions, SerialProcessingOptions


logger = logging.getLogger(__name__)


@dataclass
class PreProcessingConfig:
    """Configuration for PDF processing operations."""

    # Screenshot settings
    screenshot_dpi: float = 2.0
    screenshot_format: str = "png"

    # Image processing settings
    image_format: str = "png"
    max_image_size: Optional[int] = None  # Max size in bytes, None for no limit

    # Processing settings
    include_layout_hints: bool = False
    parallel_processing: bool = False

    # Memory management
    cleanup_intermediate: bool = True

    # Logging
    log_level: str = "INFO"
    log_progress: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self):
        """Validate configuration values."""
        if self.screenshot_dpi <= 0:
            raise ConfigurationError("screenshot_dpi must be greater than 0")

        if self.screenshot_format not in ["png", "jpg", "jpeg"]:
            raise ConfigurationError("screenshot_format must be 'png', 'jpg', or 'jpeg'")

        if self.image_format not in ["png", "jpg", "jpeg"]:
            raise ConfigurationError("image_format must be 'png', 'jpg', or 'jpeg'")

        if self.max_image_size is not None and self.max_image_size <= 0:
            raise ConfigurationError("max_image_size must be greater than 0 or None")

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ConfigurationError(f"log_level must be one of {valid_log_levels}")


@dataclass
class ParallelProcessingConfig:
    """Configuration for parallel processing of PDF files."""
    include_page_screenshots: bool = True
    include_page_images: bool = False
    include_previous_pages_raw_text: int = 0  # Number of previous pages to include as context
    include_next_pages_raw_text: int = 0  # Number of next pages to include as context
    include_page_layout_hints: bool = False
    generator_specific_instructions: Optional[str] = None
    critic_specific_instructions: Optional[str] = None
    default_options: Optional[ParallelProcessingOptions] = None  # Will be used if no specific options are provided at runtime    


@dataclass
class SerialProcessingConfig:
    """Configuration for serial processing of PDF files."""
    backward_pages: int = 1  # Number of pages that will be included as context for each page
    include_page_screenshots: bool = True
    include_page_images: bool = False
    include_page_layout_hints: bool = False
    generator_specific_instructions: Optional[str] = None
    critic_specific_instructions: Optional[str] = None
    default_options: Optional[SerialProcessingOptions] = None  # Will be used if no specific options are provided at runtime

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.backward_pages < 0:
            raise ConfigurationError("backward_pages must be non-negative")
    
    def _validate(self):
        """Validate configuration values."""
        if not isinstance(self.backward_pages, int):
            raise ConfigurationError("backward_pages must be an integer")
        if self.backward_pages < 0:
            raise ConfigurationError("backward_pages must be non-negative")


@dataclass
class ProcessingConfig:
    """Configuration for processing PDF files."""
    pre_processing: PreProcessingConfig
    num_workers: int = 10
    parallel_processing: Optional[ParallelProcessingConfig] = None  # If None, no parallel processing
    serial_processing: Optional[SerialProcessingConfig] = None  # If None, no serial processing

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self):
        """Validate configuration values."""
        pass # Placeholder for future validation logic
