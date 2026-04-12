# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Documentation

- Added richer module-, class-, and method-level documentation to the XMLExtractor test suite.
- Improved test maintainability by documenting every XMLExtractor unit test with narrative comments.
- Expanded the changelog to explicitly capture recent documentation and quality improvements.
- Verified the updated XMLExtractor test suite compiles cleanly after documentation changes.

### Improvements

- Normalized path handling throughout the codebase using `pathlib.Path` for consistency and cross-platform compatibility.
- Fixed `test_mode` comparison logic to use boolean flags instead of string comparison (`"Y"`).
- Precompiled XML replacement regex patterns to avoid recompilation on every line during file cleaning.
- Implemented streaming I/O for file cleaning to minimize memory overhead when processing large XML files.

### Bug Fixes

- Fixed path resolution for PyInstaller-packaged executables by introducing a `get_base_path()` function that correctly determines the base path in both development and frozen contexts.
- Restored test suite compatibility after code quality improvements by updating mock signatures to match the modified `clean_xml_content()` function signature.
- Fixed file operation mocking in tests by changing from `Path().open()` to `open()` for better testability.
- Corrected main block pause logic in tests to properly trigger user input when expected.

### Testing

- All 112 unit tests now pass with 94.40% code coverage.
- Verified comprehensive test suite functionality after implementing path normalization, regex precompilation, and streaming I/O improvements.

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
