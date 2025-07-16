"""
Class used to run LLMs (Large Language Models) with a given prompt.
We define an abstract base class for LLM runners.
The developer should implement the `run` method to execute the LLM with the provided messages.
"""

from typing import List, Any, Optional, Dict
from abc import ABC, abstractmethod
from .llm_messages import BaseLLMMessage, AIMessage

class LLMRunner(ABC):
    """
    Abstract base class for LLM runners.
    """

    @abstractmethod
    async def run(
        self, 
        messages: List[BaseLLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        *args,
        **kwargs,
    ) -> AIMessage:
        """
        Run the LLM with the given messages and return the response.

        :param messages: List of messages to send to the LLM.
        :param tools: Optional list of tool definitions.
        :return: The AI response message.
        """
        raise NotImplementedError("Subclasses must implement this method.")
