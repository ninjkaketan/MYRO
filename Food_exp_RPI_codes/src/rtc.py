from datetime import datetime

def get_current_date():
    """
    Returns the current date and time from the Raspberry Pi's inbuilt RTC.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")