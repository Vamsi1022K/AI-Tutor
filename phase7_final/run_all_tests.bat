@echo off
REM =====================================================================
REM  AI COMPILER TUTOR — Complete Demo Script (Windows)
REM  Week 14 Deliverable: run_all_tests.bat
REM  Phase 7: Final Integration and Submission
REM
REM  Usage: Double-click this file OR run from Command Prompt:
REM    cd "cd ag"
REM    phase7_final\run_all_tests.bat
REM =====================================================================

title AI Compiler Tutor — Demo Run
color 0A

echo.
echo ======================================================================
echo   🤖  AI-BASED COMPILER ERROR MESSAGE REWRITING  —  DEMO
echo   Project: AI Compiler Tutor    Sem 4 - Compiler Design
echo ======================================================================
echo.
echo   This demo runs the AI Tutor on all 10 intentional C error programs
echo   and shows how each GCC error is rewritten in plain English.
echo.
echo   Requirements:
echo     [1] Python 3.7+ must be installed
echo     [2] GCC must be installed (MinGW-w64) and on PATH
echo.

REM ── Check Python ──────────────────────────────────────────────────────
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

REM ── Check GCC ─────────────────────────────────────────────────────────
gcc --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] GCC not found. Install MinGW-w64 and add gcc.exe to PATH.
    pause
    exit /b 1
)

echo   ✅ Python found.
echo   ✅ GCC found.
echo.
echo ======================================================================
echo   Starting tests...  Press any key to begin.
echo ======================================================================
pause > nul

SET PASS=0
SET FAIL=0
SET REWRITER=phase5_ai_rewriting\rewriter.py
SET ERRORS_DIR=errors

REM ── TEST 1 ────────────────────────────────────────────────────────────
echo.
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 1: Missing Semicolon  (E001 - Syntax Error)               │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_001_missing_semicolon.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 2 ────────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 2: Undeclared Variable  (E002 - Declaration Error)         │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_002_undeclared_variable.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 3 ────────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 3: Incompatible Types  (E003 - Type Error)                 │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_003_incompatible_types.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 4 ────────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 4: Implicit Function Declaration  (E004 - Declaration)     │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_004_implicit_declaration.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 5 ────────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 5: Missing Parenthesis  (E005 - Syntax Error)              │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_005_missing_paren.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 6 ────────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 6: Too Few Arguments  (E006 - Syntax Error)                │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_006_too_few_args.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 7 ────────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 7: Variable Redefinition  (E009 - Declaration Error)       │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_007_redefinition.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 8 ────────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 8: Void Function Returns Value  (E010 - Scope Error)       │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_008_void_return.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 9 ────────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 9: Format Specifier Mismatch  (E011 - Type Error)          │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_009_format_mismatch.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.
pause > nul

REM ── TEST 10 ───────────────────────────────────────────────────────────
echo ┌─────────────────────────────────────────────────────────────────┐
echo │  TEST 10: Missing Closing Brace  (E015 - Syntax Error)           │
echo └─────────────────────────────────────────────────────────────────┘
python %REWRITER% %ERRORS_DIR%\err_010_missing_brace.c
IF ERRORLEVEL 0 (SET /A PASS+=1) ELSE (SET /A FAIL+=1)
echo.

REM ── FINAL RESULTS ─────────────────────────────────────────────────────
echo.
echo ======================================================================
echo   DEMO COMPLETE — FINAL RESULTS
echo ======================================================================
echo.
echo   Total Tests  : 10
echo   ✅ Passed    : %PASS%
echo   ❌ Failed    : %FAIL%
echo.
IF %FAIL%==0 (
    echo   🎉 ALL TESTS PASSED! The AI Compiler Tutor is working correctly.
) ELSE (
    echo   ⚠️  Some tests failed. Check GCC is installed and on PATH.
)
echo.
echo   Deliverables:
echo     📂 phase5_ai_rewriting\rewriter.py   — Main AI Tutor program
echo     📂 phase4_dataset\annotated_errors.json — Error dataset
echo     📂 errors\                             — 10 test C programs
echo     📂 phase1_understanding\ through phase7_final\ — All docs
echo.
echo ======================================================================
pause
