@echo off
echo Virgin Experience Voucher - Test Extraction Tool
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
pip install -r requirements.txt

echo.
echo Starting extraction test tool...
echo.

REM Run the simplified test extraction script
python test_extraction_simple.py

echo.
echo Test completed.
pause
