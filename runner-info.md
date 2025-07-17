How to add the file ./ssscrunner.py to my PyInstaller package so that it looks for it in the package instead of raising this error:  FileNotFoundError: [Errno 2] No such file or directory: '/Users/ciurana/ssscrunner.py' - the file should be under the package name.
--------------------------------------------------
To ensure **ssscrunner.py** is bundled with your PyInstaller package and loaded from within your package rather than the filesystem (preventing FileNotFoundError), you need to:

1. **Add ssscrunner.py as a data file in your PyInstaller build**.
2. **Access the file within your bundled app using a package-aware method**, such as pkgutil.

## Step 1: Update your PyInstaller command or spec file

**Using the PyInstaller CLI**:  
Add the file via the `--add-data` option in your build command. For example, if your project/package is called `mypackage` and `ssscrunner.py` needs to be bundled under `mypackage`:

```bash
pyinstaller main.py --add-data "ssscrunner.py:mypackage" --onefile
```
This copies `ssscrunner.py` into the `mypackage` folder within the bundled package[1].  
*(On Windows, use semicolon ; instead of colon : in --add-data)*

**Or, using a spec file**:  
Edit the `.spec` file’s `Analysis` section:

```python
a = Analysis(
    ...
    datas=[('ssscrunner.py', 'mypackage')],
    ...
)
```
[4]

## Step 2: Access ssscrunner.py at runtime (from the bundled app)

Do not load via a plain file path; instead, access it using the package context. Example using `pkgutil`:

```python
import pkgutil

# Load ssscrunner.py as bytes from the package
code_bytes = pkgutil.get_data('mypackage', 'ssscrunner.py')
exec(code_bytes)
```
[4]

This approach finds the file *inside* your application package, whether running as a script or from a PyInstaller-built executable.

> The above methods and advice are sourced directly from PyInstaller’s documentation on including non-code/data files and accessing them at runtime using `pkgutil.get_data`[4][1].

If you run PyInstaller this way, **ssscrunner.py** will always be available via your package, and your packaged app will not raise the FileNotFoundError due to missing external files.