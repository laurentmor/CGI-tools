<!--SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette-->

<div align="center">

# 🗂️ XMLExtractor

**Extract, clean, validate, and archive XML records from SQL Developer export files.**

[![Tests](https://github.com/laurentmor/CGI-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/laurentmor/CGI-tools/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/laurentmor/CGI-tools/branch/main/graph/badge.svg)](https://codecov.io/gh/laurentmor/CGI-tools)
[![Release](https://img.shields.io/github/v/release/laurentmor/CGI-tools?color=blue)](https://github.com/laurentmor/CGI-tools/releases)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Stars](https://img.shields.io/github/stars/laurentmor/CGI-tools?style=social)](https://github.com/laurentmor/CGI-tools/stargazers)

</div>

---

## What it does

SQL Developer XML exports pack every row's data into a single file. XMLExtractor streams through that file, pulls out each record's XML payload, names it from an ID tag you choose, and writes it as a standalone `.xml` file — with optional cleanup, validation, and ZIP archiving.

```
export.xml  →  xmls/MSG001.xml
               xmls/MSG002.xml
               xmls/MSG003.xml
               ...          →  archive.zip  (optional, AES-256 encrypted)
```

---

## Features

| | |
|---|---|
| ⚡ **Streaming parser** | `iterparse`-based — processes arbitrarily large files with constant memory |
| 🧼 **XML sanitisation** | Strips illegal characters, applies a custom JSON replacement map |
| ✅ **Validation** | Checks XML structure and column existence before extracting |
| 🔒 **AES-256 ZIP** | Optional encrypted archive via `pyzipper` |
| 🏃 **Dry-run mode** | Simulate the full run without writing a single file |
| 📋 **Structured logging** | Timestamped log to `script.log` |
| 📈 **Progress display** | Per-record percentage as extraction proceeds |
| 🔉 **Sound feedback** | Start / done / error WAVs (Windows; `--mute` to silence) |
| 🧪 **119 tests · 97.79% coverage** | pytest suite across Python 3.10, 3.11, 3.12 |

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/laurentmor/CGI-tools.git
cd CGI-tools/XMLExtractor

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1

# 3. Install the package and its dependencies
pip install -e .
```

**Dependencies** (installed automatically via `pyproject.toml`):

| Package | Version | Purpose |
|---|---|---|
| `pyzipper` | ≥ 0.3.6 | AES-256 ZIP encryption |
| `pycryptodomex` | ≥ 3.22.0 | Cryptographic backend for pyzipper |
| `lxml` | ≥ 5.3.1 | Fast XML parsing |

---

## Usage

```bash
python -m xml_extractor <input_file> [output_dir] [options]
```

### Positional arguments

| Argument | Description | Default |
|---|---|---|
| `input_file` | SQL Developer XML export file | *(required)* |
| `output_dir` | Directory for extracted XML files | `xmls` |

### Options

| Flag | Description |
|---|---|
| `--column-name NAME` | Column containing XML data | `RICH_TEXT_NCLOB` |
| `--file-id-tag TAG` | XML tag used as output filename stem | `MessageID` |
| `--z NAME [PASSWORD]` | Create a ZIP archive; add a password for AES-256 encryption |
| `--dry-run` | Simulate without writing any files |
| `--validate` | Validate XML structure only, then exit |
| `--mute` | Suppress WAV sound effects |
| `--skip-pause` | Skip the end-of-run prompt (useful in CI) |
| `--version` | Print version and exit |

### Examples

```bash
# Basic extraction
python -m xml_extractor export.xml

# Custom column and ID tag
python -m xml_extractor export.xml output/ --column-name MY_COL --file-id-tag TxnID

# Encrypted ZIP archive
python -m xml_extractor export.xml output/ --z archive.zip s3cr3tpass

# Dry run — nothing is written to disk
python -m xml_extractor export.xml --dry-run

# Validate XML well-formedness and exit
python -m xml_extractor export.xml --validate
```

---

## Project structure

```
XMLExtractor/
├── src/
│   └── xml_extractor/
│       ├── __init__.py
│       ├── xml_extractor.py   # core extraction engine
│       ├── decorators.py      # @log_exceptions decorator
│       └── version.py         # version resolution (package → git tag → dev)
├── tests/
│   ├── fixtures.py            # shared test helpers
│   ├── conftest.py            # stubs for platform-specific deps
│   └── test_*.py              # 29 test modules · 119 tests
├── sounds/                    # WAV feedback files
├── pyproject.toml             # src-layout packaging
├── pytest.ini                 # coverage configuration
└── requirements.txt           # pinned dependencies
```

---

## Running tests

```bash
# Full suite with coverage report
pytest

# Fail fast on first failure
pytest -x --tb=short

# Open HTML coverage report
pytest && open htmlcov/index.html    # macOS
pytest && start htmlcov/index.html   # Windows
```

Current status: **119 tests · 97.79% coverage · CI green on Python 3.10, 3.11, 3.12**

---

## How it works

1. **Sanitise** — scans the input file line-by-line, strips invalid XML characters, applies `replacements.json`, writes a `.bak` backup only when changes are made.
2. **Validate** — confirms the file is well-formed XML and that the target column exists.
3. **Stream** — `ET.iterparse` yields `<ROW>` end-events one at a time; each subtree is cleared immediately after processing to keep memory flat.
4. **Extract** — the target `<COLUMN>` text is written to `<output_dir>/<ID>.xml`.
5. **Archive** — if `--z` is given, wraps the output directory in a plain or AES-256 encrypted ZIP.

---

## Logging

| Scenario | File |
|---|---|
| Normal run | `script.log` |

Format: `YYYY-MM-DD HH:MM - LEVEL - message`

---

## Author

**Laurent Morissette** · [Twitter/X](https://twitter.com/laurentmor) · [Buy me a coffee ☕](https://www.buymeacoffee.com/laurentMords)

---

<div align="center">

*If this saved you time, a ⭐ is always appreciated.*

</div>