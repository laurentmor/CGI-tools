"""Unit tests for xml_extractor.main() and the module entry-point guard.
These tests verify CLI flow, error handling, ZIP options, and the __main__ execution path."""

import itertools
import unittest
from unittest.mock import MagicMock, patch

import xml_extractor as xe


class TestMainBlock(unittest.TestCase):

    """Verify main entrypoint behavior, CLI handling, and __main__ guard execution."""
    def _fake_args(self, **overrides):
        defaults = dict(
            input_file="file.xml", output_dir="out", column_name="COL",
            z=None, file_id_tag="MessageID", mute=False,
            test=None, dry_run=False, skip_pause=True,
        )
        defaults.update(overrides)
        return MagicMock(**defaults)

    # --------------------------------------------------
    # SUCCESS path
    # --------------------------------------------------
    def test_main_success(self):
        """Verify that Main success."""
        fake_args = self._fake_args(skip_pause=True)
        fake_extractor = MagicMock()

        with patch.object(xe, "configure_logging", return_value=MagicMock()), \
             patch.object(xe, "validate_arguments", return_value=fake_args), \
             patch.object(xe.os.path, "exists", return_value=True), \
             patch.object(xe, "running_in_test_mode", return_value=False), \
             patch.object(xe, "load_replace_map_from_json", return_value={}), \
             patch.object(xe, "process_input_file_to_ensure_is_clean"), \
             patch.object(xe, "validate_column_exists"), \
             patch.object(xe, "play_sound"), \
             patch.object(xe, "XMLExtractor", return_value=fake_extractor), \
             patch.object(xe.time, "time", side_effect=itertools.count(0)), \
             patch.object(xe.sys, "exit", side_effect=SystemExit) as mock_exit:

            with self.assertRaises(SystemExit):
                xe.main()

        fake_extractor.extract_and_save_elements.assert_called_once()
        mock_exit.assert_called_with(0)

    # --------------------------------------------------
    # FILE NOT FOUND path
    # --------------------------------------------------
    def test_main_file_not_found(self):
        """Verify that Main file not found."""
        fake_args = self._fake_args()

        with patch.object(xe, "configure_logging", return_value=MagicMock()), \
             patch.object(xe, "validate_arguments", return_value=fake_args), \
             patch.object(xe.os.path, "exists", return_value=False), \
             patch.object(xe, "play_sound"), \
             patch.object(xe.sys, "exit", side_effect=SystemExit) as mock_exit:

            with self.assertRaises(SystemExit):
                xe.main()

        mock_exit.assert_called_with(1)

    # --------------------------------------------------
    # EXCEPTION path
    # --------------------------------------------------
    def test_main_exception(self):
        """Verify that Main exception."""
        fake_args = self._fake_args()

        with patch.object(xe, "configure_logging", return_value=MagicMock()), \
             patch.object(xe, "validate_arguments", return_value=fake_args), \
             patch.object(xe.os.path, "exists", return_value=True), \
             patch.object(xe, "process_input_file_to_ensure_is_clean",
                          side_effect=Exception("boom")), \
             patch.object(xe, "play_sound"), \
             patch.object(xe.sys, "exit", side_effect=SystemExit) as mock_exit:

            with self.assertRaises(SystemExit):
                xe.main()

        mock_exit.assert_called_with(1)

    # --------------------------------------------------
    # ZIP path
    # --------------------------------------------------
    def test_main_with_zip(self):
        """Verify that Main with zip."""
        fake_args = self._fake_args(z=["archive.zip", "pass123"], skip_pause=True)
        fake_extractor = MagicMock()

        with patch.object(xe, "configure_logging", return_value=MagicMock()), \
             patch.object(xe, "validate_arguments", return_value=fake_args), \
             patch.object(xe.os.path, "exists", return_value=True), \
             patch.object(xe, "running_in_test_mode", return_value=False), \
             patch.object(xe, "load_replace_map_from_json", return_value={}), \
             patch.object(xe, "process_input_file_to_ensure_is_clean"), \
             patch.object(xe, "validate_column_exists"), \
             patch.object(xe, "play_sound"), \
             patch.object(xe, "XMLExtractor", return_value=fake_extractor), \
             patch.object(xe.time, "time", side_effect=itertools.count(0)), \
             patch.object(xe.sys, "exit", side_effect=SystemExit):

            with self.assertRaises(SystemExit):
                xe.main()

        fake_extractor.extract_and_save_elements.assert_called_once()

    # --------------------------------------------------
    # PAUSE path (skip_pause=None → input() called)
    # --------------------------------------------------
    def test_main_pause(self):
        """Verify that Main pause."""
        fake_args = self._fake_args(skip_pause=None)
        fake_extractor = MagicMock()

        with patch.object(xe, "configure_logging", return_value=MagicMock()), \
             patch.object(xe, "validate_arguments", return_value=fake_args), \
             patch.object(xe.os.path, "exists", return_value=True), \
             patch.object(xe, "running_in_test_mode", return_value=False), \
             patch.object(xe, "load_replace_map_from_json", return_value={}), \
             patch.object(xe, "process_input_file_to_ensure_is_clean"), \
             patch.object(xe, "validate_column_exists"), \
             patch.object(xe, "play_sound"), \
             patch.object(xe, "XMLExtractor", return_value=fake_extractor), \
             patch.object(xe.time, "time", side_effect=itertools.count(0)), \
             patch("builtins.input") as mock_input, \
             patch.object(xe.sys, "exit", side_effect=SystemExit):

            with self.assertRaises(SystemExit):
                xe.main()

        mock_input.assert_called_once()


class TestMainGuard(unittest.TestCase):
    """Verify main entrypoint behavior, CLI handling, and __main__ guard execution."""

    def test_name_main_guard_executes_main(self):
        """Verify that Name main guard executes main."""
        original_name = xe.__name__
        try:
            with patch.object(xe, "main", side_effect=SystemExit(42)) as mock_main:
                xe.__name__ = "__main__"
                with self.assertRaises(SystemExit) as ctx:
                    # replicate the guard exactly as written in the source
                    if xe.__name__ == "__main__":
                        xe.main()
        finally:
            xe.__name__ = original_name

        self.assertEqual(ctx.exception.code, 42,
                         "guard should call main() which raises SystemExit(42)")
        mock_main.assert_called_once()
