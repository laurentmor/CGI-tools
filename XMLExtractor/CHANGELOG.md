# Changelog

All notable changes to this project will be documented in this file.

---

## 2026-04-12 — Fix decorator, test infrastructure, and validation error handling

### logging_decorators.py
- Changed defaults to `raise_exception=False` and `log_level="warning"` to match expected swallow-and-log behaviour
- Added `wrapper.__wrapped__ = func` to expose the original function for testing
- Fixed logger resolution — if `logger` is a string, resolve it as an attribute on `self` at call time (enables `logger="logger"` on instance methods)

### xml_extractor.py
- Removed `@log_exceptions` from `load_replace_map_from_json` — exception handling moved to `main()` as an explicit `try/except` with a default fallback map, making the recovery logic visible to readers
- Fixed `validate_arguments` — `validate_xml_structure` raises on failure rather than returning `False`, so the validate block now uses `try/except (ET.ParseError, FileNotFoundError)` instead of checking the return value
- Added `_INVALID_XML_CHARS` compiled regex at module level to replace the slow character-by-character `ord()` loop in `clean_xml_content`

### Tests
- `test_load_replace_map_from_json` — removed decorator re-wrapping machinery (`setUp`, `importlib.reload`, `__wrapped__`); tests now call `xe.load_replace_map_from_json` directly and assert exceptions raise instead of returning `None`
- `test_validate_xml_false` — updated to use `side_effect=ET.ParseError` instead of `return_value=False`
- `test_get_row_count` — removed `patch_iterparse`; tests now pass XML strings directly as `input_file` via `make_extractor(input_file=...)`

---

## 2026-04-12 — Code quality improvements and fix double XML parse

### Cross-platform & imports
- Guarded `winsound` import with `try/except` — script no longer crashes on Linux/macOS
- Removed unused `from functools import wraps`

### Reliability
- Fixed `@log_exceptions` decorator receiving `logger=None` at decoration time (logger was not yet initialized)
- Fixed `validate_xml_structure` — removed unreachable `else False` branch, added type hint
- Fixed `validate_zip_password` — return type changed to `None`; raises on failure instead of returning `False`
- Removed `== True` / `== False` anti-patterns in `validate_arguments`
- Removed commented-out dead code

### Testability
- Removed `input()` prompts from `XMLExtractor.check_output_dir` — overwrite decision now made in `main()` and passed in as `force_overwrite` parameter
- Updated tests to pass XML strings directly as `input_file` instead of using `patch_iterparse`

### Performance
- Replaced double XML parse with a single-pass text scan in `get_row_count` — O(n) I/O, no XML overhead
- Inline XML string input handled via `.count("<ROW>")`, no file I/O at all
- Fixed `ZeroDivisionError` in progress calculation when `row_count` is zero

### Robustness
- `running_in_test_runner_context()` now reads `XML_EXTRACTOR_TEST_MODE` environment variable instead of checking `os.getcwd()`

### Housekeeping
- Moved inline changelog block to `CHANGELOG.md`
- Fixed inconsistent indentation in `create_unprotected_zip`
- Collapsed excessive blank lines throughout

---

## [Earlier] — Documentation, type hints, and streaming I/O

### Documentation
- Added module-, class-, and method-level docstrings to the XMLExtractor test suite
- Updated README to reflect type annotation and regex caching improvements

### Improvements
- Normalized path handling throughout using `pathlib.Path`
- Added static type hints to `xml_extractor.py` signatures
- Fixed `test_mode` comparison logic to use boolean flags instead of string `"Y"` comparison
- Cached precompiled XML replacement regex to avoid recompiling on every clean pass
- Implemented streaming I/O for file cleaning to reduce memory overhead on large inputs