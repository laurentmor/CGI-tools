"""Unit tests for XMLExtractor initialization.
These tests verify that constructor arguments are stored correctly and defaults are applied."""
import unittest
from tests.fixtures import make_extractor


class TestXMLExtractorInit(unittest.TestCase):

    """Verify XMLExtractor initialization and default attribute handling."""
    def test_all_attributes_set(self):
        """Verify that All attributes set."""
        extractor = make_extractor(input_file="in.xml", output_dir="out",
                                   zip_password="pass1", create_zip=True)
        self.assertEqual(extractor.input_file, "in.xml")
        self.assertEqual(extractor.output_dir, "out")
        self.assertEqual(extractor.zip_password, "pass1")
        self.assertTrue(extractor.create_zip)

    def test_dry_run_default_false(self):
        """Verify that dry-run mode default false."""
        self.assertFalse(make_extractor().dry_run)

    def test_mute_stored(self):
        """Verify that Mute stored."""
        self.assertTrue(make_extractor(mute=True).mute)
