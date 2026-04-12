
# XML Extractor from SQL Developer Export

This Python tool extracts, cleans, validates, and exports XML content from SQL Developer export files. It now uses `xml_extractor.py` as the primary script entry point and supports advanced capabilities like ZIP compression, password protection, logging, test mode, and invalid XML character replacement.

## Features

- ✅ Extracts XML content from a specified column in an SQL Developer export.
- 🔒 Optionally compresses extracted files into a password-protected ZIP archive.
- 🧼 Cleans invalid XML characters and optionally applies a user-defined replacement map.
- 🔁 Supports test mode to process predefined test sets and auto-generate missing sets.
- 🧪 Validates XML structure and ensures the required column and tag exist.
- 📁 Organizes extracted XML files in a user-specified output directory.
- 🔉 Plays sound effects at script start/end (Windows only; can be muted).
- 📋 Logs execution to a file (`script.log` or `script-test.log`).
- 🧰 Built-in argument validation and error handling.
- 📈 Displays progress for each processed item.
- 🔁 Optional pause at the end (can be skipped).
- 🧪 Dry-run mode to simulate execution without writing files.
- 🧪 Improved test coverage and documentation for the XMLExtractor suite (94.40% coverage across 112 tests).

## Bug Fixes & Performance Improvements

- Fixed ZIP encryption and encoding issues when creating protected archives with `pyzipper`.
- Corrected XML file name extraction logic to reliably derive output names from XML content.
- Resolved an undefined variable error in the script's error handling path.
- Improved memory usage and parsing stability by fully cleaning `iterparse` XML elements.
- Fixed path resolution issues when the tool is packaged as an executable with PyInstaller.
- Optimized file cleaning with streaming I/O to reduce memory footprint for large XML files.
- Normalized path handling across all file operations using `pathlib.Path`.
- Precompiled regex patterns for character replacement to improve performance during XML cleaning.
- Updated test mocks to maintain compatibility with code improvements, ensuring all 112 tests pass.

## Requirements

- Python 3.7+
- Required packages:
  - `pyzipper`

## Installation

1. Clone the repository.
2. Install dependencies:

   ```bash
   install-deps.bat
   ```

## Usage

```bash
python xml_extractor.py <input_file> <output_dir> [options]
```

### Positional Arguments

- `input_file`: Path to the input XML file (required unless in test mode).
- `output_dir`: Directory where XML files will be saved (default: `xmls`).

### Options

| Option | Description |
|--------|-------------|
| `--column-name` | Name of the column containing XML (default: `RICH_TEXT_NCLOB`) |
| `--file-id-tag` | Tag used to name output files (default: `MessageID`) |
| `--z <zip_name> <zip_password>` | Create a ZIP file with optional password |
| `--mute` | Mute sound effects |
| `--skip-pause` | Skip pause at the end of script |
| `--test [N]` | Run in test mode with optional test set size (default: 10) |
| `--validate` | Validate XML structure only |
| `--dry-run` | Simulate script execution without writing files |
| `--version` | Show script version info |

### Examples

Extract XML content into `xmls/` directory:

```bash
python xml_extractor.py export.xml xmls/
```

Create a password-protected ZIP file:

```bash
python xml_extractor.py export.xml xmls/ --z result.zip mypassword
```

Run in test mode with 5 mock entries:

```bash
python xml_extractor.py --test 5
```

Validate XML structure only:

```bash
python xml_extractor.py export.xml --validate
```

## Logging

Execution logs are saved to:

- `script.log` for normal runs
- `script-test.log` for test mode

If an error occurs, it will also be shown in Notepad (on Windows).

## Changelog Summary

- Password-protected ZIP creation
- XML cleaning and validation
- CLI validation and help prompts
- Logging, dry-run mode, and progress display
- Improved performance and memory management
- Automatic test set generation
- Updated test suite documentation and narrative comments
- Resolved ZIP encoding and XML naming bug fixes

## Author

**Laurent Morissette**
Version: `1.3`

---

> _"This script was built for real-world XML extraction from complex SQL Developer exports with robustness and flexibility in mind."_
