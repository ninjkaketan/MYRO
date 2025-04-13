from transformers import AutoModelForImageClassification, AutoImageProcessor
import torch
from PIL import Image

# Load the model and processor
model_name = "watersplash/waste-classification"
model = AutoModelForImageClassification.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

# Load an image for testing
image = Image.open("image.jpg")  # Replace with the actual image path
inputs = processor(images=image, return_tensors="pt")

# Perform the prediction
with torch.no_grad():
    logits = model(**inputs).logits

# Get the predicted class
predicted_class = torch.argmax(logits, dim=-1)
print(f"Predicted class: {predicted_class.item()}")
