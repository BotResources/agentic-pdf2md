import logging
import json
import uuid
from typing import List, Optional
from agentic_pdf2md.models.llm_runner import LLMRunner
from agentic_pdf2md.models.llm_messages import AIMessage, BaseLLMMessage

logger = logging.getLogger(__name__)


class FakeLLMRunner(LLMRunner):
    """A fake LLM runner for testing purposes."""
    
    def __init__(self, responses: Optional[List[AIMessage]] = None, llm_runner_id: Optional[str] = None):
        """Initialize the fake LLM runner with optional responses."""
        self.llm_runner_id = llm_runner_id
        self.responses = responses
        self.index = 0

    async def run(
            self, 
            messages: List[BaseLLMMessage],
            tools: Optional[List[dict]] = None,
            **kwargs,
        ) -> AIMessage:
        """
        Simulate running the LLM with the provided messages.
        If no responses are provided, return what was passed in the last message in as an AIMessage.
        If a list of responses is provided - in the init - return the next response in the list.
        """
        if not messages:
            raise ValueError("No messages provided to run the LLM.")
        # logging the messages for debugging
        logger.debug("Running Fake LLM with messages:\n%s\n", ", ".join([msg.content for msg in messages]))
        logger.debug("Using tools:\n%s\n", json.dumps(tools, indent=2) if tools else "None")
        # In a real implementation, this would call the LLM API
        if self.responses:
            response = self.responses[self.index]
            self.index = (self.index + 1) % len(self.responses)
        else:
            # If no responses are provided, return the last message as an AIMessage
            last_message = messages[-1] if messages else BaseLLMMessage()
            response = AIMessage(content=last_message.content)
        logger.debug("Fake LLM response:\n%s\n", response.content)
        return response

    def reset_index(self):
        """Reset the index to start from the first response again."""
        self.index = 0

    def set_responses(self, responses: List[AIMessage], reset_index: bool = True):
        """Set the responses to be returned by the fake LLM runner."""
        self.responses = responses
        if reset_index:
            self.reset_index()

def fake_llm_runner_factory(responses: Optional[List[AIMessage]] = None) -> FakeLLMRunner:
    """
    Factory function to create a FakeLLMRunner instance with optional responses.
    
    Args:
        responses: Optional list of AIMessage responses to return.
    
    Returns:
        FakeLLMRunner: An instance of the fake LLM runner.
    """
    llm_runner_id = str(uuid.uuid4())
    return FakeLLMRunner(responses=responses, llm_runner_id=llm_runner_id)