

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_services import AIServices

def test_description():
    ai_services = AIServices()
    image_path = "/home/arihant/Downloads/down.jpeg"
    
    print(f"Describing image: {image_path}")
    description = ai_services.describe_image(image_path)
    print(f"\nDescription: {description}\n")
    
    print("Converting description to speech...")
    ai_services.text_to_speech(description)
    print("Done.")

if __name__ == "__main__":
    test_description()

