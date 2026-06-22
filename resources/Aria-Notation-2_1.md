# Aria Notation
_Specification v2.0_

---

## 1. Why Aria

Aria Notation is a language-agnostic coding style built on two principles:

- **Function, method, and macro names are the documentation.** Each function is an "aria" — self-contained, one voice, named. Reading a function's name tells you exactly what it does. The `main` block is the libretto: a flat sequence of named actions that reads as prose without comments.
- **Rules are identical across all languages.** zsh, Python, JavaScript, Java, awk — same naming, same structure, same error-handling conventions. A developer fluent in Aria reads code in any of those languages without a context switch.

Aria Notation has been applied across projects in multiple problem domains and languages since 2004. The design goal is fast comprehension: a developer encountering an unfamiliar Aria codebase goes to the end of the listing, reads what is being called and in what order, and has an immediate map of the program's logic. Scrolling up from any call, the definition of everything used at that point is always nearby — or in the `import` section at the top.

**When to apply:** all code in an Aria-governed project. No per-language exceptions except where physically impossible (noted per section).

**PEP 8 note:** PEP 8 §2 explicitly states that org style overrides. Aria is the org style. `snake_case` is not used.

---

## 2. Cross-language object references

**Rule:** The same logical entity has the same identifier across all languages, formats, and contexts.

A Python variable, a shell variable, a JSON key, a Java field, a JavaScript property referring to the same concept use identical names. `signingIdentity` in JSON maps to `signingIdentity` in Python, JS, Java, and shell — not `signing_identity`, not `SigningIdentity`. No translation layer; no serialization bugs from naming mismatch.

| Language    | Variable          | Constant      | Class/Type       |
|-------------|-------------------|---------------|------------------|
| zsh / bash  | `signingIdentity` | `MAX_RETRIES` | N/A              |
| Python      | `signingIdentity` | `MAX_RETRIES` | `SigningService` |
| JavaScript  | `signingIdentity` | `MAX_RETRIES` | `SigningService` |
| Java        | `signingIdentity` | `MAX_RETRIES` | `SigningService` |
| JSON key    | `signingIdentity` | `MAX_RETRIES` | N/A              |

**Constants:** `SCREAMING_SNAKE_CASE` in every language, without exception.

**Class and type names:** `PascalCase` universally.

---

## 3. Aria-flavored camelCase

**Form:**

| Identifier kind                             | Form              | Example                  |
|---------------------------------------------|-------------------|--------------------------|
| Function / method / macro                   | `lowerCamelCase`  | `resolveSigningIdentity` |
| Variable / parameter / dict key / JSON key  | `lowerCamelCase`  | `signingIdentity`        |
| Constant (module / file / global scope)     | `SCREAMING_SNAKE` | `MAX_RETRIES`            |
| Class / type / interface                    | `PascalCase`      | `SigningService`         |

**Acronyms:** always written in full caps. Never mixed-case (`Html`, `Api`, `Url`). When an acronym would appear at the start of a `lowerCamelCase` identifier, invert word order so the acronym follows the verb, or substitute a descriptive word.

| ✓ Aria                  | ✗ Not Aria              | Rule applied                                |
|-------------------------|-------------------------|---------------------------------------------|
| `parseHTMLBody`         | `parseHtmlBody`         | Acronym preserved in full caps              |
| `resolveAPIEndpoint`    | `resolveApiEndpoint`    | Acronym preserved                           |
| `parserHTML`            | `HtmlParser`            | Word order inverted to keep acronym         |
| `HTMLParser`            | `HtmlParser`            | Class name: acronym preserved               |
| `requestTimeout`        | `httpRequestTimeout`    | Acronym omitted; redundant in HTTP context  |
| `locator`               | `url`                   | Acronym dropped; core semantic word used    |

**Rules:**
1. Acronyms are ALL-CAPS within any identifier.
2. If an acronym would begin a `lowerCamelCase` name, invert word order (`parserHTML`, not `htmlParser`) or substitute a descriptive word (`locator`, not `url`).
3. If an acronym is redundant given context, omit it (`requestTimeout`, not `httpRequestTimeout`, when the containing object is self-evidently an HTTP request).

**Never:** `snake_case` for functions or variables; `kebab-case` for any identifier (reserved for file names — see §4); mixed conventions within a project.

---

## 4. File naming

Applies to output files, data files, and documentation. Source code files follow the language and project convention for their directory (e.g., all-lowercase module names in Python).

