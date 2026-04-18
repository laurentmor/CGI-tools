# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""Performance regression tests for core helper functions.
These tests compare relative timings on the current machine to avoid brittle absolute thresholds."""

import logging
import timeit
import unittest

import xml_extractor as xe
from tests.fixtures import REPLACE_MAP, make_extractor


class TestPerformanceRegression(unittest.TestCase):
    """Verify relative performance characteristics remain acceptable across helper functions."""

    REPS = 7
    N = 500

    def setUp(self):
        xe.logger = logging.getLogger("test")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _median(self, times):
        s = sorted(times)
        n = len(s)
        return (s[n // 2] + s[~(n // 2)]) / 2

    def _median_us_per_call(self, fn, n=None, reps=None) -> float:
        n = n or self.N
        reps = reps or self.REPS
        return self._median(timeit.repeat(fn, number=n, repeat=reps)) / n * 1e6

    def _baseline_us(self, n=None, reps=None) -> float:
        """Cost of a bare lambda call on this machine (floor 0.05 µs)."""
        dummy = object()
        raw = timeit.repeat(lambda: dummy, number=n or self.N, repeat=reps or self.REPS)
        return max(self._median(raw) / (n or self.N) * 1e6, 0.05)

    def _assert_relative(self, fn, max_multiplier: float, label: str, n=None, reps=None):
        baseline = self._baseline_us(n, reps)
        actual_us = self._median_us_per_call(fn, n, reps)
        ratio = actual_us / baseline
        print(
            f"\n[PERF] {label}: {actual_us:.2f} µs/call  "
            f"(baseline {baseline:.3f} µs, ratio {ratio:.1f}×, limit {max_multiplier}×)"
        )
        self.assertLess(
            ratio,
            max_multiplier,
            f"{label} too slow: {actual_us:.2f} µs/call is "
            f"{ratio:.1f}× baseline (limit {max_multiplier}×)",
        )

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_clean_xml_relative_speed(self):
        """Verify that Clean xml relative speed."""
        content = "Hello * World \x02 End\x1a"
        self._assert_relative(
            lambda: xe.clean_xml_content(content, REPLACE_MAP),
            max_multiplier=200,
            label="clean_xml_content",
        )

    def test_get_message_id_relative_speed(self):
        """Verify that Get message id relative speed."""
        ext = make_extractor()
        content = "<Proponix><Header><MessageID>MSG12345678</MessageID></Header></Proponix>"
        self._assert_relative(
            lambda: ext.get_message_id(content),
            max_multiplier=200,
            label="get_message_id",
        )

    def test_validate_zip_password_relative_speed(self):
        """Verify that Validate zip password relative speed."""
        self._assert_relative(
            lambda: xe.validate_zip_password("valid_password_123"),
            max_multiplier=100,
            label="validate_zip_password",
            n=2000,
        )

    def test_clean_xml_scales_linearly(self):
        """Verify that Clean xml scales linearly."""
        lines_100 = [f"Line {i} * \x02 \x1a\n" for i in range(100)]
        lines_1000 = lines_100 * 10

        def run_100():
            for line in lines_100:
                xe.clean_xml_content(line, REPLACE_MAP)

        def run_1000():
            for line in lines_1000:
                xe.clean_xml_content(line, REPLACE_MAP)

        t_100 = min(timeit.repeat(run_100, number=1, repeat=10))
        t_1000 = min(timeit.repeat(run_1000, number=1, repeat=10))
        ratio = t_1000 / t_100 if t_100 > 0 else 1
        print(f"\n[PERF] linear scaling ratio (×10 input): {ratio:.2f}×")
        self.assertLess(
            ratio,
            20,
            f"clean_xml_content scaling ratio {ratio:.2f}× exceeds 20× "
            f"(t_100={t_100 * 1000:.2f}ms, t_1000={t_1000 * 1000:.2f}ms)",
        )
