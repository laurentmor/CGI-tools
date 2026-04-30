# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Unit tests for validate_arguments().
These tests cover CLI parsing, test-mode file selection, XML validation mode, and ZIP password checking."""

import sys
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import xml_extractor as xe  # type: ignore


class TestValidateArguments(unittest.TestCase):
    """Verify CLI arguments parsing, file validation, test-mode behavior, and zip password validation."""

    def setUp(self):
        import xml_extractor.xml_extractor as xe_mod  # type: ignore

        xe_mod.logger = MagicMock()

    # --------------------------------------------------
    # 1. No arguments → help + exit(1)
    # --------------------------------------------------
    def test_no_arguments_exit(self):
        """Verify that No arguments exit."""
        with (
            patch.object(sys, "argv", ["prog"]),
            patch("argparse.ArgumentParser.print_help"),
            patch("sys.exit", side_effect=SystemExit) as mock_exit,self.assertRaises(SystemExit)
        ):
            xe.validate_arguments()
        mock_exit.assert_called_with(1)

    # --------------------------------------------------
    # 2. Missing input file → exception
    # --------------------------------------------------
    def test_missing_input_file_raises(self):
        """Verify that Missing input file raises."""
        with patch.object(sys, "argv", ["prog", "missing.xml"]), \
            patch("xml_extractor.xml_extractor.Path.exists", return_value=False), \
            patch("argparse.ArgumentParser.print_help"), \
            patch("xml_extractor.xml_extractor.play_sound"), self.assertRaises(FileNotFoundError):
            xe.validate_arguments()

    # --------------------------------------------------
    # 5. --validate with invalid XML → exit(1)
    # --------------------------------------------------
    def test_validate_xml_false(self):
        """Verify that invalid XML structure exits with code 1."""
        with (
            patch.object(sys, "argv", ["prog", "file.xml", "--validate"]),
            patch("xml_extractor.xml_extractor.Path.exists", return_value=True),
            patch(
                "xml_extractor.xml_extractor.validate_xml_structure",
                side_effect=ET.ParseError("bad xml"),
            ),
            patch("xml_extractor.xml_extractor.sys.exit") as mock_exit,
        ):
            xe.validate_arguments()
        mock_exit.assert_called_with(1)

    # --------------------------------------------------
    # 6. --validate with valid XML → exit(0)
    # --------------------------------------------------
    def test_validate_xml_true(self):
        """Verify that Validate xml true."""
        with (
            patch.object(sys, "argv", ["prog", "file.xml", "--validate"]),
            patch("xml_extractor.xml_extractor.Path.exists", return_value=True),
            patch("xml_extractor.xml_extractor.validate_xml_structure", return_value=True),
            patch("xml_extractor.xml_extractor.sys.exit") as mock_exit,
        ):
            xe.validate_arguments()
        mock_exit.assert_called_with(0)

    # --------------------------------------------------
    # 7. Invalid ZIP password → exit(1)
    # --------------------------------------------------
    def test_invalid_zip_password(self):
        """Verify that an invalid zip password raises ValueError."""
        with (
            patch.object(sys, "argv", ["prog", "file.xml", "--z", "archive.zip", "123"]),
            patch("xml_extractor.xml_extractor.Path.exists", return_value=True),
        ):
            with self.assertRaises(ValueError) as context:
                xe.validate_arguments()

            self.assertIn("Password must be at least", str(context.exception))

    # --------------------------------------------------
    # 8. Valid ZIP password → args returned
    # --------------------------------------------------
    def test_valid_zip_password(self):
        """Verify that Valid zip password."""
        with (
            patch.object(sys, "argv", ["prog", "file.xml", "--z", "archive.zip", "12345"]),
            patch("xml_extractor.xml_extractor.Path.exists", return_value=True),
            patch("xml_extractor.xml_extractor.validate_zip_password", return_value=True),
        ):
            args = xe.validate_arguments()
        self.assertEqual(args.z[0], "archive.zip")

    # --------------------------------------------------
    # 9. Normal full flow → args returned
    # --------------------------------------------------
    def test_valid_arguments_success(self):
        """Verify that Valid arguments success."""
        with (
            patch.object(sys, "argv", ["prog", "file.xml"]),
            patch("xml_extractor.xml_extractor.Path.exists", return_value=True),
        ):
            args = xe.validate_arguments()
        self.assertEqual(args.input_file, "file.xml")
