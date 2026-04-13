"""
See README.md for instructions and documentation.
See CHANGELOG.md for version history and changes.
Version 1.3 - 2026-04-12     
"""

"""
XMLExtractor Module

This module provides functionality to extract XML data from database export files
and save individual XML documents as separate files. It supports optional ZIP
compression with password protection, test mode for development, and various
validation and cleaning operations.

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

# Import necessary modules for the script's functionality
import os
import sys
import argparse
import time
import zipfile
import pyzipper # type: ignore
import shutil
# Replace the bare import
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False
import logging
import re
import json
from pathlib import Path
from typing import Any, Dict, Optional, Pattern
from xml.etree import ElementTree as ET
from tests.generate_test_sets import generate
from decorators import log_exceptions

# Constants
DEFAULT_COLUMN_NAME = "RICH_TEXT_NCLOB"
DEFAULT_FILE_ID_TAG = "MessageID"
DEFAULT_OUTPUT_DIR = "xmls"
DEFAULT_TEST_SIZE = 10
MIN_PASSWORD_LENGTH = 5
TEST_MODE_INDICATOR = "test"
SOUND_START = "homer_start.wav"
SOUND_DONE = "homer_done.wav"
SOUND_ERROR = "homer_error.wav"
LOG_FILE_NAME = "script.log"
LOG_FILE_TEST_NAME = "script-test.log"
REPLACEMENT_MAP_FILE = "replacements.json"
TEST_SET_PATH_TEMPLATE = "sets/set_{}.xml"
TEST_SET_PATH_TEST_TEMPLATE = "tests/sets/set_{}.xml"

# Global variables used throughout the script
# logger: Configured logging instance for outputting messages to console and file
logger = None
# replace_map: Dictionary containing character replacements for cleaning XML content, loaded from JSON
replace_map: Optional[Dict[str, str]] = None
# Cache the compiled regex for repeated cleanup calls when the replacement map is reused
replace_regex_cache: Optional[Pattern] = None
replace_map_cache: Optional[Dict[str, str]] = None
#script global methods

# Utility functions for script configuration and validation

def running_in_test_mode() -> bool:
    """Check if the script is running in a test directory context.

    This function determines if the current working directory contains 'test',
    which indicates the script is being run in a testing environment. This affects
    logging file names, test set paths, and other behaviors.

    Returns:
        bool: True if 'test' is in the current working directory path, False otherwise.
    """
    return TEST_MODE_INDICATOR in os.getcwd()

def configure_logging() -> logging.Logger:
    """Configures the logger for the script with console and file handlers.

    Sets up logging to output messages to both the console and a log file.
    The log file name depends on whether the script is in test mode.
    Uses a custom formatter for consistent log message formatting.

    Returns:
        logging.Logger: The configured logger instance ready for use.
    """
    logger = logging.getLogger(__name__)
    if not logger.handlers:  # Prevent duplicate handlers if called multiple times
        # Define a formatter with timestamp, log level, and message
        formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")
        logger.setLevel(logging.INFO)  # Set default log level to INFO

        # Console handler for outputting to terminal
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler; log file name changes based on test mode
        log_file_name = LOG_FILE_TEST_NAME if running_in_test_mode() else LOG_FILE_NAME
        out_file_handler = logging.FileHandler(log_file_name, mode="a", encoding="utf-8")
        out_file_handler.setFormatter(formatter)
        out_file_handler.setLevel(logging.INFO)
        logger.addHandler(out_file_handler)
    return logger

def play_sound(sound_file: str, mute: bool) -> None:
    """Play a sound effect if not muted and the sound file exists.

    This function plays WAV sound files located in the 'sounds' directory
    using Windows' winsound module. It's used for user feedback during
    script execution (start, done, error sounds).

    Args:
        sound_file (str): Name of the sound file (e.g., 'homer_start.wav').
        mute (bool): If True, sound playback is disabled.
    """
    sound_path = Path("sounds") / sound_file
    if mute is False and os.path.exists(str(sound_path)):
        if WINSOUND_AVAILABLE:
            winsound.PlaySound(str(sound_path.resolve()), winsound.SND_FILENAME)
    return

def load_replace_map_from_json(json_path: str) -> Optional[Dict[str, Any]]:
    """Load a replacement map from a JSON file for XML content cleaning.

    Reads a JSON file containing key-value pairs for character replacements.
    This map is used to clean invalid or unwanted characters from XML content
    before processing. If the file is not found or invalid, logs a warning
    but does not raise an exception.

    Args:
        json_path (str): Path to the JSON file containing the replacement map.

    Returns:
        dict: Dictionary with replacement mappings, or None if loading fails.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load replacement map: {e} - using default map.")
    return {"*": "-", "\x02": "", "\x1A": ""}




