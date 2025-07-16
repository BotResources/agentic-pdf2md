"""
Configuration for PDF processing.
"""
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .exceptions import ConfigurationError
from .models.cancellation_token import CancellationToken
from .models.llm_runner import LLMRunner

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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "screenshot_dpi": self.screenshot_dpi,
            "screenshot_format": self.screenshot_format,
            "image_format": self.image_format,
            "max_image_size": self.max_image_size,
            "include_layout_hints": self.include_layout_hints,
            "parallel_processing": self.parallel_processing,
            "cleanup_intermediate": self.cleanup_intermediate,
            "log_level": self.log_level,
            "log_progress": self.log_progress,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "PreProcessingConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)
    

@dataclass
class ParallelProcessingConfig:
    """Configuration for parallel processing of PDF files."""
    num_workers: int = 10
    cancellation_token: CancellationToken
    generator_runner: LLMRunner
    critic_runner: LLMRunner

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.num_workers <= 0:
            raise ConfigurationError("num_workers must be greater than 0")

    def _validate(self):
        """Validate configuration values."""
        if not isinstance(self.num_workers, int):
            raise ConfigurationError("num_workers must be an integer")
        if self.num_workers <= 0:
            raise ConfigurationError("num_workers must be greater than 0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "num_workers": self.num_workers,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ParallelProcessingConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)
    


@dataclass
class SerialProcessingConfig:
    """Configuration for serial processing of PDF files."""
    backward_pages: int = 1  # Number of pages that will be included as context for each page

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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "backward_pages": self.backward_pages,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "SerialProcessingConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)

@dataclass
class ProcessingConfig:
    """Configuration for processing PDF files."""
    cancellation_token: CancellationToken
    pre_processing: PreProcessingConfig = PreProcessingConfig()
    parallel_processing: Optional[ParallelProcessingConfig] = None  # If None, no parallel processing
    serial_processing: Optional[SerialProcessingConfig] = None  # If None, no serial processing

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self):
        """Validate configuration values."""
        pass # Placeholder for future validation logic
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = {
            "pre_processing": self.pre_processing.to_dict(),
            "parallel_processing": self.parallel_processing.to_dict() if self.parallel_processing else None,
            "serial_processing": self.serial_processing.to_dict() if self.serial_processing else None,
        }
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any], cancellation_token: CancellationToken) -> "ProcessingConfig":
        """Create configuration from dictionary."""
        pre_processing = PreProcessingConfig.from_dict(config_dict.get("pre_processing", {}))
        parallel_processing = ParallelProcessingConfig.from_dict(config_dict["parallel_processing"]) if config_dict.get("parallel_processing") else None
        serial_processing = SerialProcessingConfig.from_dict(config_dict["serial_processing"]) if config_dict.get("serial_processing") else None
        
        return cls(
            pre_processing=pre_processing, 
            parallel_processing=parallel_processing, 
            serial_processing=serial_processing, 
            cancellation_token=cancellation_token,
        )
