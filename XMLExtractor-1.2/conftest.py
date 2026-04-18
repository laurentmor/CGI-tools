# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
conftest.py
===========
Executed by pytest *before* any test module is imported, which means
pytest-cov has already started its tracer by the time xml_extractor is
first imported.  Registering all dependency stubs here (instead of at the
top of the test file) is what allows coverage to instrument the module
under test properly.

Without this file:
  1. test files register stubs + import xml_extractor at *collection* time,
     before pytest-cov's tracer is active.
  2. coverage never sees the module loaded → "no data collected".

With this file:
  pytest-cov starts → conftest.py runs (stubs registered) → test modules
  collected (xml_extractor imported under the live tracer) → coverage works.

tests package vs tests.generate_test_sets stub
-----------------------------------------------
xml_extractor imports `from tests.generate_test_sets import generate` at
module level.  We need to stub that sub-module so the import doesn't fail.

However, we also have a real tests/ package (our split test suite).  A plain
  sys.modules["tests"] = types.ModuleType("tests")
would shadow the real package, making `from tests.fixtures import ...` fail.

Fix: load the real tests/ package explicitly via importlib, then register
the generate_test_sets stub *under* it.
"""

import importlib.util as _ilu
import pathlib as _pathlib
import sys
import types
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# winsound  -- Windows-only; not present on Linux/macOS/CI
# ---------------------------------------------------------------------------
if "winsound" not in sys.modules:
    _winsound = types.ModuleType("winsound")
    _winsound.PlaySound = MagicMock()
    _winsound.SND_FILENAME = 0
    sys.modules["winsound"] = _winsound

# ---------------------------------------------------------------------------
# pyzipper  -- optional AES-zip library; may not be installed in CI
# ---------------------------------------------------------------------------
if "pyzipper" not in sys.modules:
    _pyzipper = types.ModuleType("pyzipper")
    _pyzipper.AESZipFile = MagicMock()
    _pyzipper.WZ_AES = "WZ_AES"
    sys.modules["pyzipper"] = _pyzipper

# ---------------------------------------------------------------------------
# tests  -- load the real tests/ package so that tests.fixtures and every
#            tests.test_* module resolve correctly.
#            Then stub only tests.generate_test_sets (the sub-module that
#            xml_extractor imports at module level).
# ---------------------------------------------------------------------------
if "tests" not in sys.modules:
    _conftest_dir = _pathlib.Path(__file__).parent
    _tests_init = _conftest_dir / "tests" / "__init__.py"
    _tests_dir = str(_tests_init.parent)

    _spec = _ilu.spec_from_file_location(
        "tests",
        str(_tests_init),
        submodule_search_locations=[_tests_dir],
    )
    _pkg = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_pkg)
    sys.modules["tests"] = _pkg

if "tests.generate_test_sets" not in sys.modules:
    _tsg = types.ModuleType("tests.generate_test_sets")
    _tsg.generate = MagicMock()
    sys.modules["tests.generate_test_sets"] = _tsg

# ---------------------------------------------------------------------------
# decorators  -- no-op stub so xml_extractor can be imported without the real
#                decorators.py being on the path.  Individual test classes load
#                the real decorators.py explicitly via importlib when they need
#                to test actual decorator behaviour.
# ---------------------------------------------------------------------------
if "decorators" not in sys.modules:
    _dec = types.ModuleType("decorators")

    def _noop_log_exceptions(*args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    _dec.log_exceptions = _noop_log_exceptions
    sys.modules["decorators"] = _dec
