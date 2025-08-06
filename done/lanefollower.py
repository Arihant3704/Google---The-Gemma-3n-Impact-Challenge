from pal.products.qcar import QCar, QCarCameras
from pal.utilities.math import Filter
from pal.utilities.gamepad import LogitechF710
from hal.utilities.image_processing import ImageProcessing
import time
import numpy as np
import cv2
import math

# Timing Parameters
sampleRate = 60
sampleTime = 1 / sampleRate
print('Sample Time:', sampleTime)

# Camera & Processing Parameters
imageWidth, imageHeight = 1640, 820
steeringFilter = Filter().low_pass_first_order_variable(25, 0.033)
next(steeringFilter)
dt = 0.033

# Initialize the CSI Camera for lane detection
myCam = QCarCameras(frameWidth=imageWidth, frameHeight=imageHeight, frameRate=sampleRate, enableFront=True)

# Initialize QCar and Gamepad
myCar = QCar()
gpad = LogitechF710()

def control_from_gamepad(LB, RT, leftLateral, A):
    """ Manual joystick control function """
    if LB:
        throttle_axis = -0.3 * RT if A else 0.3 * RT
        steering_axis = leftLateral * 0.5
    else:
        throttle_axis, steering_axis = 0, 0
    return np.array([throttle_axis, steering_axis])

try:
    while True:
        start = time.time()
       
        # Capture Image
        myCam.readAll()
        croppedRGB = myCam.csiFront.imageData[524:674, 0:820]
       
        # Convert to HSV & Threshold for Yellow Lane
        hsvBuf = cv2.cvtColor(croppedRGB, cv2.COLOR_BGR2HSV)
        binaryImage = ImageProcessing.binary_thresholding(hsvBuf, np.array([10, 50, 100]), np.array([45, 255, 255]))
       
        # Display Processed Image
        cv2.imshow('Lane Binary Image', cv2.resize(binaryImage, (410, 75)))
       
        # Extract Lane Information
        slope, intercept = ImageProcessing.find_slope_intercept_from_binary(binaryImage)
        rawSteering = 1.5 * (slope - 0.3419) + (1 / 150) * (intercept + 5)
        steering = steeringFilter.send((np.clip(rawSteering, -0.5, 0.5), dt))
       
        # Read Gamepad Inputs
        new = gpad.read()
        QCarCommand = control_from_gamepad(gpad.buttonLeft, gpad.trigger, gpad.leftJoystickX, gpad.buttonA)
       
        # Enable Lane Following when X is Pressed
        if gpad.buttonX:
            QCarCommand[1] = steering if not math.isnan(steering) else 0
            QCarCommand[0] *= np.cos(steering)
       
        # Send Command to QCar
        LEDs = np.array([0, 0, 0, 0, 0, 0, 1, 1])
        myCar.read_write_std(QCarCommand[0], QCarCommand[1], LEDs)
       
        # Loop Timing Control
        cv2.waitKey(1)
        dt = time.time() - start

except KeyboardInterrupt:
    print("User interrupted!")
finally:
    myCam.terminate()
    myCar.terminate()

