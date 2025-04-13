from gpiozero import MotionSensor
from time import sleep

PIR_PIN = 15

pir = MotionSensor(PIR_PIN)

print("PIR Motion sensor test (Ctrl+D to exit)")

try:
    while True:
        pir.wait_for_motion()
        print("Motion Detected")

        pir.wait_for_no_motion()
        print("No motion detected")

except KeyboardInterrupt:
    print("Exiting")