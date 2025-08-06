# Virgin Experience Voucher Automation

This project automates the process of inputting voucher data from a CSV spreadsheet into the Virgin Experience Days website. It extracts serial numbers and PINs from the spreadsheet, inputs them into the website, and creates a report of the results.

## Features

- Automatically launches Chrome and navigates to the website
- Extracts serial numbers and PINs from spreadsheet data
- Automates browser interaction to input data into the website
- Handles different page outcomes (success or error)
- Creates a results CSV file and HTML report with color-coded results
- Supports various formats of serial numbers and PINs in the input data
- Robust file path handling for input and output files

## Requirements

- Python 3.7 or higher
- Chrome browser

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. The script will automatically download the correct ChromeDriver version for your Chrome browser.

## Usage

### Quick Start (Windows)

Run the batch file:
- **run_voucher_automation.bat** - Downloads the correct ChromeDriver, updates dependencies, and runs the main automation script

### Manual Execution

Run the main automation script:

```bash
python voucher_automation_simple.py
```

When running the automation script:

1. You'll be prompted to enter the path to your CSV file (or press Enter to use the default)
2. The script will launch Chrome and navigate to the website
3. Log in to the website when prompted
4. Press Enter to start the automation
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
- If there are issues with file paths, the script will attempt to save results to the local directory

## Notes

- The script will skip rows that already have "Claimed" in the Satus column
- The script will automatically stop processing when it encounters a completely blank row
- The script generates an HTML report that will automatically open in your browser
- The HTML report provides a color-coded view of the results (green for success, red for errors)
- The script includes error handling to recover from most issues
- Results are always saved to the local directory to avoid path-related issues
