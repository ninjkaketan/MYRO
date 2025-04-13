from gpiozero import MotionSensor, DistanceSensor, Servo
from time import sleep

# Set up the sensors
pir = MotionSensor(15)  # Motion sensor on pin 15
distance_sensor_bin1 = DistanceSensor(echo=17, trigger=4)  # Bin 1 ultrasonic sensor
distance_sensor_bin2 = DistanceSensor(echo=18, trigger=5)  # Bin 2 ultrasonic sensor

# Set up the servos
decomposable_servo = Servo(18)  # Servo for decomposable bin
non_decomposable_servo = Servo(25)  # Servo for non-decomposable bin

def read_ultrasonic_sensors():
    """Read ultrasonic sensor values and print fill levels"""
    distance_bin1 = distance_sensor_bin1.distance * 100  # Convert to cm
    distance_bin2 = distance_sensor_bin2.distance * 100  # Convert to cm

    fill_level_bin1 = max(0, min(100, 100 - distance_bin1))  # Ensure values are within range
    fill_level_bin2 = max(0, min(100, 100 - distance_bin2))

    print(f"Distance Bin 1: {distance_bin1:.2f} cm | Fill Level Bin 1: {fill_level_bin1:.2f}%")
    print(f"Distance Bin 2: {distance_bin2:.2f} cm | Fill Level Bin 2: {fill_level_bin2:.2f}%")

# Main loop to handle motion detection and ultrasonic sensors
while True:
    # Read ultrasonic sensor data
    read_ultrasonic_sensors()
    
    # Check motion sensor without blocking
    if pir.motion_detected:
        print("Motion detected! Opening bins...")
        
        # Example logic: Open both bins momentarily
        decomposable_servo.min()
        non_decomposable_servo.min()
        sleep(1)  # Delay for consistency

        decomposable_servo.max()
        non_decomposable_servo.max()
        sleep(1)

    else:
        print("No motion detected")

    sleep(1)  # General delay to match ultrasonic sensor readings
