<!-- SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette -->

# HISTMessagesGenerator

A Python tool for generating historical message files from SQL export data.

## What it does

- Parses SQL Developer export files containing XML payloads.
- Extracts message content and converts it into generated historical message files.
- Resolves product class metadata using `ProductClassResolver.py`.
- Includes a sample generation test script and supporting SQL inputs.

## Contents

- `HISTMessagesGenerator.py` — main script for generating message outputs
- `ProductClassResolver.py` — resolves product class mappings
- `logging_decorators.py` — shared decorators used by the project
- `export.xml` — sample XML export file for input testing
- `test_hist_messages_generator.py` — sample unit test coverage
- `HISTMessagesGenerator.log` — example log output from execution

## Usage

Run the generator with Python:

```bash
cd HISTMessagesGenerator
python HISTMessagesGenerator.py
```

## Notes

- The repository includes several SQL input files covering multiple country formats.
- Use `ProductClassResolver.py` to understand how product-class decisions are made.
- The tool is intended for offline file-based generation, not a web service.
