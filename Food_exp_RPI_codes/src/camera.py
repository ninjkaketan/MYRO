from picamera2 import Picamera2
import time

def capture_image():
    """
    Captures an image using the Raspberry Pi Camera Module 3 with improved focus and lighting settings.
    Saves the image temporarily inside the 'projectfiles' folder with the name 'captured_image.jpg'.
    Returns the path to the saved image or None if capture fails after retries.
    """
    retries = 3  # Number of retries
    delay = 5  # Delay between retries in seconds

    for attempt in range(retries):
        try:
            # Initialize the camera
            picam2 = Picamera2()

            # Configure the camera for still capture with higher resolution
            config = picam2.create_still_configuration(main={"size": (3280, 2464)})  # Full resolution for Camera Module 3
            picam2.configure(config)

            # Enable Continuous Auto Focus (AF)
            picam2.set_controls({"AfMode": 2, "AfTrigger": 0})  # AfMode 2 = Continuous AF, AfTrigger 0 = Start AF

            # Start the camera
            picam2.start()

            # Allow more time for the autofocus to adjust
            print("Adjusting autofocus...")
            time.sleep(5)  # Increased delay to 5 seconds for better focus

            # Capture an image and save it temporarily as 'captured_image.jpg'
            image_path = 'captured_image.jpg'
            picam2.capture_file(image_path)
            print(f"Image saved temporarily: {image_path}")

            # Stop the camera
            picam2.stop()

            # Ensure the camera is properly closed
            picam2.close()

            return image_path

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retries failed. Camera initialization or capture failed.")
                return None