@log_exceptions({
    FileNotFoundError: "XML file not found",
    ET.ParseError: "XML parsing failed"
}, log_level="warning", raise_exception=True, logger=logger)
def validate_xml_structure(input_file:str) -> bool:
    """Validates the XML structure of the input file.

    Attempts to parse the XML file using ElementTree. If parsing succeeds,
    the XML is considered valid. This is a basic validation check for
    well-formed XML.

    Args:
        input_file (str): Path to the XML file to validate.

    Returns:
        bool: True if XML is valid (parsing succeeds), raises exception otherwise.

    Raises:
        ET.ParseError: If the XML is malformed.
        FileNotFoundError: If the input file does not exist.

    """
    ET.parse(input_file)  # Attempt to parse the XML file; will raise if invalid            
    return True 


def validate_arguments() -> argparse.Namespace:
    """Validates command-line arguments and returns them after processing.

    Sets up an ArgumentParser with all possible command-line options.
    Parses the arguments, performs validation checks, and adjusts paths
    for test mode. Handles special cases like test mode file paths,
    validation-only runs, and ZIP password checks.

    Returns:
        argparse.Namespace: Parsed and validated command-line arguments.

    Raises:
        SystemExit: If arguments are invalid or required files are missing.
    """
    logger.info("Validating CLI arguments")
    parser = argparse.ArgumentParser(description="Generate XML files based on SQLDEV export.")
    parser.add_argument("input_file", nargs="?", help="Input XML file (optional if --test is used)")
    parser.add_argument("output_dir", nargs="?", help=f"Output directory for XML files (optional) (default: {DEFAULT_OUTPUT_DIR})", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--column-name", default=DEFAULT_COLUMN_NAME, help=f"Column name to extract XML from (default {DEFAULT_COLUMN_NAME})")
    parser.add_argument(     "--z", nargs="+",  metavar=("zip_name", "[zip_password]"), help="Create a zip file. Optionally provide a password.")
    parser.add_argument("--file-id-tag", default=DEFAULT_FILE_ID_TAG, help=f"XML tag to use as the file name (default: '{DEFAULT_FILE_ID_TAG}')")
    parser.add_argument("--test", nargs="?", type=int,const=DEFAULT_TEST_SIZE,default=None, help=f"Optional test size. Defaults to {DEFAULT_TEST_SIZE} if used without value.")

    parser.add_argument("--skip-pause", action="store_true", help="Skip pause at the end of execution", default=False)
    parser.add_argument("--mute", action="store_true",  help="Mute sound effects during execution ")
    parser.add_argument('--dry-run', help='Simulate script execution',action="store_true")
    parser.add_argument("--validate", action="store_true", help="Validate XML structure only")

    parser.add_argument("--version", action="version", version="%(prog)s 1.3 by Laurent Morissette - Generate XML files based on SQLDEV export.", help="Show version information")
    args = parser.parse_args()

    # Check if script is run without arguments and not in test mode; show help and exit
    if len(sys.argv) == 1 and args.test is None:
        logger.info("No arguments provided. Showing help message.")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Ensure input file exists unless in test mode
    if args.test is None and (args.input_file is None or not os.path.isfile(args.input_file)):
        parser.print_help(sys.stderr)
        play_sound(SOUND_ERROR, args.mute)
        raise Exception(f"Error: an existing Input file is required in non-test mode. File '{args.input_file}' does not exist.")

    # Handle test mode: adjust input file and output directory paths
    if args.test:
        # Adjust test set path depending on whether script is run from runner or pure CLI
        args.input_file = TEST_SET_PATH_TEMPLATE.format(args.test) if running_in_test_mode() else TEST_SET_PATH_TEST_TEMPLATE.format(args.test)
        args.output_dir = "tests-results"
        logger.info(f"Test mode enabled. Using test set: {args.input_file}")
        if not os.path.isfile(args.input_file):
            logger.warning(f"Error: Test set file '{args.input_file}' does not exist. Generating it now.")
            generate("./tests", args.test)  # Generate the test set if it does not exist already
            logger.info(f"Test set file '{args.input_file}' generated.")

    # If validation only is requested, validate XML and exit
    
    if args.validate:
        try:
           validate_xml_structure(args.input_file)
           logger.info("XML structure is valid.")
           sys.exit(0)
        except Exception as e:  
            logger.error(f"XML structure validation failed: {e}")
            sys.exit(1)   

    # Validate ZIP password if ZIP creation is requested and password is provided
    if args.z and len(args.z) > 1 and validate_zip_password(args.z[1]) == False:
        sys.exit(1)

    ##XMLExtractor.validate_column_exists(args.input_file, args.column_name)
    logger.info("Arguments validated successfully.")
    return args

def validate_zip_password(password: Optional[str]) -> bool:
    """Validates the ZIP password length for security.

    Ensures the password is at least 5 characters long to provide
    minimal security for ZIP encryption. This is a basic check
    to prevent weak passwords.

    Args:
        password (str): The password string to validate.

    Returns:
        bool: True if password is valid (length >= 5), raises ValueError otherwise.

    Raises:
        ValueError: If password is None or shorter than 5 characters.
    """
    if password is None or len(password) < 5:
        raise ValueError("Password must be at least 5 characters long.")
    return True
def process_input_file_to_ensure_is_clean(input_file: str) -> None:
    """Cleans the input XML file to ensure it contains valid XML content.

    Reads the input file line by line, applies character replacements using
    the global replace_map, and removes invalid XML characters. If any
    cleaning is performed, creates a backup and overwrites the original file.
    This ensures the XML can be parsed without errors.

    Args:
        input_file (str): Path to the XML file to clean.
    """
    input_path = Path(input_file)
    backup = input_path.with_suffix(input_path.suffix + ".bak")
    temp = input_path.with_suffix(input_path.suffix + ".tmp")
    cleaned = False  # Flag to track if any cleaning occurred
    cleaned_lines = []  # List to hold cleaned lines

    # Create a backup of the original file
    shutil.copy2(str(input_path), str(backup))
    logger.info(f"Backup created: {backup}")

    # Precompile replacement regex once for efficiency
    replace_regex = None
    if replace_map:
        replace_regex = re.compile('|'.join(map(re.escape, replace_map)))

    # Read the input file and clean it line by line
    with open(str(input_path), 'r', encoding='utf-8', errors='ignore') as fin:
        for ligne in fin:
            ligne_propre = clean_xml_content(ligne, replace_map, replace_regex)
            if ligne_propre != ligne:
                cleaned = True  # Mark as cleaned if line changed
            cleaned_lines.append(ligne_propre)

    # Write the cleaned lines to the temporary file if any replacements were made
    if cleaned:
        with open(str(temp), 'w', encoding='utf-8') as fout:
            fout.writelines(cleaned_lines)
        logger.info("Cleaning done. Continuing...")
        os.replace(str(temp), str(input_path))  # Replace original with cleaned version
    else:
        # No replacements were made, remove temp file if it exists
        logger.info("No illegal characters found. No replacement done.")
        if os.path.exists(str(temp)):
            os.remove(str(temp))  


def clean_xml_content(content: Optional[str], replace_map: Optional[Dict[str, str]], replace_regex: Optional[Pattern] = None) -> Optional[str]:
    """Clean XML content by removing invalid characters and applying replacements.

    Performs two main cleaning operations:
    1. Removes all characters that are invalid in XML (keeps only chars with ord 9,10,13 or >=32).
    2. Applies custom replacements from the replace_map dictionary using regex.

    This ensures the XML content is well-formed and free of problematic characters.

    Args:
        content (str): The XML content string to clean.
        replace_map (dict): Dictionary of character replacements (e.g., {'*': '-', '\x02': ''}).
        replace_regex (Pattern, optional): Precompiled regex for replace_map. If not provided and replace_map is present, will be compiled.

    Returns:
        str: The cleaned XML content string.
    """
    if not content:
        return content

    # 🔥 Remove ALL invalid XML characters (always executed)
    # Valid XML chars: tab (9), LF (10), CR (13), and chars >= 32
    content = ''.join(
        ch for ch in content
        if ord(ch) in (9, 10, 13) or ord(ch) >= 32
    )

    # 🔥 Apply the replace_map (if present)
    if replace_map:
        # Compile regex if not already provided (for backward compatibility)
        global replace_regex_cache, replace_map_cache
        if replace_regex is None:
            if replace_map_cache != replace_map or replace_regex_cache is None:
                replace_regex_cache = re.compile('|'.join(map(re.escape, replace_map)))
                replace_map_cache = replace_map.copy()
            replace_regex = replace_regex_cache
        content = replace_regex.sub(lambda m: replace_map[m.group(0)], content)

    return content

@log_exceptions({Exception: "Error validating column existence"}, log_level="error", raise_exception=True, logger=logger)
def validate_column_exists(input_file: str, column_name: str) -> bool:
    """Validates if the specified column exists in the XML file.

    Parses the XML file and checks for the presence of a <COLUMN> element
    with the specified NAME attribute. This ensures the column to extract
    from actually exists in the data.

    Args:
        input_file (str): Path to the XML file or XML string content.
        column_name (str): Name of the column to check for.

    Raises:
        ValueError: If the column is not found or if there are parsing errors.
    """
    try:
        if input_file.strip().startswith("<"):
            # Handle XML string input
            root = ET.fromstring(input_file)
        else:
            # Handle file input
            if not os.path.exists(input_file):
                raise ValueError(f"File not found: {input_file}")
            tree = ET.parse(input_file)
            root = tree.getroot()

        # Iterate through COLUMN elements to find the specified name
        for col in root.iter("COLUMN"):
            if col.attrib.get("NAME") == column_name:
                return True

        raise ValueError(f"Column '{column_name}' not found")

    except Exception as e:
        raise ValueError(f"Error validating column '{column_name}': {e}") from e


def get_base_path() -> Path:
    """Get the base path for the application, handling both development and PyInstaller contexts."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

    
class XMLExtractor:
    """Class to extract XML elements from an input file and save them as separate files.

    This class handles the core functionality of parsing an XML file, extracting
    specified columns from <ROW> elements, and saving each as an individual XML file.
    It optionally compresses the output files into a ZIP archive with optional
    password protection. Supports dry-run mode for testing without file creation.
    """

    def __init__(self, input_file: str, output_dir: str, output_file_name: Optional[str], column_name: str, create_zip: bool, zip_password: Optional[str], file_id_tag: str, mute: bool, test_mode: bool = False, dry_run: bool = False) -> None:
        """
        Initializes the XMLExtractor with the provided parameters.

        Sets up all instance variables needed for extraction, including file paths,
        column specifications, ZIP options, and mode flags.

        Args:
            input_file (str): Path to the input XML file.
            output_dir (str): Directory to save the extracted XML files.
            output_file_name (str): Base name for the output ZIP file.
            column_name (str): Name of the column containing XML data to extract.
            create_zip (bool): Whether to create a ZIP archive of output files.
            zip_password (str): Password for ZIP encryption (if applicable).
            file_id_tag (str): XML tag name used to generate unique file names.
            mute (bool): If True, disables sound effects.
            test_mode (bool): If True, enables test-specific behaviors.
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
        self.test_mode = test_mode
        self.dry_run = dry_run
        self.zip_filename = None

    @log_exceptions({
        FileNotFoundError: "Output directory not found",
       Exception: "Error deleting output directory"
   }, log_level="error", raise_exception=True, logger=logger)
    def delete_output_dir(self) -> None:
        """Deletes the output directory and all its contents recursively.

        Walks through the output directory, removing all files and subdirectories.
        This is used when the user confirms deletion of an existing output directory
        before creating new files.

        Raises:
            FileNotFoundError: If the output directory does not exist.
            Exception: For other file system errors during deletion.
        """
        for root, dirs, files in os.walk(self.output_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))  # Remove files
            for name in dirs:
                os.rmdir(os.path.join(root, name))   # Remove subdirectories
        os.rmdir(self.output_dir)  # Remove the root directory
        logger.info(f"Deleted output directory: {self.output_dir}")



    def get_message_id(self, content: str) -> str:
        """Extracts the message ID from the XML content using regex.

        Searches for the specified file_id_tag in the XML content and extracts
        the text between the opening and closing tags. This ID is used as
        the filename for the extracted XML file.

        Args:
            content (str): The XML content string to search.

        Returns:
            str: The extracted message ID, or empty string if not found.
        """
        match = re.search(rf"<{self.file_id_tag}>(.*?)</{self.file_id_tag}>", content)
        return match.group(1) if match else ""

    def check_output_dir(self) -> None:
        """Checks if the output directory exists and handles creation/deletion.

        If the path exists as a file, prompts to delete it. If it's a directory,
        prompts to delete the directory. In test mode, automatically deletes.
        If dry-run is enabled, skips all file system operations. Otherwise,
        creates the directory if it doesn't exist.

        This ensures a clean output directory for new extractions.
        """
        if self.dry_run:
            logger.info(f"[Dry-run] Output directory {self.output_dir} will not be created or deleted.")
            return

        can_delete = 'N'  # Default to not delete
        if os.path.exists(self.output_dir):
            if os.path.isfile(self.output_dir):
                # It's a file, not a directory
                if self.test_mode:
                    can_delete = 'Y'
                else:
                    can_delete = input(f"Output path '{self.output_dir}' exists as a file. Do you want to delete it? (Y/N): ").strip().upper()
                if can_delete == 'Y':
                    os.remove(self.output_dir)  # Remove the file
                    os.makedirs(self.output_dir, exist_ok=True)  # Create directory
                    logger.info(f"Removed file and created output directory '{self.output_dir}'.")
                else:
                    logger.error(f"Output path '{self.output_dir}' is a file. Cannot proceed.")
                    raise ValueError(f"Output path '{self.output_dir}' is a file, not a directory.")
            else:
                # It's a directory
                if self.test_mode:
                    can_delete = 'Y'
                else:
                    can_delete = input(f"Output directory '{self.output_dir}' already exists. Do you want to delete it? (Y/N): ").strip().upper()
                if can_delete == 'Y':
                    self.delete_output_dir()  # Delete existing directory
                    os.makedirs(self.output_dir, exist_ok=True)  # Recreate it
                    logger.info(f"Output directory '{self.output_dir}' recreated.")
                else:
                    logger.info(f"Output directory '{self.output_dir}' already exists. Content will be appended.")
        else:
            os.makedirs(self.output_dir, exist_ok=True)  # Create new directory
            logger.info(f"Output directory '{self.output_dir}' created.")


    @log_exceptions({
        FileNotFoundError: "Input file not found",
        ET.ParseError: "XML parsing error",
        ValueError: "Invalid XML structure or column name not found",
        IOError: "File handling or writing error"
    }, log_level="error", raise_exception=True)
    def extract_and_save_elements(self) -> None:
        """Extracts XML elements from the input file and saves them as separate files.

        Parses the XML file using iterative parsing for memory efficiency.
        For each <ROW> element, extracts the specified column's XML content,
        generates a filename from the message ID, and writes the content to a file.
        Tracks progress and reports completion. Optionally creates a ZIP archive.

        The method uses ElementTree's iterparse to handle large files without
        loading everything into memory at once. Elements are cleared after processing
        to free memory.

        Raises:
            FileNotFoundError: If input file doesn't exist.
            ET.ParseError: If XML is malformed.
            ValueError: If XML structure is invalid or column not found.
            IOError: For file writing errors.
        """
        # Log processing start and output directory
        logger.info(f"Processing file: {self.input_file}")
        logger.info(f"Output directory: {self.output_dir}")
        self.check_output_dir()  # Ensure output directory is ready

        file_count = 0  # Counter for successfully created files
        row_count = self.get_row_count()  # Get total rows for progress calculation
        logger.info(f"Total <ROW> elements to process: {row_count}")

        # Initialize iterative XML parsing for memory efficiency
        context = ET.iterparse(self.input_file, events=("start", "end"))
        _, root = next(context)  # Advance to get root element
        processed_rows = 0  # Track processed rows for progress

        # Validate that root element is <RESULTS> as expected
        if root.tag != "RESULTS":
            raise ValueError("Root element is not <RESULTS>")

        # Process each element in the XML iteratively
        for event, elem in context:
            if event == "end" and elem.tag == "ROW":
                logger.debug(f"Processing <ROW> element: {elem.tag}")
                # Find the column with the specified name
                rich_text = elem.find(f"COLUMN[@NAME='{self.column_name}']")
                if rich_text is not None and rich_text.text:
                    # Extract unique ID for filename
                    xml_id = self.get_message_id(rich_text.text).strip()
                    if xml_id:  # Only process if ID exists
                        file_name = f"{xml_id}.xml"
                        # Calculate and display progress
                        processed_rows += 1
                        if row_count:
                            progress_percentage = (processed_rows / row_count) * 100
                            logger.info(f"Processing {self.file_id_tag}: {xml_id} ({progress_percentage:.2f}%)")
                        else:
                            logger.info(f"Processing {self.file_id_tag}: {xml_id}")
                        if not self.dry_run:
                            # Write XML content to individual file
                            output_path = Path(self.output_dir) / file_name
                            with open(str(output_path), "w", encoding="utf-8") as output:
                                output.write(rich_text.text.strip())
                                file_count += 1
                                logger.info(f"File created: {file_name}")
                        else:
                            # Dry run: just log what would happen
                            logger.info(f"Dry run: File would be created: {file_name}")

                elem.clear()  # Free memory by clearing processed element

        root.clear()  # Clear root element to free memory

        # Create ZIP archive if requested
        if self.create_zip:
            self.create_zip_archive()

        logger.info(f"Total files created: {file_count}")




    @log_exceptions({
       Exception: "Error counting <ROW> elements"
   }, log_level="error", raise_exception=True, logger=logger)
    def get_row_count(self) -> int:
        """Counts the number of <ROW> elements in the input XML file.

        Uses iterative parsing to count rows without loading the entire file
        into memory. This is used for progress reporting during extraction.

        Returns:
            int: The total number of <ROW> elements found in the XML file.
        """
        logger.info(f"Counting <ROW> elements in: {self.input_file[:60]}")
        if self.input_file.strip().startswith("<"):
            return self.input_file.count("<ROW>")
        with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for line in f if '<ROW>' in line)
        
        
    @log_exceptions({Exception: "Error creating unprotected zip file"}, log_level="error", raise_exception=True, logger=logger)
    def create_unprotected_zip(self, zip_filename: str = None):
         """Creates a plain ZIP archive without password protection.

         Uses standard ZIP compression to archive all files in the output directory.
         The ZIP file is named based on the provided filename or output_file_name attribute.

         Args:
             zip_filename (str, optional): Explicit ZIP filename. If not provided, uses output_file_name.

         Raises:
             Exception: For any errors during ZIP creation or file operations.
         """
         if not zip_filename:
             zip_filename = self.zip_filename or f"{self.output_file_name}.zip"
         full_zip_path = Path(self.output_dir).parent / zip_filename
         with zipfile.ZipFile(str(full_zip_path), 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            # Walk through output directory and add all files
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    # Add file with relative path to maintain directory structure
                    zipf.write(str(file_path), str(file_path.relative_to(self.output_dir)))
            logger.info(f"ZIP archive '{full_zip_path}' created successfully without password protection.")


    @log_exceptions({
       Exception: "Error creating protected zip file"
   }, log_level="error", raise_exception=True)
    def create_protected_zip(self, zip_filename: str = None):
        """Creates a ZIP archive with AES encryption and password protection.

        Uses pyzipper to create a password-protected ZIP file with AES encryption.
        All files in the output directory are added to the archive.

        Args:
            zip_filename (str, optional): Explicit ZIP filename. If not provided, uses output_file_name.

        Raises:
            Exception: For errors during ZIP creation or file operations.
        """
        if not zip_filename:
            zip_filename = self.zip_filename or f"{self.output_file_name}-protected.zip"
        full_zip_path = Path(self.output_dir).parent / zip_filename
        with pyzipper.AESZipFile(str(full_zip_path), 'w', compression=zipfile.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
            zipf.setpassword(self.zip_password.encode('utf-8'))  # Set password for encryption
            # Add all files from output directory
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    zipf.write(str(file_path), file)  # Add with just filename (no path)
        logger.info(f"Protected ZIP archive '{full_zip_path}' created successfully.")

    def create_zip_archive(self) -> None:
        """Creates a ZIP archive of the extracted XML files.

        Determines whether to create a password-protected or unprotected ZIP
        based on the presence of a password. Calls the appropriate ZIP creation method.
        Skips if dry-run is enabled.

        This method orchestrates ZIP creation after file extraction.
        """
        if self.dry_run:
           logger.info(f"[Dry-run] No zip named {self.output_file_name} will be created.")
           return

        if self.zip_password:
            # Create password-protected ZIP
            zip_filename = f"{self.output_file_name}-protected.zip"
            self.zip_filename = zip_filename
            self.create_protected_zip(zip_filename)
        else:
            # Create unprotected ZIP
            zip_filename = f"{self.output_file_name}.zip"
            self.zip_filename = zip_filename
            self.create_unprotected_zip(zip_filename)













def main() -> None:
    """Main entry point for the script.

    Orchestrates the entire XML extraction process:
    - Configures logging
    - Validates arguments
    - Loads replacement map
    - Cleans input file
    - Validates column existence
    - Initializes and runs XMLExtractor
    - Handles sound effects and user interaction
    - Manages errors and cleanup

    This function serves as the central coordinator for all script operations.
    """
    global logger, replace_map
    try:
        start_time = time.time()  # Record start time for performance measurement
        logger = configure_logging()  # Set up logging system
        args = validate_arguments()  # Parse and validate command-line arguments

        # Ensure input file exists
        if not os.path.exists(args.input_file):
            raise FileNotFoundError(f"Input file '{args.input_file}' does not exist.")

        # Determine path to replacements.json consistently using pathlib
        base_path = get_base_path()
        replace_map_path = base_path / REPLACEMENT_MAP_FILE
        # Load character replacement mappings
        replace_map = load_replace_map_from_json(replace_map_path) 
        logger.info(f"Replacement map loaded  : {replace_map}")

        # Clean the input XML file to remove invalid characters
        process_input_file_to_ensure_is_clean(args.input_file)
        # Validate that the specified column exists in the XML
        validate_column_exists(args.input_file, args.column_name)

        logger.info("Starting XMLExtractor script")
        play_sound(SOUND_START, args.mute)  # Play start sound effect

        # Extract ZIP parameters from arguments
        zip_password = args.z[1] if args.z and len(args.z) > 1 else None
        zip_name = args.z[0] if args.z else None
        test_set_size = args.test if args.test else DEFAULT_TEST_SIZE  # Default test size
        is_test_mode = args.test is not None

        # Initialize XMLExtractor with all parameters
        extractor = XMLExtractor(
            args.input_file,
            args.output_dir,
            zip_name,
            args.column_name,
            bool(args.z),
            zip_password,
            args.file_id_tag,
            args.mute,
            is_test_mode,
            args.dry_run
        )

        # Perform the main extraction and saving operation
        extractor.extract_and_save_elements()

        logger.info("Script completed successfully.")
        play_sound(SOUND_DONE, args.mute)  # Play completion sound
        logger.info(f"Total execution time: {time.time() - start_time:.2f} seconds")

        # Pause for user interaction unless skip-pause is set
        input("Press Enter to exit...") if (args.skip_pause is False) else sys.exit(0)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error("Script execution failed.")
        play_sound(SOUND_ERROR, "N")  # Play error sound (force on)
        sys.exit(1)


if __name__ == "__main__":
    # Entry point when script is run directly (not imported as module)
    main()