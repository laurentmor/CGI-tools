# Changelog

All notable changes to this project will be documented in this file.

## [Released]

### Added Features

- Extraction of XML elements and saving them in individual files.
- Creation of a ZIP archive from the extracted files.
- Password protection for ZIP archives using `pyzipper`.
- Support for a customizable XML tag to name the files (default: `id`).
- Addition of sounds at the beginning and end of execution (Windows only, via `winsound`).
- Added a test mode to work with test sets.
- XML content cleaning with a customizable replacement map.
- Advanced validation of command-line arguments.
- Display of progress percentage during file processing.
- Confirmation before deleting the existing output directory.
- Validity checks for:
  - The input XML file
  - The output directory
  - The specified XML tag
  - The column name to extract
  - The ZIP password (minimum 5 characters)
  - The ZIP file name
  - The test file and its format
- Option to disable sound effects (`--mute`).
- Option to skip the final pause (`--skip-pause`).
- Can now generate test sets automatically if the specified test set size does not exist
- Simplified CLI arguments

### Bug Fixes

- Fixed the use of an undefined variable in error handling.
- Fixed ZIP encoding and encryption with `pyzipper`.
- Improved memory management using `iterparse` and explicit cleaning of XML elements.
- Resolved a bug where the file name wasn't extracted correctly from actual XML – switched to extraction via regex.

### Improvements

- Optimized file processing and XML parsing performance.
- Complete refactoring to improve code readability and maintainability.
- Converted `print` statements to logging via `logging`.
- Added `docstrings`, explanatory comments, and types to improve code documentation and understanding.
- Added support for loading a JSON file for the unwanted character replacement map.
- Enhanced robustness when reading and writing files.

---

### Author

This script is developed by **Laurent Morissette**.
