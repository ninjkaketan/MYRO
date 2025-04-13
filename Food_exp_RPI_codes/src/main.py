import requests
import time
from camera import capture_image
from ocr import extract_text, extract_expiry_date
from rtc import get_current_date

# Function to send expiry date to Next.js backend
def send_expiry_date(expiry_date):
    """
    Sends the extracted expiry date to the Next.js backend.
    """
    # Use the Network URL of your Next.js backend
    url = 'http://10.5.0.238:3001/api/expiry'  # Use the Network URL from `npm run dev`
    data = {'expiry_date': expiry_date}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Expiry date sent successfully!")
        else:
            print(f"Error: Failed to send expiry date. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    while True:  # Run the code continuously
        try:
            # Step 1: Capture an image
            print("Capturing image...")
            image_path = capture_image()
            if not image_path:
                print("Image capture failed. Retrying in 5 seconds...")
                time.sleep(5)  # Wait for 5 seconds before retrying
                continue

            # Step 2: Extract text from the image
            extracted_text = extract_text(image_path)
            if not extracted_text:
                print("No text extracted from the image. Retrying in 5 seconds...")
                time.sleep(5)  # Wait for 5 seconds before retrying
                continue

            print("Extracted Text:", extracted_text)

            # Step 3: Extract the expiry date from the OCR result
            expiry_date = extract_expiry_date(extracted_text)
            if expiry_date:
                print(f"Extracted Expiry Date: {expiry_date}")
            else:
                print("No expiry date found in the extracted text. Retrying in 5 seconds...")
                time.sleep(5)  # Wait for 5 seconds before retrying
                continue

            # Step 4: Get the current date from the RTC
            current_date = get_current_date()
            print(f"Current Date: {current_date}")

            # Step 5: Send the expiry date to the Next.js backend
            send_expiry_date(expiry_date)

            # Wait for 10 seconds before capturing the next image
            print("Waiting for 10 seconds before capturing the next image...")
            time.sleep(10)

        except KeyboardInterrupt:
            # Allow the user to stop the script gracefully
            print("\nScript stopped by user. Exiting...")
            break
        except Exception as e:
            # Handle any unexpected errors
            print(f"Unexpected error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()