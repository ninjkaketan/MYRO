import requests
import time
from rtc import get_current_date

# Function to fetch expiring items from MongoDB
def fetch_expiring_items():
    try:
        #  the URL of your Next.js backend
        url = 'http://192.168.1.10:3000/api/expiry'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Returns a list of expiring items
        else:
            print(f"Error: Failed to fetch expiring items. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

# Function to check for expiring items
def check_expiry():
    while True:
        # Get the current date from the RTC module
        current_date = get_current_date()
        print(f"Current Date: {current_date}")

        # Fetch expiring items from MongoDB
        expiring_items = fetch_expiring_items()
        if expiring_items:
            print("Expiring Items:", expiring_items)
            # Send alerts to the website (optional)
            send_alerts(expiring_items)
        else:
            print("No items expiring soon.")

        # Wait for 24 hours before checking again
        time.sleep(86400)  # 86400 seconds = 24 hours

# Function to send alerts to the website
def send_alerts(expiring_items):
    try:
        # the URL of your Next.js backend
        url = 'http://10.5.0.238:3001/api/alerts'
        response = requests.post(url, json=expiring_items)
        if response.status_code == 200:
            print("Alerts sent successfully!")
        else:
            print(f"Error: Failed to send alerts. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_expiry()