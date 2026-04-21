# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

# __init__.py
#
# Re-exports every public symbol from the submodule so that
#   import xml_extractor as xe; xe.clean_xml_content(...)
# works for tests and library consumers.
#
# RuntimeWarning guard
# --------------------
# When Python runs `python -m xml_extractor.xml_extractor`, runpy calls
# __import__("xml_extractor") which executes this file BEFORE running the
# submodule.  At that point sys.argv[0] has already been set to the full
# path of xml_extractor.py (by runpy._get_module_details → alter_argv).
#
# If __init__.py then does `from .xml_extractor import ...`, it loads the
# submodule into sys.modules.  runpy detects the collision and fires:
#   RuntimeWarning: 'xml_extractor.xml_extractor' found in sys.modules ...
#
# Fix: check sys.argv[0] before importing.  When the script is being run
# directly, argv[0] will be the path to xml_extractor.py — skip the import.

import pathlib as _pl
import sys as _sys

_argv0_stem = _pl.Path(_sys.argv[0]).stem if _sys.argv else ""
_is_script = _argv0_stem == "xml_extractor"

if not _is_script:
    from .xml_extractor import (
        # DEFAULT_COLUMN_NAME,
        # DEFAULT_FILE_ID_TAG,
        # DEFAULT_OUTPUT_DIR,
        # Internal modules tests patch via patch("xml_extractor.<mod>.<attr>")
        ET,
        # LOG_FILE_NAME,
        # MIN_PASSWORD_LENGTH,
        # SOUND_DONE,
        # SOUND_ERROR,
        # SOUND_START,
        WINSOUND_AVAILABLE,
        Path,
        XMLExtractor,
        clean_xml_content,
        configure_logging,
        load_replace_map_from_json,
        logger,
        main,
        os,
        play_sound,
        process_input_file_to_ensure_is_clean,
        pyzipper,  # type: ignore
        re,
        replace_map,
        shutil,
        sys,
        time,
        validate_arguments,
        validate_column_exists,
        validate_xml_structure,
        validate_zip_password,
    )

    try:
        from .xml_extractor import winsound  # type: ignore
    except ImportError:
        import types as _types

        winsound = _sys.modules.get("winsound") or _types.ModuleType("winsound")

    __all__ = [
        "XMLExtractor",
        "clean_xml_content",
        "configure_logging",
        "load_replace_map_from_json",
        "main",
        "play_sound",
        "process_input_file_to_ensure_is_clean",
        "validate_arguments",
        "validate_column_exists",
        "validate_xml_structure",
        "validate_zip_password",
        "logger",
        "replace_map",
        "WINSOUND_AVAILABLE",
        "ET",
        "os",
        "shutil",
        "sys",
        "time",
        "Path",
        "re",
        "pyzipper",
        "winsound",
    ]
