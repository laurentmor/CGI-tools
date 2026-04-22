# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
XMLExtractor Module

This module provides functionality to extract XML data from database export files
and save individual XML documents as separate files. It supports optional ZIP
compression with password protection, test mode for development, and various
validation and cleaning operations.

See README.md for instructions and documentation.
See CHANGELOG.md for version history and changes.
Version 1.3 - 2026-04-12

Key Features:
- Extracts XML content from specified columns in SQL export files
- Cleans invalid XML characters using configurable replacement maps
- Generates unique filenames based on XML content tags
- Creates ZIP archives with optional AES encryption
- Provides comprehensive logging and error handling
- Supports dry-run mode for testing
- Includes test mode with generated test data
- Plays sound effects for user feedback (Windows only)

Usage:
    Run as a script with command-line arguments, or import classes/functions
    for programmatic use in other applications.
"""

import argparse
import os
import shutil
import sys
import time

# DEBUG# import traceback
import zipfile
from importlib.resources import files

import pyzipper  # type: ignore

try:
    import winsound

    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional, Pattern
from xml.etree import ElementTree as ET

from .logging_decorators import log_exceptions
from .version import __version__

##

# ---------------------------------------------------------------------------
# Constants and defaults configuration
# ---------------------------------------------------------------------------
DEFAULT_COLUMN_NAME = "RICH_TEXT_NCLOB"
DEFAULT_FILE_ID_TAG = "MessageID"
DEFAULT_OUTPUT_DIR = "xmls"
DEFAULT_TEST_SIZE = 10
MIN_PASSWORD_LENGTH = 5
SOUND_START = "homer_start.wav"
SOUND_DONE = "homer_done.wav"
SOUND_ERROR = "homer_error.wav"
LOG_FILE_NAME = "script.log"
LOG_FILE_TEST_NAME = "script-test.log"
REPLACEMENT_MAP_FILE = "replacements.json"

# ---------------------------------------------------------------------------
# Global variables
# ---------------------------------------------------------------------------
# logger: Configured logging instance for outputting messages to console and file.
# Initialised to a no-op stub so module-level decorators that capture it at
# decoration time always have a valid object; main() replaces it with the real
# configured logger before any user-visible work begins.
logger: logging.Logger = logging.getLogger(__name__)

# replace_map: Dictionary containing character replacements for cleaning XML
# content, loaded from JSON at startup.
replace_map: Optional[Dict[str, str]] = None

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def configure_logging() -> logging.Logger:
    """Configure the logger for the script with console and file handlers.

    Sets up logging to output messages to both the console and a log file.
    Uses a custom formatter for consistent log message formatting.

    Returns:
        logging.Logger: The configured logger instance ready for use.
    """
    _logger = logging.getLogger(__name__)
    if not _logger.handlers:  # Prevent duplicate handlers if called multiple times
        formatter = logging.Formatter(
            "{asctime} - {levelname} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
        )
        _logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)

        # File handler
        out_file_handler = logging.FileHandler(LOG_FILE_NAME, mode="a", encoding="utf-8")
        out_file_handler.setFormatter(formatter)
        out_file_handler.setLevel(logging.INFO)
        _logger.addHandler(out_file_handler)

    return _logger


# ---------------------------------------------------------------------------
# Sound
# ---------------------------------------------------------------------------


def play_sound(sound_file: str, mute: bool) -> None:
    """Play a sound effect if not muted and the sound file exists.

    Plays WAV sound files located in the 'sounds' directory using Windows'
    winsound module.  Used for user feedback during script execution
    (start, done, error sounds).

    Args:
        sound_file (str): Name of the sound file (e.g., 'homer_start.wav').
        mute (bool): If True, sound playback is disabled.
    """
    if mute or not WINSOUND_AVAILABLE:
        return
    sound_path = files("xml_extractor.sounds") /sound_file

    if sound_path.exists():
        winsound.PlaySound(str(sound_path.resolve()), winsound.SND_FILENAME)


# ---------------------------------------------------------------------------
# Replacement map
# ---------------------------------------------------------------------------


def load_replace_map_from_json(json_path: str) -> Dict[str, Any]:
    """Load a replacement map from a JSON file for XML content cleaning.

    Reads a JSON file containing key-value pairs for character replacements.
    If the file is not found or is invalid JSON, logs a warning and returns
    a safe built-in default map.

    Args:
        json_path (str): Path to the JSON file containing the replacement map.

    Returns:
        dict: Dictionary with replacement mappings.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load replacement map: {e} - using default map.")
    return {"*": "-", "\x02": "", "\x1a": ""}


