import re
from datetime import datetime
from paddleocr import PaddleOCR

def extract_text(image_path):
    """
    Extracts text from an image using PaddleOCR.
    Returns a list of extracted text lines.
    """
    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    # Perform OCR on the image
    result = ocr.ocr(image_path, cls=True)
    extracted_text = []
    for line in result:
        for word in line:
            extracted_text.append(word[1][0])  # Append the detected text
    return extracted_text

def convert_to_yyyy_mm_dd(date_str):
    """
    Converts a date string into YYYY-MM-DD format.
    Supports multiple formats like DD/MM/YYYY, DD-MM-YYYY, DDMMYYYY, DD/MM/YY, CB+DDMMYY, DD.MM.YYYY, EDD/MM/YYYY, CB DD.MM.YY, and CB DD MM YY.
    """
    # Remove any non-alphanumeric characters (e.g., 'CB' or 'E' prefix)
    cleaned_date_str = re.sub(r'[^0-9]', '', date_str)

    # Handle short year format (e.g., 21/05/25 or CB210525)
    if len(cleaned_date_str) == 6:
        # Assume the format is DDMMYY
        day = cleaned_date_str[:2]
        month = cleaned_date_str[2:4]
        year = cleaned_date_str[4:6]
        # Convert YY to YYYY (assuming 20XX)
        year = f"20{year}"
        return f"{year}-{month}-{day}"

    # Handle other formats
    date_formats = [
        "%d/%m/%Y",  # DD/MM/YYYY
        "%Y-%m-%d",  # YYYY-MM-DD
        "%d-%m-%Y",  # DD-MM-YYYY
        "%d%m%Y",    # DDMMYYYY
        "%d/%m/%y",  # DD/MM/YY (short year)
        "%d.%m.%Y",  # DD.MM.YYYY (period separator)
        "%d.%m.%y",  # DD.MM.YY (short year with period separator)
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")  # Convert to YYYY-MM-DD
        except ValueError:
            continue  # Try the next format if parsing fails

    # Handle the 'EDD/MM/YYYY' format
    if date_str.startswith('E') and len(date_str) >= 10:
        try:
            # Extract the date part (DD/MM/YYYY) after the 'E' prefix
            date_part = date_str[1:11]  # Extract '09/11/2025' from 'E09/11/202519:35L3'
            return datetime.strptime(date_part, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            pass  # Ignore and return None if parsing fails

    # Handle the 'CB DD.MM.YY' format
    if date_str.startswith('CB') and len(date_str) >= 8:
        try:
            # Extract the date part (DD.MM.YY) after the 'CB' prefix
            date_part = date_str[2:10]  # Extract '01.03.25' from 'CB01.03.25'
            return datetime.strptime(date_part, "%d.%m.%y").strftime("%Y-%m-%d")
        except ValueError:
            pass  # Ignore and return None if parsing fails

    # Handle the 'CB DD MM YY' format
    if date_str.startswith('CB') and len(date_str) >= 8:
        try:
            # Extract the date part (DD MM YY) after the 'CB' prefix
            date_part = date_str[2:].replace(' ', '')  # Remove spaces and extract '020325' from 'CB 2 3 25'
            day = date_part[:2]
            month = date_part[2:4]
            year = date_part[4:6]
            # Convert YY to YYYY (assuming 20XX)
            year = f"20{year}"
            return f"{year}-{month}-{day}"
        except ValueError:
            pass  # Ignore and return None if parsing fails

    # Handle the 'EDD.MM.YY' format (e.g., 'E04.03.25M60:38')
    if date_str.startswith('E') and len(date_str) >= 8:
        try:
            # Extract the date part (DD.MM.YY) after the 'E' prefix
            date_part = date_str[1:9]  # Extract '04.03.25' from 'E04.03.25M60:38'
            return datetime.strptime(date_part, "%d.%m.%y").strftime("%Y-%m-%d")
        except ValueError:
            pass  # Ignore and return None if parsing fails

    return None  # Return None if no valid format is found

def extract_expiry_date(extracted_text):
    """
    Extracts the expiry date from the OCR result.
    Converts it to YYYY-MM-DD format before returning.
    """
    # Regular expression to match dates in various formats
    date_patterns = [
        r'\b(\d{2}/\d{2}/\d{4})\b',  # DD/MM/YYYY
        r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
        r'\b(\d{2}-\d{2}-\d{4})\b',  # DD-MM-YYYY
        r'\b(\d{2}\d{2}\d{4})\b',    # DDMMYYYY
        r'\b(\d{2}/\d{2}/\d{2})\b',  # DD/MM/YY (short year)
        r'\b(CB\d{6})\b',            # CB+DDMMYY
        r'\b(\d{2}\.\d{2}\.\d{4})\b',  # DD.MM.YYYY (period separator)
        r'\b(E\d{2}/\d{2}/\d{4})\b',  # EDD/MM/YYYY (prefix 'E')
        r'\b(CB\s?\d{2}\.\d{2}\.\d{2})\b',  # CB DD.MM.YY or CBDD.MM.YY
        r'\b(CB\s?\d{1,2}\s?\d{1,2}\s?\d{2})\b',  # CB DD MM YY or CBDD MM YY
        r'\b(E\d{2}\.\d{2}\.\d{2})\b',  # EDD.MM.YY (e.g., 'E04.03.25M60:38')
    ]

    # Keywords to identify expiry date
    expiry_keywords = ['exp:', 'expiry', 'e:', 'use by', 'best before', 'exp date', 'exp.date', 'exp', 'expd', 'expiration', 'cb', 'e', 'exp. date : ']

    # Extract all valid dates from the OCR result
    valid_dates = []
    for text in extracted_text:
        # Check if the text contains any expiry keywords
        if any(keyword in text.lower() for keyword in expiry_keywords):
            # Search for a date in the text
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    raw_date = match.group(0)
                    formatted_date = convert_to_yyyy_mm_dd(raw_date)
                    if formatted_date:
                        valid_dates.append(formatted_date)

    # If no valid dates are found, search for dates without keywords
    if not valid_dates:
        for text in extracted_text:
            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    raw_date = match.group(0)
                    formatted_date = convert_to_yyyy_mm_dd(raw_date)
                    if formatted_date:
                        valid_dates.append(formatted_date)

    # If no valid dates are found, return None
    if not valid_dates:
        return None

    # Select the greatest date as the expiry date
    expiry_date = max(valid_dates)
    return expiry_date