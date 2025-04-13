from gpiozero import DistanceSensor
import requests
from time import sleep

# Initialize ultrasonic sensors
# Sensor 1 (for Bin 1) - TRIG: GPIO 23, ECHO: GPIO 24
ultrasonic_bin1 = DistanceSensor(echo=23, trigger=24, max_distance=1.0)

# Sensor 2 (for Bin 2) - TRIG: GPIO 25, ECHO: GPIO 8
ultrasonic_bin2 = DistanceSensor(echo=27, trigger=17, max_distance=1.0)

# ThingSpeak API URL and Write Key (from your channel settings)
THINGSPEAK_URL = "https://api.thingspeak.com/update?api_key=TXP2PIP7V2VO7EQR&field1=0"
WRITE_API_KEY = "TXP2PIP7V2VO7EQR"  # Replace with your ThingSpeak Write API Key

# Set the maximum and minimum distances (bin height in cm)
BIN_EMPTY_DISTANCE = 30  # Distance when the bin is empty (in cm)
BIN_FULL_DISTANCE = 5    # Distance when the bin is full (in cm)

def calculate_fill_percentage(distance_cm):
    """
    Converts distance to a fill percentage.
    Closer distance = More full.
    """
    # Check if the distance is within a valid range
    if distance_cm <= BIN_FULL_DISTANCE:
        return 100  # Bin is completely full
    elif distance_cm >= BIN_EMPTY_DISTANCE:
        return 0  # Bin is empty
    else:
        # Linear interpolation to calculate fill level
        fill_percentage = 100 - ((distance_cm - BIN_FULL_DISTANCE) / (BIN_EMPTY_DISTANCE - BIN_FULL_DISTANCE) * 100)
        # Clamp fill percentage between 0 and 100
        fill_percentage = max(0, min(fill_percentage, 100))
        return round(fill_percentage, 2)

def send_to_thingspeak(fill_percentage_bin1, fill_percentage_bin2):
    """
    Sends the fill percentages to ThingSpeak.
    """
    # Prepare the data for the API request
    payload = {
        "api_key": WRITE_API_KEY,
        "field1": fill_percentage_bin1,  # "field1" corresponds to the first field (Bin 1)
        "field2": fill_percentage_bin2   # "field2" corresponds to the second field (Bin 2)
    }

    # Send data to ThingSpeak
    try:
        response = requests.post(THINGSPEAK_URL, params=payload)
        if response.status_code == 200:
            print(f"Data sent successfully! Bin 1 Fill Level: {fill_percentage_bin1}% | Bin 2 Fill Level: {fill_percentage_bin2}%")
        else:
            print(f"Error sending data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

print("Ultrasonic sensor percentage test started...")

try:
    while True:
        # Read distance for both bins
        distance_bin1_cm = ultrasonic_bin1.distance * 100  # Convert meters to cm
        distance_bin2_cm = ultrasonic_bin2.distance * 100  # Convert meters to cm
        
        # Print out the raw distances for debugging
        print(f"Raw Distance Bin 1: {distance_bin1_cm:.2f} cm | Raw Distance Bin 2: {distance_bin2_cm:.2f} cm")
        
        # Calculate fill percentage for both bins
        fill_percentage_bin1 = calculate_fill_percentage(distance_bin1_cm)
        fill_percentage_bin2 = calculate_fill_percentage(distance_bin2_cm)
        
        # Print distance and bin fill percentage
        print(f"Distance Bin 1: {distance_bin1_cm:.2f} cm | Bin 1 Fill Level: {fill_percentage_bin1:.2f}%")
        print(f"Distance Bin 2: {distance_bin2_cm:.2f} cm | Bin 2 Fill Level: {fill_percentage_bin2:.2f}%")
        
        # Send data to ThingSpeak
        send_to_thingspeak(fill_percentage_bin1, fill_percentage_bin2)
        
        sleep(15)  # Wait for 15 seconds before the next reading

except KeyboardInterrupt:
    print("\nTest stopped by user.")
