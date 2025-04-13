from gpiozero import DistanceSensor
from time import sleep

# Define one ultrasonic sensor
sensor = DistanceSensor(echo=23, trigger=24, max_distance=2.0)

print("🔍 Testing One Ultrasonic Sensor...")

try:
    while True:
        distance = sensor.distance * 100  # Convert to cm
        print(f"📦 Bin Level: {distance:.2f} cm")
        sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
