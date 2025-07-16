"""
LLM Messages Module
This is just a convenient way to define LLM messages.
BaseLLMMessage is an abstract base class that defines the structure of a message.
SystemMessage, UserMessage and AIMessage are concrete implementations of the BaseLLMMessage class.
We define those in the simplest possible way, assuming that the class used by the LLM runner will handle the actual message formatting.
We just need to be able to instantiate the proper message type to pass to the LLM Runner.
For that we will need a way to:
- Create a system message by providing a string.
- Create a user message by providing a string and images as base64 encoded strings.

The AIMessage is used to represent the response from the LLM, we don't instantiate it directly, but it is included to define the type of message 
returned by the LLM Runner.
We only assume that the AIMessage will have a optional parameter tool_calls which will be a list of tool calls made by the LLM.
Each ToolCall will have an id, a name and arguments.

ToolResponseMesssage are messages that include a content which is a string. In case the tool response is a dictionary, content will be a json dump of the dictionary.

```python
from typing import List
from agentic_pdf2md.models.llm_messages import BaseLLMMessage, SystemMessage, UserMessage, AIMessage
from agentic_pdf2md.models.llm_runner import LLMRunner

system_message = SystemMessage("This is a system message.")
user_message = UserMessage("This is a user message.")
chat_history: List[BaseLLMMessage] = [system_message, user_message, ai_message]
llm_runner = LLMRunner() # In real code, this would be a concrete implementation of LLMRunner
llm_response: AIMessage = await llm_runner.run(chat_history)

# For tool calls, the lib will handle those using the following structure:
if llm_response.tool_calls:
    for tool_call in llm_response.tool_calls:
        print(f"Tool call: {tool_call.name} with arguments {tool_call.arguments}")

# Tool responses will be generated like this:
from agentic_pdf2md.models.llm_messages import ToolResponseMessage
# If the tool returns a string:
tool_response = ToolResponseMessage(id=tool_call.id, content=tool_implementation(tool_call.arguments))
# If the tool returns a dictionary:
tool_response = ToolResponseMessage(id=tool_call.id, content=json.dumps(tool_implementation(tool_call.arguments)))

# Then the LLM will be called back like this:
chat_history.append(llm_response)
chat_history.append(tool_response)
llm_response = await llm_runner.run(chat_history)
```
"""

from abc import ABC
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json

class BaseLLMMessage(ABC):
    """Abstract base class for LLM messages."""
    pass

@dataclass
class SystemMessage(BaseLLMMessage):
    """System message containing instructions for the LLM."""
    content: str

@dataclass
class UserMessage(BaseLLMMessage):
    """User message containing text and optional images."""
    content: str
    images: Optional[List[str]] = None  # Base64 encoded images    

@dataclass
class ToolCall:
    """Represents a tool call made by the LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class AIMessage(BaseLLMMessage):
    """AI response message with optional tool calls."""
    content: str
    tool_calls: Optional[List[ToolCall]] = None

@dataclass
class ToolResponseMessage(BaseLLMMessage):
    """Tool response message containing the result of a tool call."""
    id: str  # References the tool call ID
    content: str  # String content or JSON dump of dict response

    @classmethod
    def from_result(cls, tool_call_id: str, result: Any) -> "ToolResponseMessage":
        """Create a ToolResponseMessage from a tool call result."""
        if isinstance(result, str):
            content = result
        else:
            content = json.dumps(result)
        return cls(id=tool_call_id, content=content)
