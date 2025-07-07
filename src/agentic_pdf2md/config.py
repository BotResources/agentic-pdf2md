"""
Configuration for PDF processing.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .exceptions import ConfigurationError


@dataclass
class ProcessingConfig:
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
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ProcessingConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)