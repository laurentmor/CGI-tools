# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
fixtures.py
===========
Shared constants, XML payloads, and helper functions used across all
test modules.  Import from here rather than duplicating in each file.
"""

import importlib.util as _ilu
import io
import pathlib as _pathlib
from contextlib import contextmanager
from unittest.mock import patch
from xml.etree import ElementTree as ET

import xml_extractor as xe

# ---------------------------------------------------------------------------
# XML payloads
# ---------------------------------------------------------------------------

SINGLE_ROW_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>MSG001</MessageID></Header></Proponix>]]></COLUMN>
  </ROW>
</RESULTS>"""

MULTI_ROW_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>MSG001</MessageID></Header></Proponix>]]></COLUMN>
  </ROW>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>MSG002</MessageID></Header></Proponix>]]></COLUMN>
  </ROW>
  <ROW>
    <COLUMN NAME="RICH_TEXT_NCLOB"><![CDATA[<Proponix><Header><MessageID>MSG003</MessageID></Header></Proponix>]]></COLUMN>
  </ROW>
</RESULTS>"""

MISSING_COLUMN_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS>
  <ROW>
    <COLUMN NAME="OTHER_COL"><![CDATA[data]]></COLUMN>
  </ROW>
</RESULTS>"""

WRONG_ROOT_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<NOT_RESULTS>
  <ROW/>
</NOT_RESULTS>"""

EMPTY_RESULTS_XML = """\
<?xml version='1.0' encoding='UTF8'?>
<RESULTS/>"""

INVALID_XML = "<<not xml at all>>"

DIRTY_XML_CONTENT = "Hello\x02World\x1AEnd"

REPLACE_MAP = {"*": "-", "\x02": "", "\x1A": ""}

# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------

def make_extractor(**overrides):
    """Return an XMLExtractor with safe defaults; no filesystem access needed."""
    defaults = dict(
        input_file="input.xml",
        output_dir="output",
        output_file_name="archive",
        column_name="RICH_TEXT_NCLOB",
        create_zip=False,
        zip_password=None,
        file_id_tag="MessageID",
        mute=True,
        dry_run=False,
    )
    defaults.update(overrides)
    return xe.XMLExtractor(**defaults)


# ---------------------------------------------------------------------------
# iterparse patch helper
# ---------------------------------------------------------------------------

@contextmanager
def patch_iterparse(xml_string: str):
    """Replace ET.iterparse so it parses *xml_string* instead of a real file.

    The real ET.iterparse is captured *before* patching so the fake can call
    it without triggering infinite recursion through the mock.
    """
    _real_iterparse = ET.iterparse

    def fake_iterparse(source, events=None):
        return _real_iterparse(
            io.BytesIO(xml_string.encode()),
            events=events or ("end",)
        )

    with patch("xml_extractor.ET.iterparse", side_effect=fake_iterparse):
        yield


# ---------------------------------------------------------------------------
# Real log_exceptions loader
# ---------------------------------------------------------------------------

def load_real_log_exceptions():
    """Load and return log_exceptions from decorators.py.

    Searches in order:
      1. Same directory as this fixtures.py  (project root if tests/ is a
         sub-package, or wherever decorators.py lives alongside the tests).
      2. Parent directory of tests/  (most common layout: decorators.py sits
         next to xml_extractor.py at the project root).
    """
    candidates = [
        _pathlib.Path(__file__).parent / "decorators.py",           # tests/decorators.py
        _pathlib.Path(__file__).parent.parent / "decorators.py",    # project_root/decorators.py
    ]
    for path in candidates:
        if path.exists():
            _spec = _ilu.spec_from_file_location("_dec_real", str(path))
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            return _mod.log_exceptions

    raise FileNotFoundError(
        "decorators.py not found in any of: "
        + ", ".join(str(p) for p in candidates)
    )
