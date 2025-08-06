@echo off
echo Virgin Experience Voucher Automation
echo ===================================
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
echo Downloading the correct ChromeDriver version...
echo.

REM Create a temporary directory for the download
mkdir temp_download 2>nul
cd temp_download

echo Downloading ChromeDriver version 139.0.7258.67...
echo.

REM Download the ChromeDriver zip file
curl -L -o chromedriver_win32.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.67/win64/chromedriver-win64.zip

echo.
echo Extracting ChromeDriver...
echo.

REM Extract the zip file
powershell -command "Expand-Archive -Force 'chromedriver_win32.zip' '.'"

echo.
echo Copying ChromeDriver to the main directory...
echo.

REM Copy the chromedriver.exe to the parent directory
copy /Y chromedriver-win64\chromedriver.exe ..\chromedriver.exe

echo.
echo Cleaning up...
echo.

REM Clean up the temporary directory
cd ..
rmdir /S /Q temp_download

echo.
echo ChromeDriver has been updated to version 139.
echo.

REM Update Selenium to the latest version
echo Updating Selenium to the latest version...
pip install --upgrade selenium

echo.
echo Starting voucher automation...
echo.
echo NOTE: The script will launch a new Chrome window.
echo You will need to log in to the website when prompted.
echo.

REM Run the simplified voucher automation script
python voucher_automation_simple.py

echo.
echo Script execution completed.
pause
