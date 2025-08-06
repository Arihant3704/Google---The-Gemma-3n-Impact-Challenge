

import time
from src.hardware_interface import QCarHardwareInterface
from src.agent import Agent
from src.ai_services import AIServices
from src.voice_control import VoiceControl
from src.socket_client import SocketClient
from src.demonstration import Demonstration
import cv2
import threading
import argparse
import json
import numpy as np
import base64

class MainApplication:
    def __init__(self, demonstrate=False):
        self.command = "stop"
        self.hardware = QCarHardwareInterface()
        # Create a simple grid for the A* algorithm
        self.grid = [[0 for _ in range(10)] for _ in range(10)]
        self.agent = Agent(self.hardware.cameras.csiFront.imageData.shape[1], self.hardware.cameras.csiFront.imageData.shape[0], self.grid)
        self.ai_services = AIServices()
        self.voice_control = VoiceControl()
        self.socket_client = SocketClient('http://localhost:5000') # Assuming offboard server runs on localhost:5000
        self.demonstration = Demonstration(self)
        self.run_demonstration_flag = demonstrate

    def voice_command_thread(self):
        while True:
            command = self.voice_control.listen_for_command()
            if command:
                self.command = command

    def socket_client_thread(self):
        self.socket_client.connect()
        self.socket_client.start_background_task()
        while True:
            # Process commands from the web interface
            web_command = self.socket_client.get_latest_command()
            if web_command:
                self.command = web_command
            time.sleep(0.1) # Small delay to prevent busy-waiting

    def run(self):
        if self.run_demonstration_flag:
            self.demonstration.run()
        else:
            self.run_normal()

    def run_normal():
        voice_thread = threading.Thread(target=self.voice_command_thread)
        voice_thread.daemon = True
        voice_thread.start()

        socket_thread = threading.Thread(target=self.socket_client_thread)
        socket_thread.daemon = True
        socket_thread.start()

        print("QCar agent started. Open your web browser to http://<qcar-ip>:5000 to control the car.")

        try:
            while True:
                # Non-blocking input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('n'):
                    self.command = "navigate"
                    print("Command: navigate")
                elif key == ord('e'):
                    self.command = "explore"
                    print("Command: explore")
                elif key == ord('d'):
                    # Save the current image to a file
                    image_data = self.hardware.read_image()
                    if image_data:
                        # Decode base64 for local display
                        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        cv2.imwrite("current_view.png", image)
                        description = self.ai_services.describe_image("current_view.png")
                        print(f"Description: {description}")
                        self.ai_services.text_to_speech(description)
                elif key == ord('g'):
                    self.command = "teleop"
                    print("Command: teleop")
                elif key == ord('s'):
                    self.command = "search"
                    print("Command: search")
                elif key == ord('t'):
                    self.command = "track"
                    print("Command: track")
                elif key == ord('f'):
                    self.command = "face_track"
                    print("Command: face_track")
                elif key == ord('l'):
                    self.command = "lane_follow"
                    print("Command: lane_follow")
                elif key == ord(' '):
                    self.command = "stop"
                    print("Command: stop")

                image_data = self.hardware.read_image()
                depth_data = self.hardware.read_depth_data()
                lidar_distances, lidar_angles = self.hardware.read_lidar_data()
                gamepad_new_read, gamepad = self.hardware.read_gamepad()

                # Send data to offboard server
                if image_data:
                    self.socket_client.send_video_frame(image_data)
                if lidar_distances is not None and lidar_angles is not None:
                    self.socket_client.send_lidar_data({'distances': lidar_distances.tolist(), 'angles': lidar_angles.tolist()})
                self.socket_client.send_status_update({'state': self.agent.state})

                # Decode image for local display
                if image_data:
                    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    cv2.imshow("Camera Feed", image)
                
                throttle, steering = self.agent.get_action(self.command, image, depth_data, lidar_distances, lidar_angles, gamepad_new_read, gamepad, target_location=(9, 9))
                self.hardware.send_command(throttle, steering)

                # Handle description request from agent
                if self.agent.request_description:
                    image_data_for_desc = self.hardware.read_image()
                    if image_data_for_desc:
                        nparr_desc = np.frombuffer(base64.b64decode(image_data_for_desc), np.uint8)
                        image_desc = cv2.imdecode(nparr_desc, cv2.IMREAD_COLOR)
                        cv2.imwrite("current_view.png", image_desc)
                        description = self.ai_services.describe_image("current_view.png")
                        print(f"Description: {description}")
                        self.ai_services.text_to_speech(description)
                
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nExiting agent. Stopping the car.")
        finally:
            cv2.destroyAllWindows()
            self.hardware.__exit__(None, None, None)
            self.socket_client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demonstrate", action="store_true", help="Run the agent in demonstration mode.")
    args = parser.parse_args()

    app = MainApplication(demonstrate=args.demonstrate)
    app.run()
