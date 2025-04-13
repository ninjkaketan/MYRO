from gpiozero import Servo
from time import sleep

# GPIO Pins
DECOMPOSABLE_SERVO_PIN = 12  # Servo for decomposable bin
NON_DECOMPOSABLE_SERVO_PIN = 6  # Servo for non-decomposable bin

# Initialize servos
decomposable_servo = Servo(DECOMPOSABLE_SERVO_PIN)
non_decomposable_servo = Servo(NON_DECOMPOSABLE_SERVO_PIN)

# Function to control servos
def open_bin(category):
    if category == "Decomposable":
        print("✅ Opening Decomposable Bin")
        decomposable_servo.max()  # Move servo to open position
        sleep(2)  # Keep bin open for 2 seconds
        decomposable_servo.min()  # Close bin
    elif category == "Non-Decomposable":
        print("🛑 Opening Non-Decomposable Bin")
        non_decomposable_servo.max()
        sleep(2)
        non_decomposable_servo.min()
    else:
        print("⚠️ Not Available - Manual Sorting Needed")
