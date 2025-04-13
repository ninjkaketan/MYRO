
from gpiozero import DistanceSensor, MotionSensor, Servo
from picamera2 import Picamera2
from time import sleep
import requests
from ml_model import classify_trash
from servo_control import open_bin

# Initialize ultrasonic sensors
ultrasonic_bin1 = DistanceSensor(echo=23, trigger=24, max_distance=1.0)
ultrasonic_bin2 = DistanceSensor(echo=27, trigger=17, max_distance=1.0)

# Initialize motion sensor and camera
PIR_PIN = 15  # Motion sensor on GPIO 15
pir = MotionSensor(PIR_PIN)
picam2 = Picamera2()
picam2.start()

# Servo Pins
DECOMPOSABLE_SERVO_PIN = 25
NON_DECOMPOSABLE_SERVO_PIN = 8

decomposable_servo = Servo(DECOMPOSABLE_SERVO_PIN)
non_decomposable_servo = Servo(NON_DECOMPOSABLE_SERVO_PIN)

# ThingSpeak API URL and Write Key
THINGSPEAK_URL = "https://api.thingspeak.com/update?api_key=TXP2PIP7V2VO7EQR&field1=0"
WRITE_API_KEY = "TXP2PIP7V2VO7EQR"  # Replace with your ThingSpeak Write API Key

# Set the maximum and minimum distances for bin height (cm)
BIN_EMPTY_DISTANCE = 30
BIN_FULL_DISTANCE = 5

def calculate_fill_percentage(distance_cm):
    if distance_cm <= BIN_FULL_DISTANCE:
        return 100
    elif distance_cm >= BIN_EMPTY_DISTANCE:
        return 0
    else:
        fill_percentage = 100 - ((distance_cm - BIN_FULL_DISTANCE) / (BIN_EMPTY_DISTANCE - BIN_FULL_DISTANCE) * 100)
        return round(max(0, min(fill_percentage, 100)), 2)

def send_to_thingspeak(fill_percentage_bin1, fill_percentage_bin2):
    payload = {
        "api_key": WRITE_API_KEY,
        "field1": fill_percentage_bin1,
        "field2": fill_percentage_bin2
    }

    try:
        response = requests.post(THINGSPEAK_URL, params=payload)
        if response.status_code == 200:
            print(f"Data sent successfully! Bin 1 Fill: {fill_percentage_bin1}% | Bin 2 Fill: {fill_percentage_bin2}%")
        else:
            print(f"Error sending data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def capture_and_classify_trash():
    print("Motion detected! Capturing image...")
    image_path = 'captured_trash.jpg'
    picam2.capture_file(image_path)
    print("Image captured! Classifying trash...")

    category = classify_trash(image_path)
    open_bin(category)

def monitor_motion():
    print("Waiting for motion...")
    try:
        while True:
            pir.wait_for_motion()
            capture_and_classify_trash()
            print("Waiting for next motion event...\n")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        picam2.stop()

# Main loop
try:
    while True:
        # Monitor motion
        monitor_motion()

        # Monitor ultrasonic sensors
        distance_bin1_cm = ultrasonic_bin1.distance * 100
        distance_bin2_cm = ultrasonic_bin2.distance * 100

        print(f"Raw Distance Bin 1: {distance_bin1_cm:.2f} cm | Raw Distance Bin 2: {distance_bin2_cm:.2f} cm")

        # Calculate fill percentage
        fill_percentage_bin1 = calculate_fill_percentage(distance_bin1_cm)
        fill_percentage_bin2 = calculate_fill_percentage(distance_bin2_cm)

        print(f"Distance Bin 1: {distance_bin1_cm:.2f} cm | Bin 1 Fill Level: {fill_percentage_bin1:.2f}%")
        print(f"Distance Bin 2: {distance_bin2_cm:.2f} cm | Bin 2 Fill Level: {fill_percentage_bin2:.2f}%")

        # Send data to ThingSpeak
        send_to_thingspeak(fill_percentage_bin1, fill_percentage_bin2)

        sleep(15)  # Wait for 15 seconds before the next reading

except KeyboardInterrupt:
    print("\nTest stopped by user.")
