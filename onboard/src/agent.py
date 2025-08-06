from src.camera_processing import ColorTracker, FaceDetector
from src.obstacle_avoidance import VFH, DepthObstacleDetector
from src.planning import AStar
import time
import numpy as np
import cv2

class Agent:
    def __init__(self, camera_width, camera_height, grid):
        self.state = "stopped"
        self.tracker = ColorTracker(camera_width, camera_height)
        self.face_detector = FaceDetector()
        self.avoider_lidar = VFH()
        self.avoider_depth = DepthObstacleDetector(image_width=camera_width, image_height=camera_height)
        self.planner = AStar(grid)
        self.path = None
        self.path_index = 0
        self.search_start_time = 0
        self.request_description = False
        self.image_processing = ImageProcessing()

    def get_action(self, command, image, depth_data, lidar_distances, lidar_angles, gamepad_new_read, gamepad, target_location=None):
        throttle = 0.0
        steering = 0.0
        self.request_description = False # Reset request

        if command == "navigate":
            self.state = "navigating"
            # For demonstration, we'll assume the QCar starts at (0,0)
            start_node = (0, 0)
            self.path = self.planner.find_path(start_node, target_location)
            self.path_index = 0
        elif command == "explore":
            self.state = "exploring"
        elif command == "teleop":
            self.state = "teleop"
        elif command == "search":
            self.state = "searching"
            self.search_start_time = time.time()
        elif command == "track":
            self.state = "tracking"
        elif command == "face_track":
            self.state = "face_tracking"
        elif command == "lane_follow":
            self.state = "lane_following"
        elif command == "stop":
            self.state = "stopped"

        if self.state == "teleop":
            if gamepad_new_read:
                throttle = -gamepad.leftJoystickY
                steering = gamepad.rightJoystickX
            return throttle, steering

        # Prioritize obstacle avoidance using Lidar and Depth
        if self.avoider_lidar.is_obstacle_present(lidar_distances, lidar_angles) or \
           self.avoider_depth.is_obstacle_present(depth_data):
            throttle = -0.2 # Reverse
            steering = 0.5 # Turn right
            return throttle, steering

        # VFH-based local steering for autonomous modes
        vfh_steering = self.avoider_lidar.get_steering_direction(lidar_distances, lidar_angles)

        if self.state == "navigating":
            if self.path and self.path_index < len(self.path):
                throttle = 0.2
                # Combine VFH with path following
                # If VFH suggests a significant turn, prioritize it
                if np.abs(vfh_steering) > 0.1:
                    steering = vfh_steering
                else:
                    # Otherwise, try to steer towards the next path node
                    # This is a very simplified approach and would need a proper path follower
                    current_node = (0,0) # Assuming current position is (0,0) for simplicity
                    next_node = self.path[self.path_index]
                    
                    # Calculate desired steering towards next_node
                    # This is a placeholder, a real implementation would use PID or similar
                    desired_steering = 0.0
                    if next_node[1] > current_node[1]: # If next node is to the right
                        desired_steering = 0.1
                    elif next_node[1] < current_node[1]: # If next node is to the left
                        desired_steering = -0.1

                    steering = desired_steering

                # Advance to next path node if close enough (simplified)
                # In a real system, this would be based on actual position and distance
                if self.path_index < len(self.path) - 1 and np.linalg.norm(np.array(current_node) - np.array(self.path[self.path_index])) < 0.5:
                    self.path_index += 1

            else:
                self.state = "stopped"

        object_center, object_area = self.tracker.find_object(image)
        face_bbox = self.face_detector.find_face(image)

        if self.state == "exploring":
            throttle = 0.2
            steering = vfh_steering
            if object_center is not None:
                self.state = "stopped"
                self.request_description = True # Request description from main loop

        if self.state == "searching":
            throttle = 0.2
            steering = vfh_steering
            if object_center is not None:
                self.state = "tracking"

        if self.state == "tracking":
            if object_center is not None:
                error = self.tracker.camera_width / 2 - object_center[0]
                steering = np.clip(error / 100.0, -0.5, 0.5)
                throttle = 0.2
            else:
                self.state = "searching"

        if self.state == "face_tracking":
            if face_bbox is not None:
                x, y, w, h = face_bbox
                face_center_x = x + w // 2
                error = self.tracker.camera_width / 2 - face_center_x
                steering = np.clip(error / 100.0, -0.5, 0.5)
                throttle = 0.1 # Move slowly towards the face
            else:
                throttle = 0.0
                steering = 0.0 # Stop if face is lost

        if self.state == "lane_following":
            # Decode base64 image if it's a string
            if isinstance(image, str):
                nparr = np.frombuffer(base64.b64decode(image), np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Crop image for lane detection (adjust these values based on your camera and lane position)
            cropped_image = image[int(image.shape[0]*0.7):int(image.shape[0]*0.9), 0:image.shape[1]]
            hsv_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

            # Yellow lane detection (from lanefollower.py)
            lower_yellow = np.array([10, 50, 100])
            upper_yellow = np.array([45, 255, 255])
            binary_image = self.image_processing.binary_thresholding(hsv_image, lower_yellow, upper_yellow)

            slope, intercept = self.image_processing.find_slope_intercept_from_binary(binary_image)

            if not np.isnan(slope) and not np.isnan(intercept):
                # Simple P-controller for steering based on lane position
                # Adjust these constants as needed for your QCar
                center_x = binary_image.shape[1] / 2
                lane_center_x = (binary_image.shape[0] - intercept) / slope if slope != 0 else center_x
                
                error = center_x - lane_center_x
                steering = np.clip(error * 0.005, -0.5, 0.5) # Proportional control
                throttle = 0.1 # Constant throttle for lane following
            else:
                throttle = 0.0
                steering = 0.0 # Stop if lane is lost

        return throttle, steering