# ---------------------------------------------------------------------------
# XML validation
# ---------------------------------------------------------------------------


@log_exceptions(
    {FileNotFoundError: "XML file not found", ET.ParseError: "XML parsing failed"},
    log_level="warning",
    raise_exception=True,
    logger=logger,
)
def validate_xml_structure(input_file: str) -> bool:
    """Validate the XML structure of the input file.

    Attempts to parse the XML file using ElementTree.  If parsing succeeds
    the XML is considered well-formed.

    Args:
        input_file (str): Path to the XML file to validate.

    Returns:
        bool: True if XML is valid (parsing succeeds), raises exception otherwise.

    Raises:
        ET.ParseError: If the XML is malformed.
        FileNotFoundError: If the input file does not exist.
    """
    ET.parse(input_file)
    return True


# ---------------------------------------------------------------------------
# Argument handling
# ---------------------------------------------------------------------------


def validate_arguments() -> argparse.Namespace:
    """Validate command-line arguments and return them after processing.

    Sets up an ArgumentParser with all possible command-line options,
    parses and validates them, and handles special cases such as
    validation-only runs and ZIP password checks.

    Returns:
        argparse.Namespace: Parsed and validated command-line arguments.

    Raises:
        SystemExit: If arguments are invalid or required files are missing.
    """
    logger.info("Validating CLI arguments")
    parser = argparse.ArgumentParser(description="Generate XML files based on SQLDEV export.")
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Input XML file (optional if --test is used)",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        help=f"Output directory for XML files (optional) (default: {DEFAULT_OUTPUT_DIR})",
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--column-name",
        default=DEFAULT_COLUMN_NAME,
        help=f"Column name to extract XML from (default {DEFAULT_COLUMN_NAME})",
    )
    parser.add_argument(
        "--z",
        nargs="+",
        metavar=("zip_name", "[zip_password]"),
        help="Create a zip file. Optionally provide a password.",
    )
    parser.add_argument(
        "--file-id-tag",
        default=DEFAULT_FILE_ID_TAG,
        help=f"XML tag to use as the file name (default: '{DEFAULT_FILE_ID_TAG}')",
    )
    parser.add_argument(
        "--skip-pause",
        action="store_true",
        default=False,
        help="Skip pause at the end of execution",
    )
    parser.add_argument(
        "--mute",
        action="store_true",
        help="Mute sound effects during execution",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate script execution",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate XML structure only",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__} by Laurent Morissette - Generate XML files based on SQLDEV export.",
        help="Show version information",
    )

    args = parser.parse_args()

    # Show help and exit when no arguments are provided
    if len(sys.argv) == 1:
        logger.info("No arguments provided. Showing help message.")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Ensure a valid input file is supplied
    if args.input_file is None or not Path(args.input_file).exists():
        parser.print_help(sys.stderr)

        raise FileNotFoundError(
            f"Error: an existing input file is required. File '{args.input_file}' does not exist."
        )

    # If validation only is requested, validate XML and exit
    if args.validate:
        try:
            validate_xml_structure(args.input_file)
            logger.info("XML structure is valid.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"XML structure validation failed: {e}")
            sys.exit(1)

    # Validate ZIP password when ZIP creation with a password is requested.
    # validate_zip_password raises ValueError on failure; let it propagate.
    if args.z and len(args.z) > 1:
        validate_zip_password(args.z[1])

    logger.info("Arguments validated successfully.")
    return args


def validate_zip_password(password: Optional[str]) -> bool:
    """Validate the ZIP password length for security.

    Ensures the password is at least MIN_PASSWORD_LENGTH characters long.

    Args:
        password (str | None): The password string to validate.

    Returns:
        bool: True if the password is valid.

    Raises:
        ValueError: If the password is None or shorter than the minimum length.
    """
    if password is None:
        logger.error("Password is required for ZIP encryption.")
        raise ValueError("Password is required for ZIP encryption.")
    if len(password) < MIN_PASSWORD_LENGTH:
        logger.error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    return True


# ---------------------------------------------------------------------------
# XML cleaning
# ---------------------------------------------------------------------------


def process_input_file_to_ensure_is_clean(input_file: str) -> None:
    """Clean the input XML file to ensure it contains only valid XML characters.

    Reads the input file line by line, applies character replacements using
    the global replace_map, and strips invalid XML characters.  A backup is
    created and the original overwritten *only* when cleaning is actually
    required, avoiding unnecessary filesystem writes on clean inputs.

    Args:
        input_file (str): Path to the XML file to clean.
    """
    input_path = Path(input_file)
    backup = input_path.with_suffix(input_path.suffix + ".bak")
    temp = input_path.with_suffix(input_path.suffix + ".tmp")
    cleaned = False
    cleaned_lines = []

    # Pre-compile replacement regex once for efficiency
    replace_regex = None
    if replace_map:
        replace_regex = re.compile("|".join(map(re.escape, replace_map)))

    with open(str(input_path), "r", encoding="utf-8", errors="ignore") as fin:
        for line in fin:
            clean_line = clean_xml_content(line, replace_map, replace_regex)
            if clean_line != line:
                cleaned = True
            cleaned_lines.append(clean_line)

    if cleaned:
        # Only create a backup when the file actually needs to be modified
        shutil.copy2(str(input_path), str(backup))
        logger.info(f"Backup created: {backup}")
        with open(str(temp), "w", encoding="utf-8") as fout:
            fout.writelines(cleaned_lines)
        logger.info("Cleaning done. Continuing...")
        os.replace(str(temp), str(input_path))
    else:
        logger.info("No illegal characters found. No replacement done.")
        if os.path.exists(str(temp)):
            os.remove(str(temp))


def clean_xml_content(
    content: Optional[str],
    replace_map: Optional[Dict[str, str]],
    replace_regex: Optional[Pattern] = None,
) -> Optional[str]:
    """Clean XML content by removing invalid characters and applying replacements.

    Performs two cleaning operations:
    1. Removes characters that are invalid in XML (keeps tab/9, LF/10, CR/13,
       and all characters with ordinal >= 32).
    2. Applies custom replacements from the replace_map dictionary via regex.

    The caller is responsible for pre-compiling and passing replace_regex for
    efficiency in tight loops.  If replace_regex is omitted and replace_map is
    provided, the regex is compiled on the fly (no module-level cache is used).

    Args:
        content (str | None): The XML content string to clean.
        replace_map (dict | None): Character replacement dictionary
            (e.g., ``{'*': '-', '\\x02': ''}``).
        replace_regex (Pattern | None): Pre-compiled regex for replace_map.
            Compiled from replace_map when not provided.

    Returns:
        str | None: The cleaned XML content string, or None/empty if input is
        falsy.
    """
    if not content:
        return content

    # Remove all invalid XML characters
    # Valid XML chars: tab (9), LF (10), CR (13), and any char with ord >= 32
    content = "".join(ch for ch in content if ord(ch) in (9, 10, 13) or ord(ch) >= 32)

    # Apply the replace_map when present
    if replace_map:
        if replace_regex is None:
            replace_regex = re.compile("|".join(map(re.escape, replace_map)))
        content = replace_regex.sub(lambda m: replace_map[m.group(0)], content)

    return content


# ---------------------------------------------------------------------------
# Column validation
# ---------------------------------------------------------------------------


@log_exceptions(
    {Exception: "Error validating column existence"},
    log_level="error",
    raise_exception=True,
    logger=logger,
)
def validate_column_exists(input_file: str, column_name: str) -> bool:
    """Validate that the specified column exists in the XML file.

    Parses the XML file (or XML string) and checks for a <COLUMN> element
    with a NAME attribute matching column_name.

    Args:
        input_file (str): Path to the XML file, or raw XML string content.
        column_name (str): Name of the column to check for.

    Returns:
        bool: True if the column is found.

    Raises:
        ValueError: If the column is not found or if parsing fails.
    """
    try:
        if input_file.strip().startswith("<"):
            root = ET.fromstring(input_file)
        else:
            if not os.path.exists(input_file):
                raise ValueError(f"File not found: {input_file}")
            tree = ET.parse(input_file)
            root = tree.getroot()

        for col in root.iter("COLUMN"):
            if col.attrib.get("NAME") == column_name:
                return True

        raise ValueError(f"Column '{column_name}' not found")

    except Exception as e:
        raise ValueError(f"Error validating column '{column_name}': {e}") from e


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def get_base_path() -> Path:
    """Return the base path, handling both development and PyInstaller contexts."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


# ---------------------------------------------------------------------------
# XMLExtractor
# ---------------------------------------------------------------------------


class XMLExtractor:
    """Extract XML elements from an input file and save them as separate files.

    Parses an XML export file, extracts the content of a named column from
    each <ROW> element, and writes each as an individual XML file.  Optionally
    compresses the output files into a ZIP archive with optional AES password
    protection.  Supports dry-run mode for testing without creating files.
    """

    def __init__(
        self,
        input_file: str,
        output_dir: str,
        *,
        output_file_name: Optional[str] = None,
        column_name: str = DEFAULT_COLUMN_NAME,
        create_zip: bool = False,
        zip_password: Optional[str] = None,
        file_id_tag: str = DEFAULT_FILE_ID_TAG,
        mute: bool = False,
        dry_run: bool = False,
    ) -> None:
        """Initialise XMLExtractor.

        Args:
            input_file (str): Path to the input XML file.
            output_dir (str): Directory to save the extracted XML files.
            output_file_name (str | None): Base name for the output ZIP file.
            column_name (str): Name of the column containing XML data to extract.
            create_zip (bool): Whether to create a ZIP archive of output files.
            zip_password (str | None): Password for ZIP encryption (if applicable).
            file_id_tag (str): XML tag name used to generate unique file names.
            mute (bool): If True, disables sound effects.
            dry_run (bool): If True, simulates operations without creating files.
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.output_file_name = output_file_name
        self.column_name = column_name
        self.create_zip = create_zip
        self.zip_password = zip_password
        self.file_id_tag = file_id_tag
        self.mute = mute
        self.dry_run = dry_run
        self.zip_filename: Optional[str] = None

    # ------------------------------------------------------------------
    # Directory management
    # ------------------------------------------------------------------

    @log_exceptions(
        {
            FileNotFoundError: "Output directory not found",
            Exception: "Error deleting output directory",
        },
        log_level="error",
        raise_exception=True,
        logger=logger,
    )
    def delete_output_dir(self) -> None:
        """Delete the output directory and all its contents recursively.

        Raises:
            FileNotFoundError: If the output directory does not exist.
            Exception: For other file-system errors during deletion.
        """
        shutil.rmtree(self.output_dir)
        logger.info(f"Deleted output directory: {self.output_dir}")

    def check_output_dir(self) -> None:
        """Check if the output directory exists and handle creation or deletion.

        If the path exists as a file, prompts to delete it.  If it exists as a
        directory, prompts to delete it before recreating.  In dry-run mode all
        file-system operations are skipped.
        """
        if self.dry_run:
            logger.info(
                f"[Dry-run] Output directory {self.output_dir} will not be created or deleted."
            )
            return

        if os.path.exists(self.output_dir):
            if os.path.isfile(self.output_dir):
                answer = (
                    input(
                        f"Output path '{self.output_dir}' exists as a file. "
                        "Do you want to delete it? (Y/N): "
                    )
                    .strip()
                    .upper()
                )
                if answer == "Y":
                    os.remove(self.output_dir)
                    os.makedirs(self.output_dir, exist_ok=True)
                    logger.info(f"Removed file and created output directory '{self.output_dir}'.")
                else:
                    logger.error(f"Output path '{self.output_dir}' is a file. Cannot proceed.")
                    raise ValueError(f"Output path '{self.output_dir}' is a file, not a directory.")
            else:
                answer = (
                    input(
                        f"Output directory '{self.output_dir}' already exists. "
                        "Do you want to delete it? (Y/N): "
                    )
                    .strip()
                    .upper()
                )
                if answer == "Y":
                    self.delete_output_dir()
                    os.makedirs(self.output_dir, exist_ok=True)
                    logger.info(f"Output directory '{self.output_dir}' recreated.")
                else:
                    logger.info(
                        f"Output directory '{self.output_dir}' already exists. "
                        "Content will be appended."
                    )
        else:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Output directory '{self.output_dir}' created.")

    # ------------------------------------------------------------------
    # ID extraction
    # ------------------------------------------------------------------

    def get_message_id(self, content: str) -> str:
        """Extract the message ID from XML content using regex.

        Searches for file_id_tag in the XML content and returns the text
        between the opening and closing tags.

        Args:
            content (str): The XML content string to search.

        Returns:
            str: The extracted message ID, or an empty string if not found.
        """
        match = re.search(rf"<{self.file_id_tag}>(.*?)</{self.file_id_tag}>", content)
        return match.group(1) if match else ""

    # ------------------------------------------------------------------
    # Row counting
    # ------------------------------------------------------------------

    @log_exceptions(
        {Exception: "Error counting <ROW> elements"},
        log_level="error",
        raise_exception=True,
        logger=logger,
    )
    def get_row_count(self) -> int:
        """Count the number of <ROW> elements in the input XML file.

        Uses line-by-line scanning to avoid loading the entire file into memory.
        Used for progress reporting during extraction.

        Returns:
            int: The total number of <ROW> elements found in the XML file.
        """
        logger.info(f"Counting <ROW> elements in: {self.input_file[:60]}")
        if self.input_file.strip().startswith("<"):  # For test mode with XML string input,
            # count occurrences directly without file I/O
            return self.input_file.count("<ROW>")
        # For file input, read line by line to count <ROW> occurrences without loading entire file
        # into memory
        with open(self.input_file, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for line in f if "<ROW>" in line)

    # ------------------------------------------------------------------
    # Main extraction
    # ------------------------------------------------------------------

    @log_exceptions(
        {
            FileNotFoundError: "Input file not found",
            ET.ParseError: "XML parsing error",
            ValueError: "Invalid XML structure or column name not found",
            IOError: "File handling or writing error",
        },
        log_level="error",
        raise_exception=True,
        logger=logger,
    )
    def extract_and_save_elements(self) -> None:
        """Extract XML elements from the input file and save them as separate files.

        Parses the XML file using iterative parsing for memory efficiency.
        For each <ROW> element, extracts the specified column's XML content,
        generates a filename from the message ID, and writes the content to a
        file.  Tracks progress and reports completion.  Optionally creates a
        ZIP archive.

        Raises:
            FileNotFoundError: If the input file does not exist.
            ET.ParseError: If the XML is malformed.
            ValueError: If the XML structure is invalid or the column is not found.
            IOError: For file-writing errors.
        """
        logger.info(f"Processing file: {self.input_file}")
        logger.info(f"Output directory: {self.output_dir}")
        self.check_output_dir()

        file_count = 0
        row_count = self.get_row_count()
        logger.info(f"Total <ROW> elements to process: {row_count}")

        context = ET.iterparse(self.input_file, events=("start", "end"))
        _, root = next(context)
        processed_rows = 0

        if root.tag != "RESULTS":
            raise ValueError("Root element is not <RESULTS>")

        for event, elem in context:
            if event == "end" and elem.tag == "ROW":
                logger.debug(f"Processing <ROW> element: {elem.tag}")
                rich_text = elem.find(f"COLUMN[@NAME='{self.column_name}']")
                if rich_text is not None and rich_text.text:
                    xml_id = self.get_message_id(rich_text.text).strip()
                    if xml_id:
                        file_name = f"{xml_id}.xml"
                        processed_rows += 1
                        if row_count:
                            progress_pct = (processed_rows / row_count) * 100
                            logger.info(
                                f"Processing {self.file_id_tag}: {xml_id} ({progress_pct:.2f}%)"
                            )
                        else:
                            logger.info(f"Processing {self.file_id_tag}: {xml_id}")
                        if not self.dry_run:
                            output_path = Path(self.output_dir) / file_name
                            with open(str(output_path), "w", encoding="utf-8") as output:
                                output.write(rich_text.text.strip())
                                file_count += 1
                                logger.info(f"File created: {file_name}")
                        else:
                            logger.info(f"Dry run: File would be created: {file_name}")

                elem.clear()

        root.clear()

        if self.create_zip:
            self.create_zip_archive()

        logger.info(f"Total files created: {file_count}")

    # ------------------------------------------------------------------
    # ZIP archive creation
    # ------------------------------------------------------------------

    @log_exceptions(
        {Exception: "Error creating unprotected zip file"},
        log_level="error",
        raise_exception=True,
        logger=logger,
    )
    def create_unprotected_zip(self, zip_filename: Optional[str] = None) -> None:
        """Create a plain ZIP archive without password protection.

        Uses standard ZIP compression to archive all files in the output
        directory.

        Args:
            zip_filename (str | None): Explicit ZIP filename.  Defaults to
                ``output_file_name + '.zip'``.

        Raises:
            Exception: For any errors during ZIP creation or file operations.
        """
        if not zip_filename:
            zip_filename = self.zip_filename or f"{self.output_file_name}.zip"
        full_zip_path = Path(self.output_dir).parent / zip_filename
        with zipfile.ZipFile(str(full_zip_path), "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    zipf.write(
                        str(file_path),
                        str(file_path.relative_to(self.output_dir)),
                    )
        logger.info(
            f"ZIP archive '{full_zip_path}' created successfully without password protection."
        )

    @log_exceptions(
        {Exception: "Error creating protected zip file"},
        log_level="error",
        raise_exception=True,
        logger=logger,  # was missing in the original
    )
    def create_protected_zip(self, zip_filename: Optional[str] = None) -> None:
        """Create a ZIP archive with AES encryption and password protection.

        Uses pyzipper to create a password-protected ZIP file.  All files in
        the output directory are added to the archive.

        Args:
            zip_filename (str | None): Explicit ZIP filename.  Defaults to
                ``output_file_name + '-protected.zip'``.

        Raises:
            Exception: For errors during ZIP creation or file operations.
        """
        if not zip_filename:
            zip_filename = self.zip_filename or f"{self.output_file_name}-protected.zip"
        full_zip_path = Path(self.output_dir).parent / zip_filename
        with pyzipper.AESZipFile(
            str(full_zip_path),
            "w",
            compression=zipfile.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES,
        ) as zipf:
            zipf.setpassword(self.zip_password.encode("utf-8"))
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    zipf.write(str(file_path), file)
        logger.info(f"Protected ZIP archive '{full_zip_path}' created successfully.")

    def create_zip_archive(self) -> None:
        """Create a ZIP archive of the extracted XML files.

        Determines whether to create a password-protected or unprotected ZIP
        based on the presence of a password.  Skips if dry-run is enabled.
        """
        if self.dry_run:
            logger.info(f"[Dry-run] No zip named {self.output_file_name} will be created.")
            return

        if self.zip_password:
            zip_filename = f"{self.output_file_name}-protected.zip"
            self.zip_filename = zip_filename
            self.create_protected_zip(zip_filename)
        else:
            zip_filename = f"{self.output_file_name}.zip"
            self.zip_filename = zip_filename
            self.create_unprotected_zip(zip_filename)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Main entry point for the script.

    Orchestrates the entire XML extraction process:
    - Configures logging
    - Validates arguments
    - Loads replacement map
    - Cleans input file
    - Validates column existence
    - Initialises and runs XMLExtractor
    - Handles sound effects and user interaction
    - Manages errors and cleanup
    """
    global logger, replace_map
    try:
        start_time = time.time()
        logger = configure_logging()
        args = validate_arguments()

        # validate_arguments already checks file existence; this is a safety net
        # for the case where main() is called programmatically without going
        # through validate_arguments.
        if not os.path.exists(args.input_file):
            raise FileNotFoundError(f"Input file '{args.input_file}' does not exist.")

        base_path = get_base_path()
        replace_map_path = base_path / REPLACEMENT_MAP_FILE
        replace_map = load_replace_map_from_json(replace_map_path)
        logger.info(f"Replacement map loaded: {replace_map}")

        process_input_file_to_ensure_is_clean(args.input_file)
        validate_column_exists(args.input_file, args.column_name)

        logger.info("Starting XMLExtractor script")
        play_sound(SOUND_START, args.mute)

        zip_password = args.z[1] if args.z and len(args.z) > 1 else None
        zip_name = args.z[0] if args.z else None

        extractor = XMLExtractor(
            args.input_file,
            args.output_dir,
            output_file_name=zip_name,
            column_name=args.column_name,
            create_zip=bool(args.z),
            zip_password=zip_password,
            file_id_tag=args.file_id_tag,
            mute=args.mute,
            dry_run=args.dry_run,
        )

        extractor.extract_and_save_elements()

        logger.info("Script completed successfully.")
        play_sound(SOUND_DONE, args.mute)
        logger.info(f"Total execution time: {time.time() - start_time:.2f} seconds")

        if not args.skip_pause:
            input("Press Enter to exit...")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error("Script execution failed.")
        # logger.exception("Stack trace for debugging:")
        # traceback.print_exc()
        play_sound(SOUND_ERROR, False)  # False = not muted; force the error sound
        sys.exit(1)


if __name__ == "__main__":
    main()
