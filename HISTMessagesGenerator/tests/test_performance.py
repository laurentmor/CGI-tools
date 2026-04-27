# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Performance and benchmark tests for HISTMessagesGenerator.

Uses pytest-benchmark for timing assertions.
Separate non-benchmark performance regression tests use time.perf_counter.

These tests ensure the system handles realistic data volumes within
acceptable time budgets.
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET

import pytest
from fixtures import LARGE_XML, make_xml

from hist_messages_generator import HISTMessagesGenerator
from hist_messages_generator.product_class_resolver import ProductType, resolve_class

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_xml_n(n: int, product_type: str = "DLC") -> str:
    return make_xml(
        [
            {
                "INSTRUMENT_ID": f"INS{i:06d}",
                "TYPE_": product_type,
                "CUSTOMER_PARTY_TYPE": "BUYER",
            }
            for i in range(1, n + 1)
        ]
    )


# ---------------------------------------------------------------------------
# resolve_class benchmarks
# ---------------------------------------------------------------------------


class TestResolveClassPerformance:
    def test_single_resolve_under_1ms(self):
        start = time.perf_counter()
        resolve_class("DLC")
        elapsed = time.perf_counter() - start
        assert elapsed < 0.001, f"resolve_class took {elapsed:.4f}s, expected < 1ms"

    def test_1000_resolves_under_50ms(self):
        codes = [pt.value for pt in ProductType] * 44  # ~1012 calls
        start = time.perf_counter()
        for code in codes:
            resolve_class(code)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.05, f"1000 resolve_class calls took {elapsed:.4f}s, expected < 50ms"


@pytest.mark.benchmark(group="resolve_class")
def test_benchmark_resolve_class_dlc(benchmark):
    benchmark(resolve_class, "DLC")


@pytest.mark.benchmark(group="resolve_class")
def test_benchmark_resolve_class_all_types(benchmark):
    codes = [pt.value for pt in ProductType]

    def _resolve_all():
        for c in codes:
            resolve_class(c)

    benchmark(_resolve_all)


# ---------------------------------------------------------------------------
# build_instruments_dictionary benchmarks
# ---------------------------------------------------------------------------


class TestBuildDictPerformance:
    def test_100_rows_under_100ms(self):
        root = ET.fromstring(_make_xml_n(100))
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        start = time.perf_counter()
        g.build_instruments_dictionary(root)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.1, f"build_instruments_dictionary(100) took {elapsed:.4f}s"

    def test_1000_rows_under_1s(self):
        root = ET.fromstring(_make_xml_n(1000))
        g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
        start = time.perf_counter()
        result = g.build_instruments_dictionary(root)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"build_instruments_dictionary(1000) took {elapsed:.4f}s"
        assert len(result) == 1000


@pytest.mark.benchmark(group="build_dict")
def test_benchmark_build_dict_100(benchmark):
    root = ET.fromstring(_make_xml_n(100))
    g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
    benchmark(g.build_instruments_dictionary, root)


@pytest.mark.benchmark(group="build_dict")
def test_benchmark_build_dict_1000(benchmark):
    root = ET.fromstring(_make_xml_n(1000))
    g = HISTMessagesGenerator.__new__(HISTMessagesGenerator)
    benchmark(g.build_instruments_dictionary, root)


# ---------------------------------------------------------------------------
# get_row_count benchmarks
# ---------------------------------------------------------------------------


class TestGetRowCountPerformance:
    def test_1000_rows_count_under_500ms(self, generator_factory, tmp_xml):
        xml_path = tmp_xml(LARGE_XML)
        g = generator_factory(xml_path)
        start = time.perf_counter()
        count = g.get_row_count()
        elapsed = time.perf_counter() - start
        assert count == 1000
        assert elapsed < 0.5, f"get_row_count(1000) took {elapsed:.4f}s"


@pytest.mark.benchmark(group="row_count")
def test_benchmark_get_row_count_1000(benchmark, generator_factory, tmp_xml):
    xml_path = tmp_xml(LARGE_XML)
    g = generator_factory(xml_path)
    benchmark(g.get_row_count)


# ---------------------------------------------------------------------------
# Full run() benchmarks
# ---------------------------------------------------------------------------


class TestRunPerformance:
    def test_run_100_instruments_under_2s(self, generator_factory, tmp_xml, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        xml_path = tmp_xml(_make_xml_n(100))
        g = generator_factory(xml_path)
        start = time.perf_counter()
        g.run()
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, f"run() with 100 rows took {elapsed:.4f}s"

    def test_run_1000_instruments_under_10s(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        xml_path = tmp_xml(LARGE_XML)
        g = generator_factory(xml_path)
        start = time.perf_counter()
        g.run()
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"run() with 1000 rows took {elapsed:.4f}s"
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert sql.count("INSERT INTO") == 1000


@pytest.mark.benchmark(group="run")
def test_benchmark_run_100(benchmark, generator_factory, tmp_xml, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    xml_path = tmp_xml(_make_xml_n(100))

    def _run():
        g = generator_factory(xml_path)
        g.run()

    benchmark(_run)


# ---------------------------------------------------------------------------
# SQL generation size regression
# ---------------------------------------------------------------------------


class TestSQLSizeRegression:
    def test_sql_file_not_empty_for_1000_rows(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        xml_path = tmp_xml(LARGE_XML)
        g = generator_factory(xml_path)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        # Each INSERT is substantial; 1000 inserts should produce > 500KB
        assert len(sql) > 500_000, f"Expected large SQL output, got {len(sql)} bytes"

    def test_sql_line_count_proportional_to_instruments(
        self, generator_factory, tmp_xml, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        xml_path = tmp_xml(_make_xml_n(10))
        g = generator_factory(xml_path)
        g.run()
        sql = (tmp_path / "sql_statements.sql").read_text()
        assert sql.count("INSERT INTO") == 10
