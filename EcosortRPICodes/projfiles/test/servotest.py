from gpiozero import Servo
from time import sleep
from PIL import Image
import torch
from transformers import AutoModelForImageClassification, AutoImageProcessor

# GPIO Pins for servos
DECOMPOSABLE_SERVO_PIN = 18  # Servo for decomposable bin
NON_DECOMPOSABLE_SERVO_PIN = 25  # Servo for non-decomposable bin

# Initialize servos
decomposable_servo = Servo(DECOMPOSABLE_SERVO_PIN)
non_decomposable_servo = Servo(NON_DECOMPOSABLE_SERVO_PIN)

# Load the waste classification model and processor from Hugging Face
model_name = "watersplash/waste-classification"
model = AutoModelForImageClassification.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

# Waste classification categories
waste_classification = {
    "biological": "Decomposable",
    "cardboard": "Decomposable",
    "paper": "Decomposable",

    "battery": "Non-Decomposable",
    "brown-glass": "Non-Decomposable",
    "white-glass": "Non-Decomposable",
    "green-glass": "Non-Decomposable",
    "metal": "Non-Decomposable",
    "plastic": "Non-Decomposable",
    "shoes": "Non-Decomposable",
    "clothes": "Non-Decomposable",
    "trash": "Non-Decomposable"
}

# Function to control servos
def open_bin(category):
    if category == "Decomposable":
        print("✅ Opening Decomposable Bin")
        decomposable_servo.value = 0.6  # Slightly open the decomposable bin
        non_decomposable_servo.value = -1  # Fully close the non-decomposable bin
    elif category == "Non-Decomposable":
        print("🛑 Opening Non-Decomposable Bin")
        non_decomposable_servo.value = 0.6  # Slightly open the non-decomposable bin
        decomposable_servo.value = -1  # Fully close the decomposable bin
    else:
        print("⚠️ Not Available - Manual Sorting Needed")

    sleep(2)  # Keep the bin open for 2 seconds
    decomposable_servo.value = -1  # Close the decomposable bin
    non_decomposable_servo.value = -1  # Close the non-decomposable bin

# Function to classify an image
def classify_trash(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        logits = model(**inputs).logits
    
    predicted_class = torch.argmax(logits, dim=-1)
    class_labels = model.config.id2label
    predicted_label = class_labels[predicted_class.item()]
    
    classification = waste_classification.get(predicted_label.lower(), "Not Available")
    
    print(f"Predicted trash type: {predicted_label}")
    print(f"Category: {classification}")

    return classification

# TESTING WITH TWO IMAGES
image_paths = ["image.jpg", "image2.jpg", "image3.jpg", "image4.jpg"]  # Change these to your actual image filenames

for image_path in image_paths:
    print(f"\n🔍 Processing: {image_path}")
    
    category = classify_trash(image_path)  # Classify image
    open_bin(category)  # Open correct bin
    
    print("🕒 Waiting for 5 seconds before next test...")
    sleep(5)  # Wait for 5 seconds before the next classification

print("\n✅ Test complete!")