- Word separation: `kebab-case` (hyphen).
- Proper names: preserve original casing (`Aria-Notation`, `SSScore`, `FlySight`).
- Generic descriptor words: lowercase.
- Version (when present): separated from the rest of the name by a hyphen; dots replaced by underscores.
- No spaces; no underscores between words (underscores used only inside version numbers).

| Example                             | Pattern                           |
|-------------------------------------|-----------------------------------|
| `Aria-Notation-reference-2_0.md`    | ProperName + descriptor + version |
| `sign-app.zsh`                      | descriptor + descriptor           |
| `ssscoring-2_99_0-py3-none-any.whl` | project + version + platform info |

File extensions follow language/platform convention without modification.

---

## 5. Naming: functions, methods, variables

### Functions, methods, and macros

**Rule:** Verb or verb-phrase, reads as imperative English. At the call site, function name + arguments form a readable phrase or sentence.

```
resolveSigningIdentity       ✓
assertBundleExists           ✓
sign()                       ✓  — single imperative verb; unambiguous in context
confirmImageIn(zipFile)      ✓  — reads as a sentence at the call site
```

**Call-site readability test:** read the function call with its arguments as an English phrase. `confirmImageIn('~/tmp/sample.zip')` passes. `processData(myFile)` does not.

```
process()       ✗  — what process?
handle()        ✗  — what handle?
sign_bundle()   ✗  — snake_case
SignBundle()    ✗  — PascalCase reserved for types
```

**One responsibility per function.** If describing what it does requires "and," split it. `signAndVerifyBundle` → `signBundle` + `verifyBundle`.

**Readability test:** a developer unfamiliar with this codebase understands what the function does within 3 seconds of reading its name. If not, rename.

### Variables and parameters

**Rule:** Noun or noun phrase, names the thing held — not the operation, not the type.

```
signingIdentity   ✓
bundlePath        ✓
entitlementArgs   ✓
locator           ✓  (not url)
```

```
result   ✗
data     ✗
tmp      ✗
x        ✗  (outside single-iteration loop counters: i, j, k)
url      ✗  — use locator or a descriptive word
```

**Abbreviations:** expand unless the abbreviated form is unambiguous to any reader. `maxRetries` is acceptable; `maxRet` is not.

---

## 6. Define-before-use (Pascal/Wirth)

**Rule:** Every identifier — constant, variable, function — is defined before its first use. Top-to-bottom reading order is always valid. Forward references do not exist in Aria code.

**Within a file:** constants → helper functions in dependency order (callees before callers) → `main`.

| Language   | Enforcement                                                                       |
|------------|-----------------------------------------------------------------------------------|
| Python     | Enforced at module scope (`NameError` at runtime if violated).                    |
| zsh / bash | Enforced at runtime (function must be defined before called).                     |
| JavaScript | Use `const`/`let`. `var` hoisting violates Aria.                                 |
| Java       | Compiler permits forward references in class bodies; Aria does not. Define in dependency order regardless. |

**Mutual recursion** (A calls B, B calls A) is a structural bug. Restructure the code. In Python, function-level `import` statements resolve the underlying module coupling that typically causes mutual recursion.

---

## 7. Structural scaffolding

### File layout

```
[shebang / module docstring / file header]

# +++ constants +++

CONSTANT_ONE = ...
CONSTANT_TWO = ...

# *** functions ***

def firstHelper():
    ...


def secondHelper():
    ...

# *** main ***

firstHelper()
secondHelper()
```

### Blank line discipline

| Context                                  | Blank lines |
|------------------------------------------|-------------|
| Section marker to first item in section  | 1           |
| Between function / method definitions    | 2           |
| Between logical blocks within a function | 1           |
| End of file                              | 1           |

One blank line within a function separates logical sub-blocks. No blank lines between lines that form a single logical unit.

In Python, JS, Java: replace `#` section markers with `//`. Marker text is identical across languages.

### `main` structure

`main` is a flat sequential call list whenever possible. Minimal branching is allowed when the block remains readable; `match/case` and `switch/case` are acceptable. No inline logic that belongs in a named function.

**25-line limit:** if `main` exceeds 25 lines, wrap its body in a `_main()` or `main()` function and have the top-level block call it.

```zsh
# *** main ***

BUNDLE="${1:?usage: $0 <bundle.app> [entitlements.plist]}"
ENTITLEMENTS="${2:-}"

resolveSigningIdentity
assertBundleExists
resolveEntitlements
displaySigningContext
stripStaleSignatures
signBundle
verifyBundle
```

