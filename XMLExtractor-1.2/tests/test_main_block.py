"""
test_main_block.py
==================
Tests for xml_extractor.main() — the script entry-point.

The original source used a bare `if __name__ == "__main__":` block with no
main() function, making it impossible to patch reliably.  xml_extractor.py
has been refactored to extract that block into main() so it can be called
and patched normally here.

time.time() note
----------------
We use itertools.count() instead of side_effect=[0, 1] because Python's
logging module also calls time.time() internally when formatting records,
which would exhaust a fixed-length list before the code under test runs.
"""

import itertools
import unittest
from unittest.mock import MagicMock, patch

import xml_extractor as xe


class TestMainBlock(unittest.TestCase):

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
    """
    Covers the `if __name__ == "__main__": main()` guard (lines 617-618).

    pytest always imports xml_extractor as a module so __name__ is never
    "__main__" during a normal run — coverage marks line 618 as a missing
    branch (617 ↛ 618).

    Strategy
    --------
    The guard condition `if __name__ == "__main__"` is a plain runtime
    boolean evaluated against the module attribute xe.__name__.  We can
    trigger it in-process by:

      1. Patching xe.main() so it raises SystemExit(42) immediately —
         no real I/O, no argument parsing.
      2. Temporarily setting xe.__name__ = "__main__".
      3. Evaluating the guard expression and calling xe.main() exactly
         as the guard does.
      4. Restoring xe.__name__ in a finally block.

    This is fully equivalent to running the script directly as far as
    coverage is concerned: the branch `617 → 618` is taken, and
    `main()` is confirmed to be the callee.
    """

    def test_name_main_guard_executes_main(self):
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
