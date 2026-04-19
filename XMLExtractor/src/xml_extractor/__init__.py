# Re-export everything tests touch via `import xml_extractor as xe`
# Functions and module-level variables
# Re-export the internal modules that tests patch via patch("xml_extractor.<mod>.<attr>")
# pyzipper is imported at the top of xml_extractor.py; re-export so tests can
# patch "xml_extractor.pyzipper.AESZipFile"
from .xml_extractor import (
    DEFAULT_COLUMN_NAME,
    DEFAULT_FILE_ID_TAG,
    DEFAULT_OUTPUT_DIR,
    ET,  # xml.etree.ElementTree — patched as xml_extractor.ET.parse / .iterparse
    LOG_FILE_NAME,
    MIN_PASSWORD_LENGTH,
    SOUND_DONE,
    SOUND_ERROR,
    SOUND_START,
    WINSOUND_AVAILABLE,
    Path,  # patched as xml_extractor.Path.exists
    XMLExtractor,
    clean_xml_content,
    configure_logging,
    load_replace_map_from_json,
    logger,
    main,
    os,  # patched as xml_extractor.os.path.exists / .remove / .walk / .replace
    play_sound,
    process_input_file_to_ensure_is_clean,
    pyzipper,  # type: ignore
    re,  # accessed via xe.re
    replace_map,
    shutil,  # patched as xml_extractor.shutil.rmtree / .copy2
    sys,  # patched as xml_extractor.sys
    time,  # patched as xml_extractor.time
    validate_arguments,
    validate_column_exists,
    validate_xml_structure,
    validate_zip_password,
)

# winsound may be a stub from conftest; re-export so tests can patch
# "xml_extractor.winsound"
try:
    from .xml_extractor import winsound  # type: ignore
except ImportError:
    import sys as _sys
    import types as _types
    if "winsound" in _sys.modules:
        winsound = _sys.modules["winsound"]
    else:
        winsound = _types.ModuleType("winsound")

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