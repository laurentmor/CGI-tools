# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
Unit tests for ProductClassResolver.py

Covers:
- ProductType enum membership and string values
- InstrumentClass enum membership and string values
- PRODUCT_TO_INSTRUMENT mapping completeness and correctness
- resolve_class() happy-path for every known product code
- resolve_class() edge cases: whitespace, mixed-case, unknown, empty
- Regression: BIL type added 2026-03-01
"""

from __future__ import annotations

import pytest

from hist_messages_generator.product_class_resolver import (
    PRODUCT_TO_INSTRUMENT,
    InstrumentClass,
    ProductType,
    resolve_class,
)

# ---------------------------------------------------------------------------
# ProductType enum
# ---------------------------------------------------------------------------


class TestProductTypeEnum:
    ALL_CODES = [
        "DLC",
        "SLC",
        "CAR",
        "RMB",
        "DBA",
        "CBA",
        "RBA",
        "DFP",
        "ADV",
        "LOI",
        "DCO",
        "DIR",
        "TAC",
        "GUA",
        "PBD",
        "PBS",
        "SBS",
        "FIN",
        "ATP",
        "OAP",
        "RPM",
        "SRM",
        "BIL",
    ]

    def test_all_expected_codes_present(self):
        for code in self.ALL_CODES:
            assert code in ProductType.__members__

    def test_str_value_equals_name(self):
        """StrEnum: str(member) == member.value == member name."""
        for member in ProductType:
            assert str(member) == member.value
            assert member.value == member.name

    def test_bil_regression(self):
        """BIL was added 2026-03-01; must be present."""
        assert ProductType.BIL == "BIL"

    def test_count(self):
        assert len(ProductType) == 23


# ---------------------------------------------------------------------------
# InstrumentClass enum
# ---------------------------------------------------------------------------


class TestInstrumentClassEnum:
    def test_all_members_are_lowercase_strings(self):
        for member in InstrumentClass:
            assert member.value == member.value.lower()

    def test_bil_class_regression(self):
        assert InstrumentClass.BIL == "billing_instrument"

    def test_letter_of_indemnity_typo_preserved(self):
        """Source contains 'idemnity' (not 'indemnity'): preserve for compatibility."""
        assert InstrumentClass.LETTER_OF_INDEMNITY == "letter_of_idemnity"

    def test_count(self):
        assert len(InstrumentClass) == 23


# ---------------------------------------------------------------------------
# PRODUCT_TO_INSTRUMENT mapping
# ---------------------------------------------------------------------------


class TestProductToInstrumentMapping:
    def test_every_product_type_has_mapping(self):
        for pt in ProductType:
            assert pt in PRODUCT_TO_INSTRUMENT, f"Missing mapping for {pt}"

    def test_every_mapped_value_is_instrument_class(self):
        for pt, ic in PRODUCT_TO_INSTRUMENT.items():
            assert isinstance(ic, InstrumentClass)

    def test_known_mappings(self):
        expected = {
            ProductType.DLC: InstrumentClass.DOCUMENTARY_LC,
            ProductType.SLC: InstrumentClass.STANDBY_LC,
            ProductType.GUA: InstrumentClass.GUARANTEE,
            ProductType.BIL: InstrumentClass.BIL,
            ProductType.FIN: InstrumentClass.FINANCE,
        }
        for pt, ic in expected.items():
            assert PRODUCT_TO_INSTRUMENT[pt] == ic

    def test_no_duplicate_values(self):
        values = list(PRODUCT_TO_INSTRUMENT.values())
        assert len(values) == len(set(values)), (
            "Each ProductType should map to a unique InstrumentClass"
        )


# ---------------------------------------------------------------------------
# resolve_class()
# ---------------------------------------------------------------------------


class TestResolveClass:
    @pytest.mark.parametrize("code", [pt.value for pt in ProductType])
    def test_all_product_types_resolve(self, code):
        result = resolve_class(code)
        assert isinstance(result, InstrumentClass)

    def test_resolve_dlc(self):
        assert resolve_class("DLC") == InstrumentClass.DOCUMENTARY_LC

    def test_resolve_slc(self):
        assert resolve_class("SLC") == InstrumentClass.STANDBY_LC

    def test_resolve_bil_regression(self):
        assert resolve_class("BIL") == InstrumentClass.BIL

    def test_resolve_strips_whitespace(self):
        assert resolve_class("  DLC  ") == InstrumentClass.DOCUMENTARY_LC

    def test_resolve_case_insensitive_lower(self):
        assert resolve_class("dlc") == InstrumentClass.DOCUMENTARY_LC

    def test_resolve_case_insensitive_mixed(self):
        assert resolve_class("Dlc") == InstrumentClass.DOCUMENTARY_LC

    def test_resolve_unknown_type_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid product type"):
            resolve_class("UNKNOWN")

    def test_resolve_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            resolve_class("")

    def test_resolve_whitespace_only_raises_value_error(self):
        with pytest.raises(ValueError):
            resolve_class("   ")

    def test_resolve_numeric_string_raises_value_error(self):
        with pytest.raises(ValueError):
            resolve_class("123")

    def test_return_type_is_str_enum(self):
        """InstrumentClass is a StrEnum; result must behave as a string."""
        result = resolve_class("DLC")
        assert isinstance(result, str)
        assert result == "documentary_lc"

    def test_resolve_all_return_values_are_non_empty(self):
        for pt in ProductType:
            ic = resolve_class(pt.value)
            assert ic  # truthy / non-empty
