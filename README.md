# agentic-pdf2md

## Overview

`agentic-pdf2md` is a Python package designed to convert PDF files into Markdown format using agents to process the content.
It supports both parallel and serial processing configurations, allowing for efficient handling of large PDF files.
The fastest method is the parallel processing method, and it is also the recommended method for most use cases.
The serial processing method is only recommended for use cases where you need to have a consistent title structure across all pages, such as when you plan to use this structure to create semanticly consistent chunks for indexing in a vector database.

The package is agnostic to the specific LLM (Large Language Model) used for processing, allowing users to integrate their preferred LLM. It is also agnostic of the way the LLM is called, meaning you can use providers SDKs, good all fashioned REST APIs if you're crazy enough, or frameworks like LangChain or LlamaIndex.

The package is also optimized for local deployment, including support for a worker pool to avoid overloading the local LLMs with too many requests at once.

## Key concepts

### LLM Runners and Messages

In order to process the PDF files in an agnostic way, the package uses LLM runners and messages that are wrappers around the LLMs and their messages. To use the package, you'll need to implement your own LLM runner that is compatible with the package. The package provides a base class for LLM runners, which you can extend to create your own implementation.

Ìn a similar way, the package uses different types of messages:
* `SystemMessage`: A message that is used to provide the system prompt to the LLM.
* `UserMessage`: A message that is used to provide the user prompt to the LLM. Those messages might contain images.
* `AIMessage`: A message that is used to provide the assistant's response to the LLM.
* `ToolCall`: A message that is used to call a tool, such as an image processing agent.
* `ToolResponseMessage`: A message that is used to provide the response from a tool call.

As you might use a framework that already provides a SystemMessage, our recommendation is to import the `agentic_pdf2md` as apd and use the `apd.SystemMessage`, `apd.UserMessage`, `apd.AIMessage`, `apd.ToolCall`, and `apd.ToolResponseMessage` classes to create your messages. 

```python
import agentic_pdf2md as apd

system_message = apd.SystemMessage("You are a helpful assistant.")
user_message = apd.UserMessage("What is the capital of France?")
```

### Cancellation Tokens

As processing large PDF files can generate thousands of requests to the LLM, it is important to be able to cancel the processing at any time. The package provides a `CancellationToken` class that can be used to cancel the processing of a PDF file. You can create a cancellation token and pass it to the processing configuration, and then call the `cancel()` method on the token to cancel the processing.

```python
from agentic_pdf2md import CancellationToken

cancellation_token = CancellationToken()

# and when you want to cancel the processing:
cancellation_token.cancel()  # This will raise an OperationCancelledException in the processing future and prevent any further processing.
```

Note that it is also possible to set a timeout for the cancellation token, which will automatically cancel the processing after a certain amount of time. This is useful for long-running processes that you want to limit to a certain duration.

```python
cancellation_token = CancellationToken(timeout=3600)  # Cancel after 1 hour
```

### Progress Reporters

The full processing of a PDF can be very long. With a large PDF file with a lot of images and 100+ pages, it can take several hours to process the file in serial mode. Parallel mode can also be very long when the number of workers is low.
In order to provide feedback to the user about the progress of the processing, the package provides a `ProgressReporter` class that can be used to report the progress of the processing. You can create a progress reporter and pass it to the processing configuration

### Processing Futures

As the processing might be a very long running task, it is *not* recommended to run it in the main thread or to `await` it directly. However we usually want to be able to do something with the result of the processing, such as saving it to a file or sending it to a vector database.
To handle this we use a javascript-like `Future` object that can be used to get the result of the processing when it is ready. The `ProcessingFuture` class is used to represent the result of the processing, and it can be used to get the result or to check if the processing is still running.

### Configuration

You have to provide configuration objects to the processing methods.
To run in parallel mode, you need to provide a `ParallelProcessingConfig` object.
To run in serial mode, you need to provide a `SerialProcessingConfig` object.

Note that in most cases, you will want to use the `ParallelProcessingConfig` object, as it is the fastest method and the recommended method for most use cases.

If you provide both configurations, the pdf will be processed twice, once in parallel mode and once in serial mode. This is useful in case you want to provide fast results to the user with the parallel processing, and then provide a more accurate result with the serial processing.

## Examples

We will add examples in the future, but for now you can check out the tests in the `tests` directory.

## To do

- [ ] Implement the ParallelProcessing workflow.
- [ ] Implement the SerialProcessing workflow.
- [ ] Add more examples in the documentation, including a full example using Gemini Flash 2.5 and another using local LLM, especially Gemma 3n.
- [ ] Add more tests for the package.

## Contributing

If you would like to contribute to the `agentic-pdf2md` package, please follow these steps:
1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with a clear message.
4. Push your changes to your forked repository.
5. Create a pull request against the main branch of the original repository.
6. Ensure that your code passes all tests and adheres to the project's coding standards.
7. Provide a clear description of your changes in the pull request.

## Installation

The package is not finished yet, therefore it is not available on PyPI.
However, you can install it directly from the source code by cloning the repository and running the setup script.


```bash
git clone git@github.com:BotResources/agentic-pdf2md.git
cd agentic-pdf2md
pip install -e .
```

### Dependencies

You can install the dependencies using the following command:

```bash
pip install -r requirements.txt
```

You can also install the development dependencies using the following command:

```bash
pip install -r requirements-dev.txt
```

## Testing

### Running Tests

To run the tests for the `agentic-pdf2md` package, you can use the following command:

```bash
pytest tests
```

Note that the warnings about the DeprecationWarning: builtin type SwigPyPacked has no __module__ attribute are related to the PyMuPDF package.
Here is the issue on the PyMuPDF GitHub repository: [PyMuPDF Issue #3931](https://github.com/pymupdf/PyMuPDF/issues/3931)
Here is the corresponding issue on swig: [SWIG Issue #2881](https://github.com/swig/swig/issues/2881)

### Running Tests with Coverage
