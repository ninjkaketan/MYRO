from PIL import Image
import torch
from transformers import AutoModelForImageClassification, AutoImageProcessor

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
    "trash": "Non-Decomposable",
    
    "shoes": "Not Available",  # Exclude shoes from being classified
    "clothes": "Not Available"  # Exclude clothes from being classified
}

# Confidence threshold for classification
CONFIDENCE_THRESHOLD = 0.7  # 70% confidence

# Function to check if an image is too dark or blank
def is_blank_image(image):
    grayscale = image.convert("L")  # Convert to grayscale
    avg_pixel_value = sum(grayscale.getdata()) / len(grayscale.getdata())
    
    if avg_pixel_value < 10:  # Adjust threshold if needed
        print("?? Image is too dark or blank! Ignoring classification.")
        return True
    
    return False

# Function to classify an image
def classify_trash(image_path):
    image = Image.open(image_path)

    # Check if the image is blank
    if is_blank_image(image):
        return "Not Available"

    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        logits = model(**inputs).logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
    
    predicted_class = torch.argmax(probabilities, dim=-1).item()
    confidence = probabilities[0, predicted_class].item()
    
    class_labels = model.config.id2label
    predicted_label = class_labels[predicted_class]

    # Check confidence threshold
    if confidence < CONFIDENCE_THRESHOLD:
        print(f"?? Low confidence ({confidence*100:.2f}%) - Classification ignored.")
        return "Not Available"

    # Check if the predicted label is in the waste classification
    classification = waste_classification.get(predicted_label.lower(), "Not Available")
    
    print(f"?? Predicted trash type: {predicted_label} ({confidence*100:.2f}%)")
    print(f"?? Category: {classification}")

    return classification
