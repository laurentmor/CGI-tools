import logging
import time
import unittest
from unittest.mock import MagicMock, patch
import xml_extractor as xe
from tests.fixtures import make_extractor, patch_iterparse, REPLACE_MAP


class BenchmarkFixtures:
    """In-memory XML generation utilities for benchmark tests."""

    @staticmethod
    def make_xml(n_rows: int) -> str:
        rows = "\n".join(
            f'  <ROW>\n'
            f'    <COLUMN NAME="RICH_TEXT_NCLOB">'
            f'<![CDATA[<Proponix><Header><MessageID>MSG{i:08d}</MessageID></Header></Proponix>]]>'
            f'</COLUMN>\n  </ROW>'
            for i in range(n_rows)
        )
        return f"<?xml version='1.0' encoding='UTF8'?>\n<RESULTS>\n{rows}\n</RESULTS>"

    @staticmethod
    def make_dirty_xml(n_rows: int) -> str:
        """XML with control characters to stress-test the cleaner."""
        rows = "\n".join(
            f'  <ROW>\n'
            f'    <COLUMN NAME="RICH_TEXT_NCLOB">'
            f'<![CDATA[<Root>\x02<MessageID>MSG{i:08d}</MessageID>\x1A</Root>]]>'
            f'</COLUMN>\n  </ROW>'
            for i in range(n_rows)
        )
        return f"<?xml version='1.0' encoding='UTF8'?>\n<RESULTS>\n{rows}\n</RESULTS>"


class TestBenchmarks(unittest.TestCase):
    """
    Micro-benchmark suite executed as part of the normal test run.
    Each test records elapsed wall time and asserts it stays within a
    generous threshold so CI does not false-positive on slow machines.
    """

    THRESHOLDS = {
        "clean_xml_1000_lines": 0.5,    # seconds
        "get_message_id_10000": 0.5,
        "get_row_count_100_rows": 1.0,
        "extract_10_rows": 1.0,
        "extract_100_rows": 3.0,
    }

    def setUp(self):
        xe.logger = logging.getLogger("test")

    def test_bench_clean_xml_1000_lines(self):
        lines = [f"Line {i} with * and \x02 and \x1A\n" for i in range(1000)]
        t0 = time.perf_counter()
        for line in lines:
            xe.clean_xml_content(line, REPLACE_MAP)
        elapsed = time.perf_counter() - t0
        print(f"\n[BENCH] clean_xml_content 1000 lines: {elapsed*1000:.2f} ms")
        self.assertLess(elapsed, self.THRESHOLDS["clean_xml_1000_lines"])

    def test_bench_get_message_id_10000_calls(self):
        ext = make_extractor()
        content = "<Proponix><Header><MessageID>MSG12345678</MessageID></Header></Proponix>"
        t0 = time.perf_counter()
        for _ in range(10_000):
            ext.get_message_id(content)
        elapsed = time.perf_counter() - t0
        print(f"\n[BENCH] get_message_id ×10 000: {elapsed*1000:.2f} ms")
        self.assertLess(elapsed, self.THRESHOLDS["get_message_id_10000"])

    def test_bench_get_row_count_100_rows(self):
        xml_100 = BenchmarkFixtures.make_xml(100)
        ext = make_extractor()
        t0 = time.perf_counter()
        with patch_iterparse(xml_100):
            ext.get_row_count()
        elapsed = time.perf_counter() - t0
        print(f"\n[BENCH] get_row_count (100 rows): {elapsed*1000:.2f} ms")
        self.assertLess(elapsed, self.THRESHOLDS["get_row_count_100_rows"])

    def test_bench_extract_10_rows(self):
        self._bench_extraction(BenchmarkFixtures.make_xml(10), "extract_10_rows")

    def test_bench_extract_100_rows(self):
        self._bench_extraction(BenchmarkFixtures.make_xml(100), "extract_100_rows")

    def _bench_extraction(self, xml_string: str, label: str):
        ext = make_extractor()
        handle = MagicMock()
        handle.__enter__ = lambda s: s
        handle.__exit__ = MagicMock(return_value=False)
        handle.write = MagicMock()

        t0 = time.perf_counter()
        with patch_iterparse(xml_string), \
             patch("builtins.open", return_value=handle), \
             patch.object(ext, "check_output_dir"), \
             patch.object(ext, "create_zip_archive"):
            ext.extract_and_save_elements()
        elapsed = time.perf_counter() - t0
        print(f"\n[BENCH] {label}: {elapsed*1000:.2f} ms")
        self.assertLess(elapsed, self.THRESHOLDS[label])
