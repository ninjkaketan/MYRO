from picamera2 import Picamera2
from time import sleep
from PIL import Image
import torch
from transformers import AutoModelForImageClassification, AutoImageProcessor

# Load the waste classification model and processor from Hugging Face
model_name = "watersplash/waste-classification"
model = AutoModelForImageClassification.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

# Initialize Picamera2
picam2 = Picamera2()
picam2.start()

# Function to classify an image and return the trash type
def classify_trash(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")

    # Perform the prediction
    with torch.no_grad():
        logits = model(**inputs).logits
    
    # Get the predicted class
    predicted_class = torch.argmax(logits, dim=-1)
    class_labels = model.config.id2label  # Get the label mapping
    
    # Print the prediction result
    predicted_label = class_labels[predicted_class.item()]
    print(f"Predicted trash type: {predicted_label}")
    return predicted_label

# Function to capture image using Raspberry Pi Camera and classify the trash
def capture_and_classify_trash():
    print("Preparing to capture image...")
    # Capture image
    image_path = 'captured_trash.jpg'
    picam2.capture_file(image_path)
    print("Image captured! Classifying trash...")
    # Classify the captured image
    classify_trash(image_path)

# Call the function to capture an image and classify it
capture_and_classify_trash()

# Stop the camera
picam2.stop()
