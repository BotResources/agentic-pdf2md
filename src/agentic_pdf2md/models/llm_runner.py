from typing import List, Any, Optional
from abc import ABC, abstractmethod

class LLMRunner(ABC):
    """
    Abstract base class for LLM runners.
    """

    @abstractmethod
    async def run(
        self, 
        messages: List[Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        *args,
        **kwargs,
    ) -> str:
        """
        Run the LLM with the given prompt and return the response.

        :param prompt: The input prompt to send to the LLM.
        :return: The response from the LLM.
        """
        raise NotImplementedError("Subclasses must implement this method.")
