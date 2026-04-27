# HISTMessagesGenerator

<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Laurent Morissette -->

Generate `HIST` interface SQL `INSERT` statements from an XML file exported out of SQL Developer (`<ROWS>` format).  
The tool reads instrument records, resolves each product type to its internal instrument class, and emits a ready-to-execute SQL script that can be run against the target trading system database.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Python API](#python-api)
  - [Input XML Format](#input-xml-format)
  - [Output SQL Format](#output-sql-format)
- [Supported Product Types](#supported-product-types)
- [Development](#development)
  - [Setting Up](#setting-up)
  - [Running Tests](#running-tests)
  - [Test Suite Overview](#test-suite-overview)
  - [Coverage](#coverage)
  - [Linting](#linting)
- [Architecture](#architecture)
- [Known Quirks](#known-quirks)
- [License](#license)

---

## Overview

In the target trading system, a **HIST** event replays the full history of an instrument to a downstream interface. This tool automates the creation of the `outgoing_intrfc_e` INSERT statements required to trigger those events — a process that is otherwise done by hand, one instrument at a time.

**What it does:**

1. Parses a `<ROWS>` XML export from SQL Developer
2. Validates the XML structure and required columns
3. Deduplicates instruments (first occurrence wins)
4. Resolves each `TYPE_` code (e.g. `DLC`) to its internal instrument class string (e.g. `documentary_lc`)
5. Generates a SQL file containing:
   - A `SELECT` verification query (run before and after)
   - One `INSERT INTO outgoing_intrfc_e` per unique instrument
   - A `COMMIT`

---

## Project Structure

```
HISTMessagesGenerator/
├── conftest.py                        # Root pytest path bootstrap (do not remove)
├── pytest.ini                         # Test runner configuration
├── pyproject.toml                     # Project metadata, dependencies, build config
│
├── src/
│   └── hist_message_generator/        # Importable package (no trailing 's')
│       ├── __init__.py                # Public API re-exports + runpy guard
│       ├── hist_messages_generator.py # Core class + CLI entry point
│       ├── logging_decorators.py      # @log_exceptions decorator
│       ├── ProductClassResolver.py    # ProductType / InstrumentClass enums + resolve_class()
│       └── version.py                 # Version resolution (metadata → git → "dev")
│
└── tests/
    ├── conftest.py                    # pytest fixtures (generators, XML files)
    ├── fixtures.py                    # Shared XML string constants + make_xml()
    ├── test_hist_messages_generator.py
    ├── test_init.py
    ├── test_integration.py
    ├── test_logging_decorators.py
    ├── test_performance.py
    ├── test_product_class_resolver.py
    ├── test_regression.py
    ├── test_version.py
    └── test_coverage_gaps.py
```

---

## Requirements

- Python ≥ 3.11
- [`rich`](https://github.com/Textualize/rich) — console log formatting

---

## Installation

### From source (development)

```bash
git clone https://github.com/laurentmor/CGI-tools.git
cd CGI-tools/HISTMessagesGenerator

# Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Production install

```bash
pip install .
```

---

## Usage

### Command Line

```bash
hist-gen <input_file> <customer_id> <bank> [--log-file PATH] [--version]
```

| Argument | Type | Required | Description |
|---|---|---|---|
| `input_file` | positional | ✔ | Path to the SQL Developer XML export |
| `customer` | positional | ✔ | Customer ID embedded in the SQL statements |
| `bank` | positional | ✔ | Bank code embedded in the SQL statements |
| `--log-file` | option | ✗ | Log file path (default: `HISTMessagesGenerator.log`) |
| `--version` | flag | ✗ | Print version and exit |

**Example:**

```bash
hist-gen export.xml CUST_001 BANKX --log-file run.log
```

This produces `sql_statements.sql` in the current working directory.

### Python API

```python
from hist_message_generator import HISTMessagesGenerator

gen = HISTMessagesGenerator(
    input_file="export.xml",
    customer="CUST_001",
    bank="BANKX",
    log_file="run.log",          # optional
    enable_file_logging=True,    # optional, default True
)
gen.run()
# → writes sql_statements.sql to the current working directory
```

### Input XML Format

The input must be a SQL Developer `<ROWS>` export containing at minimum these three columns:

```xml
<ROWS>
  <ROW>
    <COLUMN NAME="INSTRUMENT_ID">LC2024-001</COLUMN>
    <COLUMN NAME="TYPE_">DLC</COLUMN>
    <COLUMN NAME="CUSTOMER_PARTY_TYPE">BUYER</COLUMN>
  </ROW>
  <ROW>
    <COLUMN NAME="INSTRUMENT_ID">GUA2024-042</COLUMN>
    <COLUMN NAME="TYPE_">GUA</COLUMN>
    <COLUMN NAME="CUSTOMER_PARTY_TYPE">APPLICANT</COLUMN>
  </ROW>
</ROWS>
```

- Leading/trailing whitespace in column values is stripped automatically.
- Duplicate `INSTRUMENT_ID` values are deduplicated; the **first occurrence wins**.
- Missing required columns raise a `ValueError` listing which columns are absent.

### Output SQL Format

```sql
-- HIST for customer CUST_001 - 2 Messages
select * from outgoing_intrfc_e where A_INTRFC_EVENT_TY= 'HIST'
  and A_INSTRUMENT in (
    select UOID from instrument where instrument_id in ('LC2024-001','GUA2024-042')
  );

INSERT INTO outgoing_intrfc_e ( UOID, DATE_BUSINESS, ... )
values (generate_uoid(), ...,
  '|instrument_uoid =...|instrument_class = documentary_lc|party_type = BUYER|...',
  ...);

INSERT INTO outgoing_intrfc_e ( ... )
values (..., '|...instrument_class = guarantee|party_type = APPLICANT|...', ...);

commit;

select * from outgoing_intrfc_e where A_INTRFC_EVENT_TY= 'HIST' ...;
```

The `SELECT` block appears twice — before and after the inserts — so you can verify the queue state before committing and confirm the rows were written after.

---

## Supported Product Types

All 23 product codes are supported. `BIL` was added 2026-03-01.

| Code | Instrument Class |
|------|-----------------|
| `DLC` | `documentary_lc` |
| `SLC` | `standby_lc` |
| `CAR` | `cargo_release` |
| `RMB` | `reimbursement` |
| `DBA` | `documentary_ba_instrument` |
| `CBA` | `clean_ba_instrument` |
| `RBA` | `refinance_ba_instrument` |
| `DFP` | `deferred_payment_instrument` |
| `ADV` | `advance_instrument` |
| `LOI` | `letter_of_idemnity` |
| `DCO` | `documentary_collection_instrument` |
| `DIR` | `direct_send_collection_instrument` |
| `TAC` | `trade_accept_instrument` |
| `GUA` | `guarantee` |
| `PBD` | `participation_bought_documentary_lc` |
| `PBS` | `participation_bought_standby_lc` |
| `SBS` | `syndication_bought_documentary_lc` |
| `FIN` | `finance_instrument` |
| `ATP` | `approval_to_pay_instrument` |
| `OAP` | `open_account_payment` |
| `RPM` | `receivables_payables_management` |
| `SRM` | `selective_receivable_management` |
| `BIL` | `billing_instrument` |

> **Note:** The `LOI` class value contains the intentional typo `idemnity` (not `indemnity`).  
> This matches the target system's column value and must not be corrected.

---

## Development

### Setting Up

```bash
pip install -e ".[dev]"
```

This installs `pytest`, `pytest-cov`, `pytest-xdist`, `ruff`, and `reuse` in addition to the runtime dependency on `rich`.

### Running Tests

Always run from the **project root** (the directory containing `conftest.py` and `pyproject.toml`):

```bash
# Full suite with coverage
python -m pytest tests/

# Skip slow performance/benchmark tests
python -m pytest tests/ --ignore=tests/test_performance.py

# Run a specific test file
python -m pytest tests/test_regression.py

# Run only regression-pinned tests
python -m pytest tests/ -m regression

# Run with benchmark support (requires pytest-benchmark)
pip install pytest-benchmark
python -m pytest tests/test_performance.py
```

### Test Suite Overview

| File | What it covers |
|---|---|
| `test_product_class_resolver.py` | All 23 `ProductType` members, all 23 `InstrumentClass` members, the full mapping, `resolve_class()` for every code plus edge cases (whitespace, case, unknown) |
| `test_logging_decorators.py` | `@log_exceptions` happy path, all log levels, `raise_exception` true/false, subclass matching, all logger resolution modes, `__wrapped__` |
| `test_hist_messages_generator.py` | `InstrumentIndex`, `__init__`, all validation methods, `get_row_count`, `build_instruments_dictionary`, full `run()` SQL correctness, CLI `main()` |
| `test_version.py` | All three version-resolution branches (package metadata → git → `"dev"`) |
| `test_init.py` | All public API exports, `__all__` completeness |
| `test_integration.py` | End-to-end SQL output correctness, BIL regression, edge cases |
| `test_performance.py` | `resolve_class` latency, `build_instruments_dictionary` at 100/1000 rows, full `run()` at 100/1000 rows, `pytest-benchmark` variants |
| `test_regression.py` | 10 numbered, never-delete regression pins (REG-001 through REG-010) |
| `test_coverage_gaps.py` | Targeted tests for structurally hard-to-reach branches |

### Coverage

```bash
python -m pytest tests/ --cov=hist_message_generator --cov-report=term-missing
```

Current coverage: **96%**. The remaining 4% is structurally unreachable:

- `__init__.py` fail-safe `except` block — only reachable if the package is partially installed/broken
- `if __name__ == "__main__"` guard — only executes when Python runs the file directly via the OS shell, not importable by the test runner

### Linting

```bash
ruff check src/ tests/
```

---

## Architecture

```
CLI (hist-gen)
    │
    └── HISTMessagesGenerator.run()
            │
            ├── validate_xml_structure()       # ET.parse — raises on bad XML
            ├── validate_columns_exist()       # streaming iterparse — raises on missing cols
            ├── get_row_count()                # streaming iterparse
            ├── build_instruments_dictionary() # parse + resolve_class() per row
            │       └── resolve_class()        # ProductType → InstrumentClass
            └── write sql_statements.sql
```

**Key design decisions:**

- `validate_columns_exist` and `get_row_count` use `ET.iterparse` (streaming) so they don't hold the entire document in memory — safe for large exports.
- `build_instruments_dictionary` deduplicates by `INSTRUMENT_ID`; the first-seen row always wins, and a warning is logged for every ignored duplicate.
- `@log_exceptions` wraps the three main methods. It is configured with `raise_exception=True`, so exceptions always propagate to the caller after being logged.
- `version.py` resolves the version via `importlib.metadata` first, then falls back to `git describe --tags`, then to the string `"dev"`.

---

## Known Quirks

**`@log_exceptions` with a `lambda` logger** — The decorator's logger resolution only handles `str` attribute names. When `logger=lambda self: ...` is passed (as in the current source), the lambda itself is stored as `_logger` rather than being called. This means that when an exception occurs inside `run()`, `get_row_count()`, or `validate_xml_structure()`, the decorator raises an `AttributeError` (the lambda has no `.warning` method) before the original exception can be logged. The original exception is still the root cause and `raise_exception=True` means it propagates correctly — but the log message is lost. Tests account for this by catching `(OriginalException, AttributeError)`.

---

## License

MIT — see [SPDX headers](https://spdx.org/licenses/MIT.html) in each source file.

```
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2026 Laurent Morissette
```