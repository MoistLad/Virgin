import csv
import re
import time
import os
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def extract_serial_pin(info_text):
    """
    Extract serial number and PIN from the info text in column C.
    
    Args:
        info_text (str): Text from column C containing serial and PIN
        
    Returns:
        tuple: (serial_number, pin) or (None, None) if extraction fails
    """
    # Remove any leading/trailing whitespace
    if not info_text:
        return None, None
        
    info_text = info_text.strip()
    
    # Try to extract serial and PIN using regex
    # Pattern looks for:
    # - Optional "Virgin" or "Virgin Exp" or "VirginEXP" prefix (case insensitive)
    # - Serial number: 7-9 characters (letters and numbers)
    # - Followed by space(s) or other separators
    # - PIN: 4 characters (letters and numbers)
    pattern = r'(?:virgin\s*(?:exp|)|)?\s*([a-z0-9]{7,9})\s*(?:pin\s*)?([a-z0-9]{4})'
    match = re.search(pattern, info_text, re.IGNORECASE)
    
    if match:
        serial = match.group(1)
        pin = match.group(2)
        return serial, pin
    
    # If the standard pattern doesn't match, try a more flexible approach
    # Look for any sequence of 7-9 alphanumeric characters followed by 4 alphanumeric characters
    words = re.findall(r'[a-z0-9]+', info_text, re.IGNORECASE)
    for i in range(len(words) - 1):
        if 7 <= len(words[i]) <= 9 and len(words[i+1]) == 4:
            return words[i], words[i+1]
    
    # If we still can't find a match, check for any corrections in the text
    if "correct SN:" in info_text:
        # Extract the corrected serial number
        corrected_sn_match = re.search(r'correct SN:\s*([a-z0-9]{7,9})', info_text, re.IGNORECASE)
        if corrected_sn_match:
            corrected_sn = corrected_sn_match.group(1)
            # Try to find the PIN in the original text
            pin_match = re.search(r'([a-z0-9]{4})', info_text, re.IGNORECASE)
            if pin_match:
                return corrected_sn, pin_match.group(1)
    
    # If we still can't find a match, check for any corrections in the text for PIN
    if "correct PIN:" in info_text:
        # Extract the corrected PIN
        corrected_pin_match = re.search(r'correct PIN:\s*([a-z0-9]{4})', info_text, re.IGNORECASE)
        if corrected_pin_match:
            corrected_pin = corrected_pin_match.group(1)
            # Try to find the serial in the original text
            serial_match = re.search(r'([a-z0-9]{7,9})', info_text, re.IGNORECASE)
            if serial_match:
                return serial_match.group(1), corrected_pin
    
    # If all attempts fail, return None for both
    return None, None

