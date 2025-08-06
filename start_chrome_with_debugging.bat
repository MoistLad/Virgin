@echo off
echo Starting Chrome with remote debugging enabled...
echo.
echo This will close all existing Chrome windows and start a new one with remote debugging.
echo.
pause

taskkill /F /IM chrome.exe /T
timeout /t 2

echo.
echo Looking for Chrome installation...

set CHROME_PATH=

REM Try common Chrome installation paths
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
    goto :found
)

if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    goto :found
)

if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
    goto :found
)

REM Check user profile locations
for /d %%a in (%USERPROFILE%\AppData\Local\Google\Chrome\Application*) do (
    if exist "%%a\chrome.exe" (
        set CHROME_PATH="%%a\chrome.exe"
        goto :found
    )
)

echo Chrome not found in common locations. Please enter the path to chrome.exe:
set /p CHROME_PATH=

:found
echo Found Chrome at: %CHROME_PATH%
echo.
echo Starting Chrome with remote debugging on port 9222...
start "" %CHROME_PATH% --remote-debugging-port=9222 https://www.acornesvs.co.uk/vouchers/search.aspx

echo.
echo Chrome has been started with remote debugging enabled.
echo Please log in to the Virgin Experience Days website.
echo.
echo Once logged in, run the voucher automation script and enter 9222 as the debugging port.
echo.
pause
