# AccountingEntryClassUpdater

A small Python utility for updating accounting entry class information from SQL export-style files.

## What it does

- Reads SQL export data from `export.xml` or user-provided files.
- Applies accounting entry class updates based on the current script logic.
- Includes helper decorators and logging support.

## Contents

- `AccountingEntryClassUpdater.py` — main script entry point
- `decorators.py` — shared decorator utilities used by the script
- `export.xml` — sample SQL Developer export input
- `sql_statements.sql` — example SQL input used for processing
- `accounting_entry_updater.log` — sample runtime log output

## Usage

Run the main script with Python:

```bash
cd AccountingEntryClassUpdater
python AccountingEntryClassUpdater.py
```

## Notes

- This folder is designed as a self-contained tool for accounting entry class updates.
- Inspect the script and `decorators.py` for customization points and logging behavior.
