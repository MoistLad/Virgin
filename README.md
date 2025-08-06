# Virgin Experience Voucher Automation

This project automates the process of inputting voucher data from a CSV spreadsheet into the Virgin Experience Days website. It extracts serial numbers and PINs from the spreadsheet, inputs them into the website, and creates a report of the results.

## Features

- Connects to an existing Chrome session (no need to handle login)
- Extracts serial numbers and PINs from spreadsheet data
- Automates browser interaction to input data into the website
- Handles different page outcomes (success or error)
- Creates a results CSV file and HTML report with color-coded results
- Supports various formats of serial numbers and PINs in the input data

## Requirements

- Python 3.7 or higher
- Chrome browser
- ChromeDriver (included in the project)

## Installation

1. Install the required Python package:

```bash
pip install selenium==4.10.0
```

2. The ChromeDriver is already included in the project directory.

## Usage

### Quick Start (Windows)

1. First, start Chrome with remote debugging enabled:
   - Double-click on **start_chrome_with_debugging.bat**
   - This will close all existing Chrome windows and start a new one with remote debugging enabled
   - Log in to the Virgin Experience Days website

2. Then run one of these batch files:
   - **run_voucher_automation.bat** - Runs the main automation script
   - **run_test_extraction.bat** - Runs the extraction test tool

### Manual Execution

#### Voucher Automation Script

Run the main automation script:

```bash
python voucher_automation_simple.py
```

#### Test Extraction Tool

Run the extraction test tool to verify serial/PIN extraction:

```bash
python test_extraction_simple.py
```

When running the automation script:

1. You'll be prompted to enter the path to your CSV file (or press Enter to use the default)
2. You'll be asked to enter the Chrome debugging port (default is 9222)
3. The script will connect to your existing Chrome session
4. Once connected, press Enter to start the automation
5. The script will process each row in the spreadsheet
6. Results will be saved to a new CSV file and an HTML report will be generated

## CSV Format

The script expects a CSV file with the following columns:
- Column C (Info): Contains the voucher information, including serial number and PIN
- Column D (Satus): Used to check if a voucher is already claimed

The script will generate a new CSV file with all the original columns plus:
- Result: Will contain "Claimed" for success or "Error" for failures

Example of valid formats in the Info column:
- "Virgin Exp E10571580 2YP8"
- "Virgin E9448035 BQT7"
- "E10571580 2YP8"
- "8410188 7TNA"

## Troubleshooting

- If the script fails to extract serial numbers and PINs, check the format in your spreadsheet
- If the browser automation fails, ensure you're logged in and on the correct page
- Check the console output for error messages

## Notes

- The script will skip rows that already have "Claimed" in the Satus column
- The script generates an HTML report that will automatically open in your browser
- The HTML report provides a color-coded view of the results (green for success, red for errors)
- The script includes error handling to recover from most issues
