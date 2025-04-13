import os
import time
from ultrasonic_sensor import DistanceSensor
from voice_recognition import process_user_request
import pymongo

# Configuration
TRIGGER_DISTANCE_CM = 10
COOLDOWN_SEC = 10
HTML_FILE = "/home/ketan/MagicMirror/modules/MMM-HTMLBox/vitaminD.html"
MONGODB_URI = "mongodb+srv://user12:user123@cluster0.jajgc.mongodb.net/VitDTracker?retryWrites=true&w=majority&appName=Cluster0"

def update_display(content):
    try:
        with open(HTML_FILE, "w") as f:
            f.write(content)
        os.chmod(HTML_FILE, 0o777)
    except Exception as e:
        print(f"Display update failed: {e}")

def run_voice_recognition(db):
    try:
        # Skip alsactl which needs root permissions
        update_display('<div style="color:yellow;text-align:center">SAY/SPELL YOUR NAME</div>')
        time.sleep(1)
        
        success, html = process_user_request(db)
        update_display(html)
        time.sleep(10 if success else 3)
        
    except Exception as e:
        update_display('<div style="color:red;text-align:center">MIC ERROR</div>')
        print(f"Error: {e}")
        time.sleep(3)

if __name__ == "__main__":
    # Fix permissions for audio
    os.system('sudo chmod a+rw /dev/snd/*')
    
    sensor = DistanceSensor()
    mongo_client = pymongo.MongoClient(MONGODB_URI)
    db = mongo_client["VitDTracker"]
    
    try:
        print("System ready - USB mic configured")
        update_display('<div style="color:green;text-align:center">READY</div>')
        
        last_trigger = 0
        while True:
            dist = sensor.measure_distance()
            now = time.time()
            
            if dist and dist < TRIGGER_DISTANCE_CM and (now - last_trigger) > COOLDOWN_SEC:
                last_trigger = now
                print(f"User detected at {dist}cm")
                run_voice_recognition(db)
                
            time.sleep(0.5)
            
    finally:
        sensor.cleanup()
        mongo_client.close()
        update_display('<div style="color:gray;text-align:center">OFFLINE</div>')
