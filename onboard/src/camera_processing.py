
import cv2
import numpy as np
import base64

class ColorTracker:
    def __init__(self, camera_width, camera_height):
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.COLOR_RANGES = {
            "red": [
                (np.array([0, 120, 70]), np.array([10, 255, 255])),
                (np.array([170, 120, 70]), np.array([180, 255, 255]))
            ],
            "green": [(np.array([40, 70, 70]), np.array([80, 255, 255]))],
            "blue": [(np.array([100, 150, 0]), np.array([140, 255, 255]))],
            "yellow": [(np.array([20, 100, 100]), np.array([30, 255, 255]))]
        }
        self.current_color_to_track = "yellow" # Default color

    def set_color_to_track(self, color_name):
        if color_name in self.COLOR_RANGES:
            self.current_color_to_track = color_name
        else:
            print(f"Warning: Color '{color_name}' not recognized. Keeping '{self.current_color_to_track}'.")

    def find_object(self, image):
        # Decode base64 image if it's a string
        if isinstance(image, str):
            nparr = np.frombuffer(base64.b64decode(image), np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = np.zeros((self.camera_height, self.camera_width), dtype=np.uint8)

        if self.current_color_to_track in self.COLOR_RANGES:
            for lower, upper in self.COLOR_RANGES[self.current_color_to_track]:
                mask |= cv2.inRange(hsv, lower, upper)
        else:
            return None, 0 # No valid color to track
        
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            # Only consider contours above a certain size to filter noise
            if area > 300:
                # Get the center of the contour
                M = cv2.moments(largest_contour)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy), area

        return None, 0

class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def find_face(self, image):
        # Decode base64 image if it's a string
        if isinstance(image, str):
            nparr = np.frombuffer(base64.b64decode(image), np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        if len(faces) > 0:
            # Return the largest face
            x, y, w, h = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)[0]
            return (x, y, w, h)
        return None
