What's the programmatic way to start a Streamlit application from a Python program and executing the code in a module and not a source Python file?
--------------------------------------------------
To programmatically start a Streamlit application from a Python script and execute code in a module (not just a source file), you can leverage Streamlit's internal CLI API. As of Streamlit 1.32.2, this can be done as shown below.

```python
from streamlit.web import cli

if __name__ == "__main__":
    # Run a module by providing its import path with the -m flag
    cli.main_run(["-m", "your_module_name"])
```

Replace your_module_name with the actual Python module name you want to run (do not include .py). This mirrors the CLI command:

```bash
streamlit run -m your_module_name
```

**Key points:**
- Using cli.main_run allows running your app programmatically, similar to using streamlit run from the command line[2].
- Supplying ["-m", "your_module_name"] as arguments tells Streamlit to execute the module instead of a file, matching the typical -m convention in Python[2].
- This enables execution of code in a proper Python module, which is more flexible than using only a source file.

For more details:
- Streamlit documentation on running as a module: [1][5]
- Example of calling Streamlit from a Python script: [2]

References:
- [Streamlit Docs: Run Your App](https://docs.streamlit.io/develop/concepts/architecture/run-your-app)[1]
- [Ploomber: Running a Streamlit app from a Python script](https://ploomber.io/blog/streamlit-from-python/)[2]
- [Streamlit Docs: Main Concepts](https://docs.streamlit.io/get-started/fundamentals/main-concepts)[5]
