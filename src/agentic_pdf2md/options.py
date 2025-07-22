from typing import Optional
from dataclasses import dataclass
from .models.llm_runner import LLMRunnerOrFactory
from .models.cancellation_token import CancellationToken
from .models.progress_reporter import ProgressReporter


@dataclass
class ParallelProcessingOptions:
    """
    Configuration options for parallel processing of a PDF file.
    """
    generator_runner: LLMRunnerOrFactory
    critic_runner: Optional[LLMRunnerOrFactory] = None
    cancellation_token: Optional[CancellationToken] = None
    progress_reporter: Optional[ProgressReporter] = None


@dataclass
class SerialProcessingOptions:
    """
    Configuration options for serial processing of a PDF file.
    """
    generator_runner: LLMRunnerOrFactory
    md_critic_runner: Optional[LLMRunnerOrFactory] = None
    structure_critic_runner: Optional[LLMRunnerOrFactory] = None
    cancellation_token: Optional[CancellationToken] = None
    progress_reporter: Optional[ProgressReporter] = None
