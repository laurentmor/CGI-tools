@echo off
REM ============================================================
REM  run_tests.bat  --  run the full xml_extractor test suite
REM  Place this file in the same folder as xml_extractor.py
REM  and run it to execute all tests and view coverage reports. 
REM  Requires Python 3.11+ and pytest with coverage plugins.
REM  Usage:
REM    1. Ensure Python 3.11+ is installed and on PATH
REM    2. Run this script: run_tests.bat
REM    3. View results in console and coverage report in htmlcov\index.html 
REM    SPDX-License-Identifier: MIT
REM    SPDX-FileCopyrightText: 2026 Laurent Morissette

REM ============================================================

setlocal EnableDelayedExpansion

:: ── 1. Locate Python ─────────────────────────────────────────
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found on PATH.
    echo         Install Python 3.11+ from https://www.python.org
    echo         Ensure "Add Python to PATH" is checked during setup.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [INFO]  Using  !PY_VER!

:: ── 2. Install / verify test dependencies ────────────────────
echo [INFO]  Checking required packages...
python -m pip install --quiet pytest pytest-cov
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip install failed. Check your internet connection.
    pause & exit /b 1
)

:: ── 3. Run the test suite ─────────────────────────────────────
echo.
echo [INFO]  Running test suite...
echo ============================================================

python -m pytest tests\ ^
    --cov=hist_messages_generator ^
    --cov=decorators ^
    --cov-report=term-missing ^
    --cov-report=html:htmlcov ^
    -v ^
    --tb=short

set TEST_EXIT=%ERRORLEVEL%

:: ── 4. Report ─────────────────────────────────────────────────
echo.
echo ============================================================
if %TEST_EXIT% EQU 0 (
    echo [PASS]  All tests passed.
    echo [INFO]  Coverage report: htmlcov\index.html
) else (
    echo [FAIL]  Some tests failed. See output above.
)
echo ============================================================
echo.
pause
exit /b %TEST_EXIT%
