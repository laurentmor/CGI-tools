
# XML Extractor from SQL Developer Export

This Python script is designed to extract, clean, and validate XML content from SQL Developer export files. It supports advanced features like ZIP compression with password protection, logging, test mode, and data cleaning for invalid XML characters.

## Features

- ✅ Extracts XML content from a specified column in an SQL Developer export.
- 🔒 Optionally compresses extracted files into a password-protected ZIP archive.
- 🧼 Cleans invalid XML characters and optionally applies a user-defined replacement map.
- 🔁 Supports test mode to process predefined test sets.
- 🧪 Validates XML structure and ensures the required column and tag exist.
- 📁 Organizes extracted XML files in a user-specified output directory.
- 🔉 Plays sound effects at script start/end (Windows only; can be muted).
- 📋 Logs execution to a file (`script.log` or `script-test.log`).
- 🧰 Built-in argument validation and error handling.
- 📈 Displays progress for each processed item.
- 🔁 Optional pause at the end (can be skipped).
- 🧪 Dry-run mode to simulate execution without performing actual writes.

## Requirements

- Python 3.7+
- Required packages:
  - `pyzipper`

## Installation

1. Clone the repository or copy the script.
2. Install dependencies:

   ```bash
   install-deps.bat
   ```

## Usage

```bash
python script.py <input_file> <output_dir> [options]
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
python script.py export.xml xmls/
```

Create a password-protected ZIP file:

```bash

python script.py export.xml xmls/ --z result.zip mypassword
```

Run in test mode with 5 mock entries:

```bash
python script.py --test 5
```

Validate XML structure only:

```bash
python script.py export.xml --validate
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

## Author

**Laurent Morissette**
Version: `1.2`

---

> _"This script was built for real-world XML extraction from complex SQL Developer exports with robustness and flexibility in mind."_
