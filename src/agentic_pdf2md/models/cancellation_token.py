import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CancellationToken:
    """
    A token that can be used to cancel an operation.
    """

    def __init__(self, timeout: Optional[float] = None):
        """
        Initialize the CancellationToken with an optional timeout.
        Args:
            timeout (Optional[float]): Timeout in seconds. If provided, the token will automatically cancel after this duration.
        """
        self._cancelled = False
        self._timeout = timeout # Timeout in seconds
        self._start_time = asyncio.get_event_loop().time() if timeout else None

        logger.debug("CancellationToken created with timeout: %s", timeout)
    
    def cancel(self):
        """
        Manually cancel the token.
        """
        self._cancelled = True
        logger.info("CancellationToken cancelled manually")
    
    @property
    def is_cancelled(self) -> bool:
        """
        Check if the token has been cancelled, either manually or due to timeout.
        """
        if self._cancelled:
            return True
        
        # Check timeout
        if self._timeout and self._start_time:
            current_time = asyncio.get_event_loop().time()
            if current_time - self._start_time > self._timeout:
                self._cancelled = True
                logger.warning("CancellationToken cancelled due to timeout after %s seconds", self._timeout)
                return True
        
        return False