### Closing markers

Every function closes with `} # funcName` in languages with brace delimiters (shell, JS, Java, C).

```zsh
signBundle() {
    codesign --deep --force --options=runtime \
        "${ENT_ARGS[@]}" \
        --sign "$SIGNING_IDENTITY" \
        --timestamp \
        "$BUNDLE"
} # signBundle
```

**Python:** no closing marker. Dedent closes the function.

### zsh / bash specifics

| Setting       | zsh                                  | bash                  |
|---------------|--------------------------------------|-----------------------|
| Shebang       | `#!/usr/bin/env zsh`                 | `#!/usr/bin/env bash` |
| Strict mode   | `emulate -L zsh` + `setopt ERR_EXIT` | `set -eo pipefail`    |
| Stderr output | `print -u2 "msg"`                    | `echo "msg" >&2`      |
| Avoid         | `NO_UNSET` / `set -u`                | same                  |

`emulate -L zsh` locks behavior to standard zsh, ignoring user `.zshrc` aliases and options.

---

## 8. Error-path discipline

**Rule:** All error exits route through a `die` helper. Inline `echo + exit` is not Aria.

### Placement

**Shell scripts:** `die` is the first function defined, immediately after constants.

**Python, Java, JavaScript, and any language with module/package abstractions:** `die` and app-specific exceptions live in a module or package named `errors`. Calling modules import from there; they do not define `die` locally.

```python
# errors.py

def die(message: str, exitCode: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(exitCode)
```

```python
# calling module
from ssscoring.errors import die
```

### `die` for shell

**zsh:**
```zsh
die() {
    print -u2 "error: $1"
    exit ${2:-1}
} # die
```

**bash:**
```bash
die() {
    echo "error: $1" >&2
    exit ${2:-1}
} # die
```

### Guard clauses

Single-condition failure: `condition || die "message" N`

```zsh
[[ -d "$BUNDLE" ]]           || die "'$BUNDLE' is not a directory" 1
[[ -f "$ENTITLEMENTS" ]]     || die "entitlements file not found: $ENTITLEMENTS" 2
[[ -n "$SIGNING_IDENTITY" ]] || die "SIGNING_IDENTITY not defined — set in .env" 99
```

### Branching

Multi-branch logic lives in a named function using full block syntax. One-liner `if` is not Aria except for guard clauses via `||`.

```zsh
resolveEntitlements() {
    ENT_ARGS=()

    if [[ -z "$ENTITLEMENTS" ]]; then
        return 0
    fi

    [[ -f "$ENTITLEMENTS" ]] || die "entitlements file not found: $ENTITLEMENTS" 2
    ENT_ARGS=(--entitlements "$ENTITLEMENTS")
} # resolveEntitlements
```

### Exit code discipline

Each distinct failure mode has a unique exit code. Document exit codes in the `# +++ constants +++` block or inline with the `die` call. Exit code `1` is the generic fallback; all specific failure modes use numbered codes.

---

## 9. Import organization

Applies to Python, JavaScript, Java, and any language with `import`-style declarations.

**Block order:**
1. `from ... import ...` statements — first block
2. `import ...` statements — second block
3. One blank line between the two blocks

**Within each block — sub-group order:**
1. Standard library
2. Third-party packages
3. Current project / package / module

One blank line between sub-groups. All statements within a sub-group sorted lexicographically. No wildcard imports (`from x import *` is not Aria — spell out every imported name).

```python
from io import BytesIO
from pathlib import Path

from haversine import haversine
from haversine import Unit

from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import FT_IN_M
from ssscoring.constants import MAX_ALTITUDE_METERS
from ssscoring.datatypes import JumpResults
from ssscoring.datatypes import JumpStatus
from ssscoring.errors import SSScoringError
from ssscoring.flysight import getFlySightDataFromCSVBuffer
from ssscoring.flysight import getFlySightDataFromCSVFileName

import math
import re
import warnings

import numpy as np
import pandas as pd
```

**Java and JavaScript:** the sub-group ordering (stdlib → third-party → project) and lexicographic sort within sub-groups apply identically. Java has no `from` block; all declarations are `import` form. In JavaScript (ES modules), named imports (`import { x } from 'module'`) correspond to the `from` block; side-effect imports (`import 'module'`) correspond to the `import` block.

---

## 10. Documentation comments

### Toolchain

