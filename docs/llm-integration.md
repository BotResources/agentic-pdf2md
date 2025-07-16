# LLM Integration Guide

This guide explains how to integrate Large Language Models (LLMs) with the agentic-pdf2md library by implementing custom LLM runners.

## 1. Logic of the Implementation

The LLM integration in agentic-pdf2md follows Domain-Driven Design (DDD) principles to maintain clean separation of concerns and enable flexible LLM provider integration.

### Core Concepts

- **Dependency Injection**: The library accepts any LLM implementation through the `LLMRunner` abstract base class
- **Message Abstraction**: Standardized message types (`SystemMessage`, `UserMessage`, `AIMessage`, `ToolResponseMessage`) that work with any LLM provider
- **Tool Support**: Built-in support for tool calling with structured `ToolCall` objects
- **Provider Agnostic**: Your LLM runner implementation handles the provider-specific message formatting and API calls

### Architecture Overview

```python
from agentic_pdf2md.models.llm_runner import LLMRunner
from agentic_pdf2md.models.llm_messages import BaseLLMMessage, AIMessage

# Your implementation
class MyLLMRunner(LLMRunner):
    async def run(self, messages: List[BaseLLMMessage], tools=None) -> AIMessage:
        # Convert messages to provider format
        # Call your LLM provider
        # Convert response back to AIMessage
        pass

# Usage with dependency injection
processor = PDFProcessor(llm_runner=MyLLMRunner())
```

The library will inject your LLM runner at runtime, allowing you to use any LLM provider while maintaining consistent message handling.

## 2. How-to Using SDKs

### 2.1 OpenAI SDK

```python
import asyncio
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from agentic_pdf2md.models.llm_runner import LLMRunner
from agentic_pdf2md.models.llm_messages import (
    BaseLLMMessage, SystemMessage, UserMessage, AIMessage, 
    ToolResponseMessage, ToolCall
)

class OpenAILLMRunner(LLMRunner):
    def __init__(self, api_key: str, model: str = "gpt-4-vision-preview"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def run(
        self, 
        messages: List[BaseLLMMessage], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AIMessage:
        # Convert messages to OpenAI format
        openai_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                openai_messages.append({
                    "role": "system",
                    "content": msg.content
                })
            elif isinstance(msg, UserMessage):
                if msg.images:
                    content = [{"type": "text", "text": msg.content}]
                    for image in msg.images:
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image}"}
                        })
                    openai_messages.append({
                        "role": "user",
                        "content": content
                    })
                else:
                    openai_messages.append({
                        "role": "user",
                        "content": msg.content
                    })
            elif isinstance(msg, AIMessage):
                openai_msg = {
                    "role": "assistant",
                    "content": msg.content
                }
                if msg.tool_calls:
                    openai_msg["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments)
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                openai_messages.append(openai_msg)
            elif isinstance(msg, ToolResponseMessage):
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": msg.id,
                    "content": msg.content
                })
        
        # Make API call
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=tools,
            **kwargs
        )
        
        # Convert response to AIMessage
        message = response.choices[0].message
        tool_calls = []
        
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                ))
        
        return AIMessage(
            content=message.content or "",
            tool_calls=tool_calls if tool_calls else None
        )

# Usage
runner = OpenAILLMRunner(api_key="your-api-key")
```

### 2.2 Anthropic SDK

```python
import json
from typing import List, Optional, Dict, Any
from anthropic import AsyncAnthropic
from agentic_pdf2md.models.llm_runner import LLMRunner
from agentic_pdf2md.models.llm_messages import (
    BaseLLMMessage, SystemMessage, UserMessage, AIMessage, 
    ToolResponseMessage, ToolCall
)

class AnthropicLLMRunner(LLMRunner):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
    
    async def run(
        self, 
        messages: List[BaseLLMMessage], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AIMessage:
        # Extract system message
        system_content = ""
        claude_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_content = msg.content
            elif isinstance(msg, UserMessage):
                if msg.images:
                    content = [{"type": "text", "text": msg.content}]
                    for image in msg.images:
                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image
                            }
                        })
                    claude_messages.append({
                        "role": "user",
                        "content": content
                    })
                else:
                    claude_messages.append({
                        "role": "user",
                        "content": msg.content
                    })
            elif isinstance(msg, AIMessage):
                claude_msg = {
                    "role": "assistant",
                    "content": msg.content
                }
                if msg.tool_calls:
                    claude_msg["content"] = [
                        {"type": "text", "text": msg.content}
                    ]
                    for tc in msg.tool_calls:
                        claude_msg["content"].append({
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.name,
                            "input": tc.arguments
                        })
                claude_messages.append(claude_msg)
            elif isinstance(msg, ToolResponseMessage):
                claude_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.id,
                        "content": msg.content
                    }]
                })
        
        # Make API call
        response = await self.client.messages.create(
            model=self.model,
            system=system_content,
            messages=claude_messages,
            tools=tools,
            **kwargs
        )
        
        # Convert response to AIMessage
        content = ""
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input
                ))
        
        return AIMessage(
            content=content,
            tool_calls=tool_calls if tool_calls else None
        )

# Usage
runner = AnthropicLLMRunner(api_key="your-api-key")
```

