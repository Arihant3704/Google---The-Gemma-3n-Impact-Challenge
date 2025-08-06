
import time
import numpy as np
from pal.products.qcar import QCar, IS_PHYSICAL_QCAR, QCarCameras, QCarRealSense
from pal.utilities.lidar import Lidar
from pal.utilities.gamepad import LogitechF710
import cv2
import base64

if not IS_PHYSICAL_QCAR:
    import qlabs_setup
    qlabs_setup.setup()

class QCarHardwareInterface:
    def __init__(self, frequency=200):
        self.qcar = QCar(frequency=frequency)
        # Initialize all four CSI cameras for 360-degree view
        self.cameras = QCarCameras(
            enableBack=True,
            enableFront=True,
            enableLeft=True,
            enableRight=True,
        )
        self.realsense = QCarRealSense(mode='Depth')
        self.lidar = Lidar(type='RPLidar')
        self.gamepad = LogitechF710(1)

    def __enter__(self):
        self.cameras.__enter__()
        self.realsense.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.qcar.write(0.0, 0.0, np.array([0,0,0,0,0,0,0,0]))
        self.cameras.__exit__(exc_type, exc_val, exc_tb)
        self.realsense.__exit__(exc_type, exc_val, exc_tb)
        self.lidar.terminate()
        self.gamepad.terminate()

    def send_command(self, throttle, steering):
        LEDs = np.array([0, 0, 0, 0, 0, 0, 1, 1])
        if steering > 0.15:
            LEDs[0] = 1
            LEDs[2] = 1
        elif steering < -0.15:
            LEDs[1] = 1
            LEDs[3] = 1
        if throttle < 0:
            LEDs[5] = 1
        self.qcar.write(throttle, steering, LEDs)

    def read_image(self):
        self.cameras.readAll()
        # Stitch images together to create a 360-degree view
        # Assuming images are available from csiFront, csiRight, csiBack, csiLeft
        # This is a simplified stitching, actual stitching might require calibration
        front_image = self.cameras.csiFront.imageData
        right_image = self.cameras.csiRight.imageData
        back_image = self.cameras.csiBack.imageData
        left_image = self.cameras.csiLeft.imageData

        if all(img is not None for img in [front_image, right_image, back_image, left_image]):
            # Resize images to a common height if they are not already
            target_height = front_image.shape[0]
            right_image_resized = cv2.resize(right_image, (int(right_image.shape[1] * target_height / right_image.shape[0]), target_height))
            back_image_resized = cv2.resize(back_image, (int(back_image.shape[1] * target_height / back_image.shape[0]), target_height))
            left_image_resized = cv2.resize(left_image, (int(left_image.shape[1] * target_height / left_image.shape[0]), target_height))

            # Concatenate images horizontally
            stitched_image = np.concatenate((left_image_resized, front_image, right_image_resized, back_image_resized), axis=1)

            _, buffer = cv2.imencode('.jpg', stitched_image)
            return base64.b64encode(buffer).decode('utf-8')
        return None

    def read_depth_data(self):
        self.realsense.read_depth()
        return self.realsense.imageBufferDepth

    def read_lidar_data(self):
        self.lidar.read()
        return self.lidar.distances, self.lidar.angles

    def read_gamepad(self):
        new_read = self.gamepad.read()
        return new_read, self.gamepad