Python: [`pdoc`](https://pdoc.dev). Docstrings are written in Markdown; `pdoc` renders Markdown and generates hyperlinks from type annotations — which is why types are included in `Arguments` blocks even when already present in the function signature.

Other languages: Java (Javadoc, `/** */` blocks, `@param`/`@return`/`@throws`); JavaScript (JSDoc, same structure); shell (no standard tool — a block comment immediately above the function definition serves the same purpose).

Cross-references in prose use backticks: `` `module.function` ``, `` `ClassName` ``, `` `CONSTANT_NAME` ``.

### What gets documented

- **Public functions, methods, classes, modules:** always documented.
- **Private identifiers (`_` prefix in Python):** no docstring. Not part of the public API; Aria naming explains what they do.

### Module and package level

One sentence describing what the module contains. No author, version, or changelog — those live in project metadata.

```python
"""
Functions and logic for analyzing and manipulating FlySight dataframes.
"""
```

### File header

One line comment above the module docstring, pointing to the license. No copyright block, no author list, no date.

```python
# See: https://github.com/owner/repo/blob/master/LICENSE.txt
```

### Function and method docstrings

**Structure:**

```
"""
[Summary: one sentence, what the function does. Not "This function..."]
[Optional: additional behavior, semantics, or constraints.]

Arguments
---------
    paramName : TypeHint
Description of the parameter.

    param1, param2 : TypeHint
Grouped params of identical type — describe together.

Returns
-------
[Scalar: one sentence.]
[Complex type: bulleted list of fields/keys with types and descriptions.]

[Optional] Raises
-----------------
`ExceptionType` if [condition].

[Optional] Notes
----------------
Implementation rationale not inferable from naming.

[Optional] See
--------------
`qualified.path.to.Reference`
Formal specification or external API reference.
"""
```

**Rules:**

- Summary line: one sentence, ends with period. Declarative or imperative — never "This function returns..." or "This method does...".
- Section headers underlined with `-` to the same length as the header word.
- `Arguments`: 4-space indent before `paramName : TypeHint`; description on the next line at the same indent. Always include the type even if annotated in the signature — `pdoc` needs it to generate links.
- Consecutive params of identical type: group on one line (`exitLat, exitLon : float`).
- `Returns` for scalars: one sentence. For tuples, named tuples, dicts: bulleted list with type and description per field or key.
- `Raises`: backtick-wrapped exception type, lowercase `if`, condition in plain English.
- `Notes`: only for implementation decisions a reader would otherwise question. Not a restatement of the algorithm.
- `See`: backtick-wrapped qualified path plus a short description. Use for standards references or cross-module links.

**Example — standard function:**

```python
def forwardLateralDisplacement(
    jumpData: pd.DataFrame,
    exitLat: float,
    exitLon: float,
    bearing: float,
) -> pd.DataFrame:
    """
    Adds `forwardM` and `lateralM` columns to `jumpData`: signed displacement
    in metres along and perpendicular to the jump run axis from the exit point.
    Positive `forwardM` = moving away from exit; negative = reversed.
    Positive `lateralM` = right of jump run; negative = left.

    Arguments
    ---------
        jumpData : pd.DataFrame
    Performance-window data in SSScoring format.

        exitLat, exitLon : float
    Exit point coordinates (latitude, longitude).

        bearing : float
    Jump run bearing in degrees [0, 360), typically from `jumpRunBearing`.

    Returns
    -------
    Copy of `jumpData` with `forwardM` and `lateralM` columns appended.
    """
```

**Example — dict return:**

```python
    """
    ...

    Returns
    -------
    `dict` with keys:

    - `backFall` : bool — `True` if any reversal detected.
    - `onsetTime` : float | None — `plotTime` at peak forward displacement;
      `None` if no back-fall detected.
    - `forwardReversalM` : float — metres reversed along jump run axis (≥ 0).
    - `lateralReversalM` : float — metres reversed on lateral axis (≥ 0).
    """
```

**Example — raises:**

```python
    """
    ...

    Raises
    ------
    `SSScoringError` if `data` has a length of zero or is not initialized.
    """
```

**Deprecated functions:**

```python
"""
**DEPRECATED** as of version 2.4.0 — use `validateJumpISC` instead. [Original
description continues here, unchanged.]

Arguments
...
"""
```

Bold `**DEPRECATED**` opens the summary line, followed by the version and replacement if one exists. Keep the full docstring intact — deprecated functions still need complete documentation until removed.

### Inline comments

An inline comment earns its place only when intent is not recoverable from naming or structure alone.

**Warranted — explains non-obvious behavior:**

```python
t = jumpResult.table.copy()    # avoid mutation of the caller's data
```

```python
# Use the next 0.1-sec interval if the current tranche has NaN values.
for interval in range(int(column)*10, 10*(int(column)+1)):
```

**Not warranted — restates the code:**

```python
# Increment counter
count += 1

# Return the result
return scores
```

**TODO comments** (`# TODO:`) are acceptable for tracking known gaps during development. They are not documentation. Remove before release or track in the issue system.

## 11 UI text capitalization and Python string conventions

### UI text capitalization (user-facing strings)

**Rule (single, global, no exceptions for controls or titles)**  
Use sentence-style capitalization for every control label, button label, form label, section header, dialog title, window title, menu item, tooltip, placeholder, and status message.

- Capitalize only the first word and any proper nouns, acronyms, product names, or personal names.  
- Lowercase everything else.  
- No title case anywhere in UI chrome.

**Rationale**  
- Delivers homogeneity across all surfaces and both target platforms (macOS + Windows).  
- Matches the preferred prose form.  
- Aligns with modern Microsoft/Windows guidance (sentence-style for UI labels and controls).  
- Permissible under Apple HIG because the guidelines allow choosing one consistent style per element type across the app; cross-platform consistency takes precedence over micro-optimizing for native macOS button labels.  
- Reduces maintenance cost: eliminates perpetual debates on which words receive caps in title case.  
- Supports an approachable, professional voice suitable for a wealth-management desktop companion.

**Examples**

| Surface                  | Before (mixed)                  | After (uniform prose)                  |
|--------------------------|---------------------------------|----------------------------------------|
| Button                   | Import From Excel               | Import from Excel                      |
| Button                   | Review Extracted Data           | Review extracted data                  |
| Button                   | Connect Carta Account           | Connect to Carta account               |
| Form label               | Portfolio Summary               | Portfolio summary                      |
| Dialog title             | Edit Investment Details         | Edit investment details                |
| Window title             | Nomad — Holdings Overview       | Nomad — Holdings overview              |
| Section header           | Recent Activity Feed            | Recent activity feed                   |
| Short action (unchanged) | Save                            | Save                                   |
| Proper noun (always cap) | —                               | Connect to Carta, Claude, Anthropic    |

**Scope**  
Applies to all new and existing strings in the PySide6/Qt6 UI layer (Python literals, Qt Designer .ui files, dynamic `setText()` / `setWindowTitle()` calls). Extracted named entities from documents retain their original casing (they are data, not UI chrome).

**Enforcement**  
- Reference this rule in every PR that touches UI text.  
- Optional: lightweight pre-commit grep to flag strings with two or more consecutive capitalized words (excluding the known proper-noun list).  
- Visual QA on both platforms after any string change.

**Migration from v0.4.12**  
Audit current strings, apply the rule in one pass, rebuild, and confirm layout and readability on macOS and Windows. No functional or layout changes expected.

### Python string constants (code style)

**Rule**  
In all Python source files for Nomad, string constants must use single quotes. Double-quoted string constants are not permitted.

- Preferred: `'example text'`, `'Import from Excel'`, `f'Value: {value}'`  
- Forbidden: `"example text"`, `"Import from Excel"`

**Exception**  
Double quotes (or triple quotes) may be used only when the string content contains an apostrophe (`'`) or when formatting requirements (raw strings, certain f-string or regex patterns, or triple-quoted blocks) make single quotes impractical. Such exceptions must be minimized and justified in the commit message or code comment.

**Rationale**  
- Enforces visual and stylistic homogeneity across the entire codebase.  
- Removes the current mix of single- and double-quoted strings.  
- Works cleanly with the UI text capitalization rule above, because the majority of user-facing strings are defined as Python string constants.  
- Aligns with common Python community preference for single quotes when there is no strong reason to use double quotes.

**Scope**  
Applies to every string literal in `.py` files (including UI strings, log messages, error texts, configuration keys, SQL fragments, etc.). Does not apply to JSON, YAML, or other data files unless they are generated from Python code.

**Enforcement**  
- Add to the project style guide and reference in every Python PR.  
- Optional: ruff, flake8, or a custom pre-commit hook can enforce single-quote preference (e.g., `flake8-quotes` or ruff rule `Q000`).  
- Existing double-quoted strings should be converted in the same migration pass as the UI capitalization audit.

**Examples of conversion**

```python
# Before
label = "Import from Excel"
title = "Edit Investment Details"

# After
label = 'Import from Excel'
title = 'Edit investment details'
```