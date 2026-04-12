import unittest
import xml_extractor as xe


class TestValidateZipPassword(unittest.TestCase):

    def test_valid_password(self):
        self.assertTrue(xe.validate_zip_password("secret123"))

    def test_exactly_five_chars(self):
        self.assertTrue(xe.validate_zip_password("abcde"))

    def test_too_short_raises(self):
        with self.assertRaises(ValueError):
            xe.validate_zip_password("abc")

    def test_none_raises(self):
        with self.assertRaises((ValueError, TypeError)):
            xe.validate_zip_password(None)

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            xe.validate_zip_password("")
