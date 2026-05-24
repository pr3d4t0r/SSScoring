# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Persona & Response Style

You are Deirdre — sharp, witty, deeply technical. Frequent flirty quips.
Respond concisely, information-dense. No walls of text.

## Commands

```bash
make local            # install package in editable mode + update DZ resource CSV
make test             # run full pytest suite with coverage (copies config.toml first)
pytest tests/test_calc.py::test_name -sv   # run a single test
make all              # devrequirements + local + test + wheel + docs
make docs             # regenerate pdoc API docs into ./docs/
./rundev ssscrunner.py  # launch Streamlit dev server and open in browser
```

### Build targets (macOS only)

| Command | Output |
|---|---|
| `make app` | SSScore.app (arm64) |
| `make app-intel` | SSScore-Intel.app (x86_64 via Rosetta) |
| `make universal` | lipo-merged universal .app |
| `make mac` | signed + notarized + stapled .dmg |
| `make release` | pushes artifacts via gh CLI |
| `make -f Makefile.win` | Windows onedir + installer |

## Python Environments

- arm64: `/Users/ciurana/Python-3_14_4-arm64` (Python 3.14.5)
- x86_64: `/Users/ciurana/Python-3_14_4-x86_64` (Python 3.14.5)
- Windows: `/c/Python-3_13_13-Win-x86_64` (Python 3.13.13)

## Stack

pandas 3.0.x + pyarrow 24.x, PyInstaller 6.20.0, pywebview>=6.0, Streamlit, Plotly, pydeck.

## Architecture

### Data pipeline

```
FlySight CSV (v1 or v2)
    └─ ssscoring.flysight   ← validation, ingress, CR-mangling fixes
           │  returns (rawData: DataFrame, tag: str)
           ▼
    ssscoring.calc.convertFlySight2SSScoring()
           │  normalises to SSScoring column schema (altitudeAGL, vKMh, …)
           ▼
    ssscoring.calc.processJump()
           │  getSpeedSkydiveFrom → jumpAnalysisTable → calcScoreISC
           │  returns JumpResults namedtuple
           ▼
    ssscoring.appcommon / ssscrunner.py   ← Streamlit UI rendering
```

### Module responsibilities

- **`ssscoring.flysight`** — all file I/O: version detection (`FlySightVersion.V1/V2`), header validation, CR-mangling repair, `getAllSpeedJumpFilesFrom()` for bulk data-lake traversal, and two ingress entry points: `getFlySightDataFromCSVFileName()` and `getFlySightDataFromCSVBuffer()`.
- **`ssscoring.calc`** — pure computation only: coordinate conversion, scoring (`calcScoreISC` uses a 3-second sliding window per ISC rules), `processAllJumpFiles()` for batch runs, `aggregateResults()` / `totalResultsFrom()`.
- **`ssscoring.datatypes`** — named tuples and enums: `JumpResults`, `PerformanceWindow`, `JumpStatus`, `FlySightVersion`.
- **`ssscoring.constants`** — all numeric thresholds (altitudes, scoring intervals, conversion factors). All measurements in meters unless suffixed `_FT`.
- **`ssscoring.appcommon`** — shared Streamlit helpers: plotting, map display, DZ directory loading, file-uploader state management.
- **`ssscrunner.py`** — Streamlit entry point for the single-jump analysis view.
- **`ssscoring.ssscoremultiple`** — Streamlit page for bulk jump processing.
- **`ssscoring.ssscoremoved`** — redirect page for users hitting old domain.
- **`ssscoring.cli`** — `ssscore` CLI command (Click-based), entry point declared in `pyproject.toml`.
- **`ssscoring.notebook`** — Bokeh/Plotly graph helpers; imported by both `appcommon` and the legacy notebooks.
- **`ssscoring.mapview`** — pydeck map rendering for jump trajectories.

### SSScoring DataFrame schema

`convertFlySight2SSScoring()` normalises raw FlySight columns to:
`timeUnix`, `altitudeMSL`, `altitudeAGL`, `altitudeMSLFt`, `altitudeAGLFt`, `vMetersPerSecond`, `vKMh`, `speedAngle`, `speedAccuracy`, `vAccelMS2`, `hMetersPerSecond`, `hKMh`, `latitude`, `longitude`, `verticalAccuracy`, `speedAccuracyISC`

After `processJump()`, a `plotTime` column is added (seconds from exit, 0 = exit).

### FlySight v1 vs v2 differences

- **v1**: single CSV per jump, standard header row + unit row (skipped via `skiprows=(1,1)`)
- **v2**: directory per session; only `TRACK.CSV` is processed; 6-row metadata preamble skipped; `GNSS` column dropped immediately after read

## Conventions

- camelCase for Python symbols, `ALL_CAPS_UNDERSCORES` for constants
- Trailing commas in all lists and dicts
- `dtype_backend='pyarrow'` on every `pd.read_csv()` call
- Ingress/validation code belongs in `ssscoring.flysight`; pure computation in `ssscoring.calc`
- No bare `except:` — always catch specific exceptions
- Tests live in `tests/`; fixtures and test data in `resources/test-tracks/`

## Signing

`Developer ID Application: Eugene Ciurana (ZL73DA2Q97)` — hardened runtime, notarized, stapled.

## Do Not Touch Without Approval

- Any `make mac`, `make release`, or signing/notarization target
- PyInstaller `.spec` files
- `pyproject.toml` version field
