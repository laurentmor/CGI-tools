"""Unit tests for validate_zip_password().
These tests verify the password rules and ensure invalid values raise the expected exceptions."""
import unittest
import xml_extractor as xe


class TestValidateZipPassword(unittest.TestCase):

    """Verify ZIP password validation rules and error conditions."""
    def test_valid_password(self):
        """Verify that Valid password."""
        self.assertTrue(xe.validate_zip_password("secret123"))

    def test_exactly_five_chars(self):
        """Verify that Exactly five chars."""
        self.assertTrue(xe.validate_zip_password("abcde"))

    def test_too_short_raises(self):
        """Verify that Too short raises."""
        with self.assertRaises(ValueError):
            xe.validate_zip_password("abc")

    def test_none_raises(self):
        """Verify that None raises."""
        with self.assertRaises((ValueError, TypeError)):
            xe.validate_zip_password(None)

    def test_empty_string_raises(self):
        """Verify that Empty string raises."""
        with self.assertRaises(ValueError):
            xe.validate_zip_password("")
