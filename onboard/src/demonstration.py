import time
import cv2
import numpy as np

class Demonstration:
    def __init__(self, main_app):
        self.main_app = main_app

    def run(self):
        self.main_app.ai_services.text_to_speech("Hello, I am the QCar agent. I will now demonstrate my capabilities.")
        time.sleep(3) # Give time for speech to play

        # Demonstrate explore mode
        self.main_app.ai_services.text_to_speech("First, I will demonstrate my explore mode. I will drive around and avoid obstacles.")
        self.main_app.command = "explore"
        time.sleep(10)
        self.main_app.command = "stop"
        time.sleep(1)

        # Demonstrate search mode
        self.main_app.ai_services.text_to_speech("Next, I will demonstrate my search mode. I will search for a yellow object.")
        self.main_app.command = "search"
        time.sleep(10)
        self.main_app.command = "stop"
        time.sleep(1)

        # Demonstrate track mode
        self.main_app.ai_services.text_to_speech("Now, I will demonstrate my track mode. I will track the yellow object.")
        self.main_app.command = "track"
        time.sleep(10)
        self.main_app.command = "stop"
        time.sleep(1)

        # Demonstrate describe mode
        self.main_app.ai_services.text_to_speech("Finally, I will demonstrate my describe mode. I will describe what I see.")
        time.sleep(3) # Give time for speech to play
        
        # Capture image and request description
        image_data = self.main_app.hardware.read_image()
        if image_data:
            # Decode base64 for local display and saving
            nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imwrite("current_view.png", image)
            description = self.main_app.ai_services.describe_image("current_view.png")
            print(f"Description: {description}")
            self.main_app.ai_services.text_to_speech(description)
            time.sleep(5) # Give time for speech to play

        self.main_app.ai_services.text_to_speech("This concludes my demonstration. Thank you for watching.")
        self.main_app.command = "stop"