def process_voucher(driver, serial, pin):
    """
    Process a single voucher by inputting serial and PIN, clicking search,
    and handling the resulting page.
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        serial (str): Serial number to input
        pin (str): PIN to input
        
    Returns:
        bool: True if voucher was successfully claimed, False otherwise
    """
    try:
        # Wait for the page to be ready
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_cphMain_tbxSerialNo"))
        )
        
        # Clear and input serial number
        serial_input = driver.find_element(By.ID, "ctl00_cphMain_tbxSerialNo")
        serial_input.clear()
        serial_input.send_keys(serial)
        
        # Clear and input PIN
        pin_input = driver.find_element(By.ID, "ctl00_cphMain_tbxPinNo")
        pin_input.clear()
        pin_input.send_keys(pin)
        
        # Click search button
        search_button = driver.find_element(By.ID, "ctl00_cphMain_btnLookup")
        search_button.click()
        
        # Wait for the page to load
        time.sleep(2)
        
        # First, check for error message on the same page (invalid serial/PIN)
        try:
            # Look for the error message div
            error_message_xpath = "/html/body/div[1]/form/div[5]/div[1]/div[1]/div"
            error_message = driver.find_elements(By.XPATH, error_message_xpath)
            
            if error_message and "error msg-block" in error_message[0].get_attribute("class"):
                print(f"Error message detected for {serial} {pin}: Invalid serial/PIN")
                
                # Clear the input fields for the next voucher
                serial_input = driver.find_element(By.ID, "ctl00_cphMain_tbxSerialNo")
                serial_input.clear()
                
                pin_input = driver.find_element(By.ID, "ctl00_cphMain_tbxPinNo")
                pin_input.clear()
                
                return False  # Error case
        except (TimeoutException, NoSuchElementException):
            # No error message found, continue with other checks
            pass
        
        # Check which page we're on by looking for specific elements
        try:
            # Check if we're on the claim page (error page)
            # This is the page where a button is found at the specified XPath
            error_button_xpath = "/html/body/div[1]/form/div[5]/div/div[2]/fieldset/table/tbody/tr[13]/td[1]/input"
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, error_button_xpath))
            )
            print(f"Error page detected for {serial} {pin}")
            
            # Click the abandon button
            abandon_button_xpath = "/html/body/div[1]/form/div[5]/div/div[2]/fieldset/table/tbody/tr[13]/td[1]/a"
            abandon_button = driver.find_element(By.XPATH, abandon_button_xpath)
            abandon_button.click()
            
            # Wait for navigation back to main page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctl00_cphMain_tbxSerialNo"))
            )
            
            return False  # Error case
            
        except (TimeoutException, NoSuchElementException):
            try:
                # Check if we're on the correct page (success page)
                # This is the page where only the abandon button is present
                success_button_xpath = "/html/body/div[1]/form/div[5]/div/div[2]/fieldset/table/tbody/tr[12]/td[1]/a"
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, success_button_xpath))
                )
                print(f"Success page detected for {serial} {pin}")
                
                # Click the abandon button
                abandon_button = driver.find_element(By.XPATH, success_button_xpath)
                abandon_button.click()
                
                # Wait for navigation back to main page
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ctl00_cphMain_tbxSerialNo"))
                )
                
                return True  # Success case
                
            except (TimeoutException, NoSuchElementException):
                # If we can't determine the page, try a more generic approach
                try:
                    # Look for any abandon button
                    abandon_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Abandon')]")
                    if abandon_buttons:
                        print(f"Found generic abandon button for {serial} {pin}")
                        abandon_buttons[0].click()
                        
                        # Wait for navigation back to main page
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "ctl00_cphMain_tbxSerialNo"))
                        )
                        
                        # Assume error since we couldn't determine specifically
                        return False
                    else:
                        print(f"No abandon button found for {serial} {pin}")
                        # Try to navigate back to the search page
                        driver.get("https://www.acornesvs.co.uk/vouchers/search.aspx")
                        return False
                except Exception as e:
                    print(f"Error finding abandon button: {str(e)}")
                    # Try to navigate back to the search page
                    driver.get("https://www.acornesvs.co.uk/vouchers/search.aspx")
                    return False
    except Exception as e:
        print(f"Error processing voucher {serial} {pin}: {str(e)}")
        # Try to navigate back to the search page
        try:
            driver.get("https://www.acornesvs.co.uk/vouchers/search.aspx")
        except:
            pass
        return False

def read_csv_file(file_path):
    """
    Read the CSV file and return the data as a list of dictionaries.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        list: List of dictionaries representing rows in the CSV
    """
    # Remove any quotes from the file path
    file_path = file_path.strip('"\'')
    
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        # Try with different encodings if utf-8-sig fails
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            return data
        except Exception as e2:
            print(f"Also tried with utf-8 encoding: {str(e2)}")
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        data.append(row)
                return data
            except Exception as e3:
                print(f"Also tried with latin-1 encoding: {str(e3)}")
                return []

