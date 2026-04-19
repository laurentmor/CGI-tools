# CGI Tools Repository

A collection of Python utilities and support packages for XML extraction, SQL export processing, accounting data updates.

## Repository Overview

This repository contains multiple standalone toolsets:

- `XMLExtractor/`
  - A complete XML extraction tool for SQL Developer export files.
  - Supports XML cleaning, validation, output file generation, optional ZIP creation, password-protected archives, and test-mode execution.
  - Includes a full pytest suite under `XMLExtractor/tests/`.

- `AccountingEntryClassUpdater/`
  - A small utility for updating accounting entry classes from SQL export data.
  - Includes supporting decorators and sample export files.

- `HISTMessagesGenerator/`
  - A script for generating historical message files from SQL exports.
  - Includes SQL input files, product-class resolution logic, and test coverage.

## Key Project Details

### XMLExtractor (tool version 1.3)

This is the most feature-rich project in the repo.

- `xml_extractor.py` — main extraction script
- `README.md` — full usage details for the XML extractor
- `requirements.txt` — Python dependencies for the XML extractor
- `tests/` — pytest-based coverage for extraction, cleaning, validation, zip handling, and CLI behavior
- `install-deps.bat` — helper script to install dependencies on Windows

#### Quick start

```bash
cd XMLExtractor
install-deps.bat
python xml_extractor.py <input_file> <output_dir> [options]
```

#### Run tests

```bash
cd XMLExtractor
pytest
```

### AccountingEntryClassUpdater

A utility to process accounting export data and update entry classes.

```bash
cd AccountingEntryClassUpdater
python AccountingEntryClassUpdater.py
```

### HISTMessagesGenerator

A utility to generate historical messages from SQL export files.

```bash
cd HISTMessagesGenerator
python HISTMessagesGenerator.py
```

### SanityCode

Contains automated web checks and output report generation.

```bash
cd SanityCode
python automation_web.py
```

### Middleware_Checklist_App_Package

Provides Windows setup support scripts and app packaging assets.

```bash
cd Middleware_Checklist_App_Package
Click_Here_To_Set_Up_Shortcut.bat
```

## Notes

- Most of the utilities are standalone and do not require a central package installation.
- Use the project-level `requirements.txt` files where available.
- The XMLExtractor project includes detailed documentation and tests in its own directory.

## Author

Laurent Morissette

---

> This repository is designed to keep several related tools together, making it easier to run SQL/XML transformation utilities, automation helpers, and deployment support from a single workspace.
