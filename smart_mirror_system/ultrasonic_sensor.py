import lgpio
import time
import subprocess

TRIG = 17
ECHO = 27

class DistanceSensor:
    def __init__(self):
        self.h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self.h, TRIG)
        lgpio.gpio_claim_input(self.h, ECHO)
        self.last_trigger = 0
        self.cooldown = 10  # seconds

    def measure_distance(self):
        lgpio.gpio_write(self.h, TRIG, 1)
        time.sleep(0.00001)
        lgpio.gpio_write(self.h, TRIG, 0)

        pulse_start = pulse_end = None
        timeout = time.time() + 0.1  # 100ms timeout
        
        while lgpio.gpio_read(self.h, ECHO) == 0:
            pulse_start = time.time()
            if time.time() > timeout: return None

        timeout = time.time() + 0.1
        while lgpio.gpio_read(self.h, ECHO) == 1:
            pulse_end = time.time()
            if time.time() > timeout: return None

        return round((pulse_end - pulse_start) * 17150, 2) if (pulse_start and pulse_end) else None

    def cleanup(self):
        lgpio.gpiochip_close(self.h)

if __name__ == "__main__":
    sensor = DistanceSensor()
    try:
        while True:
            dist = sensor.measure_distance()
            if dist and dist < 10 and (time.time() - sensor.last_trigger) > sensor.cooldown:
                sensor.last_trigger = time.time()
                subprocess.run([f"{os.path.dirname(os.path.abspath(__file__))}/venv/bin/python3", 
                              "voice_recognition.py"])
            time.sleep(0.5)
    finally:
        sensor.cleanup()
