# agentic-pdf2md

## Run tests
To run the tests for the `agentic-pdf2md` package, you can use the following command:

```bash
pytest tests
```

Note that the warnings about the DeprecationWarning: builtin type SwigPyPacked has no __module__ attribute are related to the PyMuPDF package.
Here is the issue on the PyMuPDF GitHub repository: [PyMuPDF Issue #3931](https://github.com/pymupdf/PyMuPDF/issues/3931)
Here is the corresponding issue on swig: [SWIG Issue #2881](https://github.com/swig/swig/issues/2881)