### 2.3 Google Gemini SDK

```python
import json
from typing import List, Optional, Dict, Any
import google.generativeai as genai
from agentic_pdf2md.models.llm_runner import LLMRunner
from agentic_pdf2md.models.llm_messages import (
    BaseLLMMessage, SystemMessage, UserMessage, AIMessage, 
    ToolResponseMessage, ToolCall
)

class GeminiLLMRunner(LLMRunner):
    def __init__(self, api_key: str, model: str = "gemini-pro-vision"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    async def run(
        self, 
        messages: List[BaseLLMMessage], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AIMessage:
        # Convert messages to Gemini format
        gemini_messages = []
        system_instruction = ""
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_instruction = msg.content
            elif isinstance(msg, UserMessage):
                parts = [msg.content]
                if msg.images:
                    import base64
                    import io
                    from PIL import Image
                    
                    for image_b64 in msg.images:
                        image_bytes = base64.b64decode(image_b64)
                        image = Image.open(io.BytesIO(image_bytes))
                        parts.append(image)
                
                gemini_messages.append({
                    "role": "user",
                    "parts": parts
                })
            elif isinstance(msg, AIMessage):
                gemini_messages.append({
                    "role": "model",
                    "parts": [msg.content]
                })
            elif isinstance(msg, ToolResponseMessage):
                gemini_messages.append({
                    "role": "user",
                    "parts": [f"Tool response: {msg.content}"]
                })
        
        # Configure model with system instruction
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=self.model.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model
        
        # Make API call
        response = await model.generate_content_async(
            gemini_messages,
            tools=tools,
            **kwargs
        )
        
        # Convert response to AIMessage
        content = response.text or ""
        tool_calls = []
        
        # Handle tool calls if present
        if hasattr(response, 'candidates') and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call'):
                    tool_calls.append(ToolCall(
                        id=f"call_{len(tool_calls)}",
                        name=part.function_call.name,
                        arguments=dict(part.function_call.args)
                    ))
        
        return AIMessage(
            content=content,
            tool_calls=tool_calls if tool_calls else None
        )

# Usage
runner = GeminiLLMRunner(api_key="your-api-key")
```

## 3. How-to Using Frameworks

### 3.1 LangChain

```python
import json
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage, SystemMessage as LCSystemMessage, 
    AIMessage as LCAIMessage, ToolMessage
)
from langchain_core.tools import tool
from agentic_pdf2md.models.llm_runner import LLMRunner
from agentic_pdf2md.models.llm_messages import (
    BaseLLMMessage, SystemMessage, UserMessage, AIMessage, 
    ToolResponseMessage, ToolCall
)

class LangChainLLMRunner(LLMRunner):
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    async def run(
        self, 
        messages: List[BaseLLMMessage], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AIMessage:
        # Convert messages to LangChain format
        lc_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                lc_messages.append(LCSystemMessage(content=msg.content))
            elif isinstance(msg, UserMessage):
                if msg.images:
                    content = [
                        {"type": "text", "text": msg.content}
                    ]
                    for image in msg.images:
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image}"}
                        })
                    lc_messages.append(HumanMessage(content=content))
                else:
                    lc_messages.append(HumanMessage(content=msg.content))
            elif isinstance(msg, AIMessage):
                lc_msg = LCAIMessage(content=msg.content)
                if msg.tool_calls:
                    lc_msg.tool_calls = [
                        {
                            "name": tc.name,
                            "args": tc.arguments,
                            "id": tc.id
                        }
                        for tc in msg.tool_calls
                    ]
                lc_messages.append(lc_msg)
            elif isinstance(msg, ToolResponseMessage):
                lc_messages.append(ToolMessage(
                    content=msg.content,
                    tool_call_id=msg.id
                ))
        
        # Bind tools if provided
        if tools:
            llm_with_tools = self.llm.bind_tools(tools)
        else:
            llm_with_tools = self.llm
        
        # Make API call
        response = await llm_with_tools.ainvoke(lc_messages)
        
        # Convert response to AIMessage
        tool_calls = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tc in response.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.get('id', f"call_{len(tool_calls)}"),
                    name=tc['name'],
                    arguments=tc['args']
                ))
        
        return AIMessage(
            content=response.content,
            tool_calls=tool_calls if tool_calls else None
        )

# Usage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4-vision-preview", api_key="your-api-key")
runner = LangChainLLMRunner(llm)
```

