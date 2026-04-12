"""Unit tests for validate_arguments().
These tests cover CLI parsing, test-mode file selection, XML validation mode, and ZIP password checking."""
import sys
import unittest
from unittest.mock import MagicMock, patch
import xml_extractor as xe


class TestValidateArguments(unittest.TestCase):

    """Verify CLI arguments parsing, file validation, test-mode behavior, and zip password validation."""
    def setUp(self):
        xe.logger = MagicMock()

    # --------------------------------------------------
    # 1. No arguments → help + exit(1)
    # --------------------------------------------------
    def test_no_arguments_exit(self):
        """Verify that No arguments exit."""
        with patch.object(sys, "argv", ["prog"]), \
             patch("argparse.ArgumentParser.print_help"), \
             patch("sys.exit", side_effect=SystemExit) as mock_exit:
            with self.assertRaises(SystemExit):
                xe.validate_arguments()
        mock_exit.assert_called_with(1)

    # --------------------------------------------------
    # 2. Missing input file → exception
    # --------------------------------------------------
    def test_missing_input_file_raises(self):
        """Verify that Missing input file raises."""
        with patch.object(sys, "argv", ["prog", "missing.xml"]), \
             patch("os.path.isfile", return_value=False), \
             patch("argparse.ArgumentParser.print_help"), \
             patch("xml_extractor.play_sound"):
            with self.assertRaises(Exception):
                xe.validate_arguments()

    # --------------------------------------------------
    # 3. Test mode — set file exists
    # --------------------------------------------------
    def test_test_mode_file_exists(self):
        """Verify that test mode file exists."""
        with patch.object(sys, "argv", ["prog", "--test", "5"]), \
             patch("os.path.isfile", return_value=True), \
             patch("xml_extractor.running_in_test_mode", return_value=True):
            args = xe.validate_arguments()
        self.assertIn("sets/set_5.xml", args.input_file)
        self.assertEqual(args.output_dir, "tests-results")

    # --------------------------------------------------
    # 4. Test mode — set file missing → generate() called
    # --------------------------------------------------
    def test_test_mode_generate_called(self):
        """Verify that test mode generate called."""
        with patch.object(sys, "argv", ["prog", "--test", "5"]), \
             patch("os.path.isfile", return_value=False), \
             patch("xml_extractor.running_in_test_mode", return_value=True), \
             patch("xml_extractor.generate") as mock_generate:
            xe.validate_arguments()
        mock_generate.assert_called_once()

    # --------------------------------------------------
    # 5. --validate with invalid XML → exit(1)
    # --------------------------------------------------
    def test_validate_xml_false(self):
        """Verify that Validate xml false."""
        with patch.object(sys, "argv", ["prog", "file.xml", "--validate"]), \
             patch("os.path.isfile", return_value=True), \
             patch("xml_extractor.validate_xml_structure", return_value=False), \
             patch("sys.exit") as mock_exit:
            xe.validate_arguments()
        mock_exit.assert_called_with(1)

    # --------------------------------------------------
    # 6. --validate with valid XML → exit(0)
    # --------------------------------------------------
    def test_validate_xml_true(self):
        """Verify that Validate xml true."""
        with patch.object(sys, "argv", ["prog", "file.xml", "--validate"]), \
             patch("os.path.isfile", return_value=True), \
             patch("xml_extractor.validate_xml_structure", return_value=True), \
             patch("sys.exit") as mock_exit:
            xe.validate_arguments()
        mock_exit.assert_called_with(0)

    # --------------------------------------------------
    # 7. Invalid ZIP password → exit(1)
    # --------------------------------------------------
    def test_invalid_zip_password(self):
        """Verify that Invalid zip password."""
        with patch.object(sys, "argv", ["prog", "file.xml", "--z", "archive.zip", "123"]), \
             patch("os.path.isfile", return_value=True), \
             patch("xml_extractor.validate_zip_password", return_value=False), \
             patch("sys.exit") as mock_exit:
            xe.validate_arguments()
        mock_exit.assert_called_with(1)

    # --------------------------------------------------
    # 8. Valid ZIP password → args returned
    # --------------------------------------------------
    def test_valid_zip_password(self):
        """Verify that Valid zip password."""
        with patch.object(sys, "argv", ["prog", "file.xml", "--z", "archive.zip", "12345"]), \
             patch("os.path.isfile", return_value=True), \
             patch("xml_extractor.validate_zip_password", return_value=True):
            args = xe.validate_arguments()
        self.assertEqual(args.z[0], "archive.zip")

    # --------------------------------------------------
    # 9. Normal full flow → args returned
    # --------------------------------------------------
    def test_valid_arguments_success(self):
        """Verify that Valid arguments success."""
        with patch.object(sys, "argv", ["prog", "file.xml"]), \
             patch("os.path.isfile", return_value=True):
            args = xe.validate_arguments()
        self.assertEqual(args.input_file, "file.xml")
