import time
from gpiozero import MotionSensor
from picamera2 import Picamera2
from time import sleep
from threading import Thread
from ml_model import classify_trash  # Import ML classification function
from servo_control import open_bin  # Import servo control function

# GPIO Pin for Motion Sensor
PIR_PIN = 16  # Motion sensor on GPIO 16

# Initialize motion sensor with a higher threshold to reduce false positives
pir = MotionSensor(PIR_PIN, threshold=0.6, queue_len=5)  # Adjust as needed

# Initialize camera
picam2 = Picamera2()
picam2.start()
sleep(2)  # Give the camera time to warm up

# Debounce time (seconds) to prevent repeated triggers
DEBOUNCE_TIME = 5  # Adjust if needed

# Function to check if an image is blank
def is_blank_image(image_path):
    from PIL import Image
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    avg_pixel_value = sum(image.getdata()) / len(image.getdata())

    if avg_pixel_value < 10:  # Adjust threshold if needed
        print("?? Blank or too dark image detected! Ignoring classification.")
        return True

    return False

# Function to capture image and classify trash
def capture_and_classify_trash():
    print("Motion detected! Capturing image...")
    image_path = 'captured_trash.jpg'

    sleep(1)  # Short delay to allow the camera to adjust to lighting
    picam2.capture_file(image_path)
    print("? Image captured! Processing...")

    # Check if the image is blank
    if is_blank_image(image_path):
        return  # Skip classification if the image is blank

    category = classify_trash(image_path)
    
    if category not in ["Not Available", ""]:
        open_bin(category)  # Only open bin for valid classifications

# Function to monitor motion sensor with debounce logic
def monitor_motion():
    print("?? Motion sensor initialized. Waiting for motion...")
    
    try:
        last_motion_time = 0  # Track last detected motion time

        while True:
            if pir.motion_detected:  # More reliable than pir.is_active
                current_time = time.time()

                # Check if enough time has passed since the last detection
                if current_time - last_motion_time > DEBOUNCE_TIME:
                    print("?? Motion detected!")
                    capture_and_classify_trash()
                    last_motion_time = current_time  # Update last motion time
                else:
                    print("?? Ignoring false positive (triggered too soon).")

            sleep(0.2)  # Slightly longer sleep to reduce CPU usage

    except KeyboardInterrupt:
        print("?? Exiting motion detection...")
    finally:
        picam2.stop()  # Ensure camera is stopped properly

# Run motion detection in a separate thread for concurrency
def start_motion_detection():
    motion_thread = Thread(target=monitor_motion, daemon=True)  # Daemon=True ensures it stops with the main program
    motion_thread.start()