### 3.2 LlamaIndex

```python
import json
from typing import List, Optional, Dict, Any
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
from agentic_pdf2md.models.llm_runner import LLMRunner
from agentic_pdf2md.models.llm_messages import (
    BaseLLMMessage, SystemMessage, UserMessage, AIMessage, 
    ToolResponseMessage, ToolCall
)

class LlamaIndexLLMRunner(LLMRunner):
    def __init__(self, llm: OpenAI):
        self.llm = llm
    
    async def run(
        self, 
        messages: List[BaseLLMMessage], 
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AIMessage:
        # Convert messages to LlamaIndex format
        chat_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                chat_messages.append(ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=msg.content
                ))
            elif isinstance(msg, UserMessage):
                content = msg.content
                if msg.images:
                    # LlamaIndex handles images differently
                    content += "\n[Images provided but not displayed in text]"
                
                chat_messages.append(ChatMessage(
                    role=MessageRole.USER,
                    content=content
                ))
            elif isinstance(msg, AIMessage):
                chat_messages.append(ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=msg.content
                ))
            elif isinstance(msg, ToolResponseMessage):
                chat_messages.append(ChatMessage(
                    role=MessageRole.TOOL,
                    content=msg.content
                ))
        
        # Convert tools to LlamaIndex format
        function_tools = []
        if tools:
            for tool in tools:
                function_tools.append(FunctionTool.from_defaults(
                    fn=lambda **kwargs: None,  # Placeholder
                    name=tool.get('function', {}).get('name', ''),
                    description=tool.get('function', {}).get('description', ''),
                ))
        
        # Make API call
        if function_tools:
            response = await self.llm.achat_with_tools(
                function_tools,
                chat_messages,
                **kwargs
            )
        else:
            response = await self.llm.achat(chat_messages, **kwargs)
        
        # Convert response to AIMessage
        content = str(response.message.content)
        tool_calls = []
        
        # Handle tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tc in response.tool_calls:
                tool_calls.append(ToolCall(
                    id=getattr(tc, 'id', f"call_{len(tool_calls)}"),
                    name=tc.tool_name,
                    arguments=tc.tool_kwargs
                ))
        
        return AIMessage(
            content=content,
            tool_calls=tool_calls if tool_calls else None
        )

# Usage
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4-vision-preview", api_key="your-api-key")
runner = LlamaIndexLLMRunner(llm)
```

## Usage Examples

Once you have implemented your LLM runner, you can use it with the library:

```python
from agentic_pdf2md import ProcessedPDF
from agentic_pdf2md.models.llm_messages import SystemMessage, UserMessage

# Initialize with your LLM runner
runner = OpenAILLMRunner(api_key="your-api-key")

# Create messages
system_msg = SystemMessage("You are a helpful assistant.")
user_msg = UserMessage("Convert this PDF to markdown.", images=["base64_image_data"])

# Use with the library
messages = [system_msg, user_msg]
response = await runner.run(messages)

print(response.content)
if response.tool_calls:
    for tool_call in response.tool_calls:
        print(f"Tool: {tool_call.name}, Args: {tool_call.arguments}")
```

## Error Handling

Always implement proper error handling in your LLM runner:

```python
class RobustLLMRunner(LLMRunner):
    async def run(self, messages, tools=None, **kwargs):
        try:
            # Your implementation
            return await self._make_api_call(messages, tools, **kwargs)
        except Exception as e:
            # Log the error
            logger.error(f"LLM call failed: {e}")
            # Return a default response or re-raise
            return AIMessage(content="I apologize, but I encountered an error processing your request.")
```

This design allows you to swap LLM providers easily while maintaining consistent message handling throughout your application.