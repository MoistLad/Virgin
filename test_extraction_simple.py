import re
import csv
import sys

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

def test_extraction():
    """
    Test the extraction function with various formats.
    """
    test_cases = [
        "Virgin Exp E10571580 2YP8",
        "Virgin E9448035 BQT7",
        "VirginEXP E9259699 XWWW",
        "E10571580 2YP8",
        "8410188 7TNA",
        "Virgin Exp E921164 8XLX,correct SN: E9921164",
        "Virgin Exp E1058064 QG62,correct SN: E10580645",
        "Virgin EXP E10552021 KMJH,correct PIN:XWWV",
        "Virgin Exp E10217887 DQF4,correct SN: E10327887",
        "Virgin EXP E9680313 PIN YWUT",
        "E RYLJ",  # This should fail
    ]
    
    print("Testing extraction with sample data:")
    for i, test in enumerate(test_cases):
        serial, pin = extract_serial_pin(test)
        if serial and pin:
            print(f"{i+1}. SUCCESS - Input: '{test}'")
            print(f"   Serial: {serial}, PIN: {pin}")
        else:
            print(f"{i+1}. FAILED - Input: '{test}'")
    
    print("\n")

def test_with_csv(csv_file):
    """
    Test the extraction function with actual CSV data.
    
    Args:
        csv_file (str): Path to the CSV file
    """
    # Remove any quotes from the file path
    csv_file = csv_file.strip('"\'')
    
    try:
        # Read the CSV file
        data = []
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except Exception as e:
            print(f"Error with utf-8-sig encoding: {str(e)}")
            try:
                with open(csv_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        data.append(row)
            except Exception as e2:
                print(f"Error with utf-8 encoding: {str(e2)}")
                with open(csv_file, 'r', encoding='latin-1') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        data.append(row)
        
        print(f"Testing extraction with CSV data from {csv_file}:")
        
        success_count = 0
        fail_count = 0
        
        for idx, row in enumerate(data):
            # Extract info text from the Info column
            info_text = row.get('Info', '')
            if not info_text:
                continue
                
            serial, pin = extract_serial_pin(info_text)
            
            if serial and pin:
                print(f"{idx+2}. SUCCESS - Input: '{info_text}'")
                print(f"   Serial: {serial}, PIN: {pin}")
                success_count += 1
            else:
                print(f"{idx+2}. FAILED - Input: '{info_text}'")
                fail_count += 1
        
        total = success_count + fail_count
        success_rate = (success_count / total) * 100 if total > 0 else 0
        
        print(f"\nSummary:")
        print(f"Total rows processed: {total}")
        print(f"Successful extractions: {success_count}")
        print(f"Failed extractions: {fail_count}")
        print(f"Success rate: {success_rate:.2f}%")
        
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")

def main():
    """
    Main function to run the tests.
    """
    # Test with sample data
    test_extraction()
    
    # Test with actual CSV data
    csv_file = input("Enter the path to the CSV file (or press Enter to skip CSV testing): ")
    if csv_file:
        test_with_csv(csv_file)
    
    print("\nTesting completed!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