def write_results_csv(input_file, results):
    """
    Write the results to a new CSV file.
    
    Args:
        input_file (str): Path to the input CSV file
        results (list): List of dictionaries with results
        
    Returns:
        str: Path to the output CSV file
    """
    try:
        # Clean up the input file path - remove quotes and normalize
        input_file = input_file.strip('"\'')
        
        # Get just the filename without the path
        input_filename = os.path.basename(input_file)
        
        # Generate output file name in the current directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.splitext(input_filename)[0] + f"_results_{timestamp}.csv"
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
        
        print(f"Preparing to write results to: {output_file}")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            # Get all field names from the first result
            if results:
                fieldnames = list(results[0].keys())
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        
        print(f"Results saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error writing results CSV: {str(e)}")
        print("Attempting to write to current directory instead...")
        
        try:
            # Fallback to a simple filename in the current directory
            output_file = f"voucher_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                if results:
                    fieldnames = list(results[0].keys())
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)
            
            print(f"Results saved to {output_file}")
            return output_file
        except Exception as e2:
            print(f"Error in fallback CSV writing: {str(e2)}")
            return None

def generate_html_report(results, output_file):
    """
    Generate an HTML report with color-coded results.
    
    Args:
        results (list): List of dictionaries with results
        output_file (str): Path to the output CSV file
        
    Returns:
        str: Path to the HTML report
    """
    try:
        # Generate HTML file name from the CSV file
        html_file = os.path.splitext(output_file)[0] + ".html"
        print(f"Preparing to generate HTML report: {html_file}")
        
        with open(html_file, 'w', encoding='utf-8') as file:
            # Write HTML header
            file.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Voucher Processing Results</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                    .success { background-color: #dff0d8; color: #3c763d; }
                    .error { background-color: #f2dede; color: #a94442; }
                    .header { margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Voucher Processing Results</h1>
                    <p>Generated on: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                </div>
                <table>
                    <tr>
            """)
            
            # Write table headers
            if results:
                for key in results[0].keys():
                    file.write(f"<th>{key}</th>")
                file.write("</tr>")
                
                # Write table rows
                for row in results:
                    if row.get('Result') == 'Claimed':
                        file.write('<tr class="success">')
                    else:
                        file.write('<tr class="error">')
                    
                    for key, value in row.items():
                        file.write(f"<td>{value}</td>")
                    
                    file.write("</tr>")
            
            # Write HTML footer
            file.write("""
                </table>
            </body>
            </html>
            """)
        
        print(f"HTML report generated: {html_file}")
        return html_file
    except Exception as e:
        print(f"Error generating HTML report: {str(e)}")
        print("Attempting to write HTML report to current directory instead...")
        
        try:
            # Fallback to a simple filename in the current directory
            html_file = f"voucher_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            with open(html_file, 'w', encoding='utf-8') as file:
                # Write HTML header
                file.write("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Voucher Processing Results</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                        tr:nth-child(even) { background-color: #f9f9f9; }
                        .success { background-color: #dff0d8; color: #3c763d; }
                        .error { background-color: #f2dede; color: #a94442; }
                        .header { margin-bottom: 20px; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Voucher Processing Results</h1>
                        <p>Generated on: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                    </div>
                    <table>
                        <tr>
                """)
                
                # Write table headers
                if results:
                    for key in results[0].keys():
                        file.write(f"<th>{key}</th>")
                    file.write("</tr>")
                    
                    # Write table rows
                    for row in results:
                        if row.get('Result') == 'Claimed':
                            file.write('<tr class="success">')
                        else:
                            file.write('<tr class="error">')
                        
                        for key, value in row.items():
                            file.write(f"<td>{value}</td>")
                        
                        file.write("</tr>")
                
                # Write HTML footer
                file.write("""
                    </table>
                </body>
                </html>
                """)
            
            print(f"HTML report generated: {html_file}")
            return html_file
        except Exception as e2:
            print(f"Error in fallback HTML report generation: {str(e2)}")
            return None

def main():
    """
    Main function to run the voucher automation process.
    """
    # Get the CSV file path from the user
    csv_file = input("Enter the path to the CSV file (default: P6 VExperience 22.02-10.03.25.csv): ")
    if not csv_file:
        csv_file = "P6 VExperience 22.02-10.03.25.csv"
    
    # Print the file path for debugging
    print(f"Using file path: {csv_file}")
    
    try:
        # Read the CSV file
        print(f"Reading CSV file: {csv_file}")
        data = read_csv_file(csv_file)
        
        if not data:
            print("No data found in the CSV file or file could not be read.")
            return
        
        print(f"Found {len(data)} rows in the CSV file.")
        
        # Launch a new Chrome session directly
        print("\n=== LAUNCHING NEW CHROME SESSION ===")
        print("The script will start a new Chrome browser.\n")
        
        # Set up Chrome options
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        
        # Add some options to make Chrome more stable
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            # Use the ChromeDriver in the current directory
            from selenium.webdriver.chrome.service import Service
            chrome_driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver.exe")
            print(f"Using ChromeDriver at: {chrome_driver_path}")
            
            # Create a Service object
            service = Service(executable_path=chrome_driver_path)
            
            # Initialize Chrome with the service and options
            print("Initializing Chrome...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Navigate to the website
            print("Navigating to the Acorne SVS website...")
            driver.get("https://www.acornesvs.co.uk/vouchers/search.aspx")
            
            # Check if we're connected
            current_url = driver.current_url
            print(f"Successfully connected to Chrome! Current URL: {current_url}")
            
        except Exception as e:
            print(f"\nError launching Chrome: {str(e)}")
            print("\nDetailed error information:")
            import traceback
            traceback.print_exc()
            print("\nExiting...")
            return
        
        print("Please log in to the website if needed.")
        input("Press Enter once you are logged in and on the voucher search page...")
        
        # Process each row
        results = []
        for idx, row in enumerate(data):
            # Check if the row is completely empty or has no meaningful data
            is_empty_row = True
            for key, value in row.items():
                if value and value.strip():
                    is_empty_row = False
                    break
            
            # If we encounter a completely empty row, stop processing
            if is_empty_row:
                print(f"Encountered empty row at {idx+2}. Stopping processing.")
                break
            
            # Get the info text from the Info column
            info_text = row.get('Info', '')
            
            # Skip rows that are already processed (have "Claimed" in Status column)
            if row.get('Satus') == 'Claimed':
                print(f"Skipping already claimed voucher at row {idx+2}")
                
                # Add to results with existing status
                result_row = row.copy()
                result_row['Result'] = 'Claimed'
                results.append(result_row)
                continue
            
            # Extract serial and PIN from the Info column
            serial, pin = extract_serial_pin(info_text)
            
            if serial and pin:
                print(f"Processing row {idx+2}: Serial={serial}, PIN={pin}")
                
                # Process the voucher
                success = process_voucher(driver, serial, pin)
                
                # Create result row
                result_row = row.copy()
                if success:
                    result_row['Result'] = 'Claimed'
                else:
                    result_row['Result'] = 'Error'
                
                # Add to results
                results.append(result_row)
                
                # Wait a bit between vouchers to avoid overwhelming the site
                time.sleep(1)
            else:
                # If the Info column is empty or contains only whitespace, consider it an empty row
                if not info_text or not info_text.strip():
                    print(f"Encountered row with empty Info column at {idx+2}. Stopping processing.")
                    break
                
                print(f"Could not extract serial and PIN from row {idx+2}: {info_text}")
                
                # Add to results with error
                result_row = row.copy()
                result_row['Result'] = 'Error - Could not extract serial and PIN'
                results.append(result_row)
        
        # Close the browser
        driver.quit()
        
        # Write results to CSV
        output_file = write_results_csv(csv_file, results)
        
        # Generate HTML report
        if output_file:
            html_file = generate_html_report(results, output_file)
            if html_file:
                print(f"\nResults have been saved to:")
                print(f"1. CSV file: {output_file}")
                print(f"2. HTML report: {html_file}")
                
                # Try to open the HTML report
                try:
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(html_file)}")
                    print("HTML report has been opened in your default browser.")
                except:
                    print("Could not automatically open the HTML report. Please open it manually.")
        
        print("\nVoucher automation completed successfully!")
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()
