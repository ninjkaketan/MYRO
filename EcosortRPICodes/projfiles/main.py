import threading
from time import sleep
from gpiozero import DistanceSensor
import requests
from motionsen import start_motion_detection

# Function to run ultrasonic sensor code in a separate thread
def ultrasonic_sensor_thread():
    # Initialize ultrasonic sensors
    ultrasonic_bin1 = DistanceSensor(echo=23, trigger=24, max_distance=1.0)
    ultrasonic_bin2 = DistanceSensor(echo=17, trigger=27, max_distance=1.0)

    # ThingSpeak API URL and Write Key
    THINGSPEAK_URL = "https://api.thingspeak.com/update?api_key=TXP2PIP7V2VO7EQR&field1=0"
    WRITE_API_KEY = "TXP2PIP7V2VO7EQR"  # Replace with your ThingSpeak Write API Key

    # Set the maximum and minimum distances (bin height in cm)
    BIN_EMPTY_DISTANCE = 35
    BIN_FULL_DISTANCE = 5

    def calculate_fill_percentage(distance_cm):
        """
        Converts distance to a fill percentage.
        Closer distance = More full.
        """
        if distance_cm <= BIN_FULL_DISTANCE:
            return 100
        elif distance_cm >= BIN_EMPTY_DISTANCE:
            return 0
        else:
            fill_percentage = 100 - ((distance_cm - BIN_FULL_DISTANCE) / (BIN_EMPTY_DISTANCE - BIN_FULL_DISTANCE) * 100)
            fill_percentage = max(0, min(fill_percentage, 100))
            return round(fill_percentage, 2)

    def send_to_thingspeak(fill_percentage_bin1, fill_percentage_bin2):
        """
        Sends the fill percentages to ThingSpeak.
        """
        payload = {
            "api_key": WRITE_API_KEY,
            "field1": fill_percentage_bin1,  # Bin 1
            "field2": fill_percentage_bin2   # Bin 2
        }
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

            print(f"Raw Distance Bin 1: {distance_bin1_cm:.2f} cm | Raw Distance Bin 2: {distance_bin2_cm:.2f} cm")

            # Calculate fill percentage for both bins
            fill_percentage_bin1 = calculate_fill_percentage(distance_bin1_cm)
            fill_percentage_bin2 = calculate_fill_percentage(distance_bin2_cm)

            print(f"Distance Bin 1: {distance_bin1_cm:.2f} cm | Bin 1 Fill Level: {fill_percentage_bin1:.2f}%")
            print(f"Distance Bin 2: {distance_bin2_cm:.2f} cm | Bin 2 Fill Level: {fill_percentage_bin2:.2f}%")

            # Send data to ThingSpeak
            send_to_thingspeak(fill_percentage_bin1, fill_percentage_bin2)

            sleep(15)  # Wait for 15 seconds before the next reading
    except KeyboardInterrupt:
        print("\nUltrasonic sensor test stopped by user.")

# Function to start motion detection in a separate thread
def motion_detection_thread():
    start_motion_detection()

if __name__ == "__main__":
    # Start the motion detection in a new thread
    motion_thread = threading.Thread(target=motion_detection_thread, daemon=True)
    motion_thread.start()

    # Start the ultrasonic sensor monitoring in a new thread
    ultrasonic_thread = threading.Thread(target=ultrasonic_sensor_thread, daemon=True)
    ultrasonic_thread.start()

    try:
        # Keep the main program running to allow threads to run
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Program interrupted.")