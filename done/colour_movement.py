import time
import sys
import os
import numpy as np
import cv2
import csv
import pyttsx3
import matplotlib.pyplot as plt
from threading import Thread
from collections import deque
from Quanser.q_essential import Camera3D
from pal.products.qcar import QCar

# --- HSV Color Ranges ---
COLOR_RANGES = {
    "red": [
        (np.array([0, 120, 70]), np.array([10, 255, 255])),
        (np.array([170, 120, 70]), np.array([180, 255, 255]))
    ],
    "green": [(np.array([40, 70, 70]), np.array([80, 255, 255]))],
    "blue": [(np.array([100, 150, 0]), np.array([140, 255, 255]))]
}

# --- Settings ---
imageWidth, imageHeight = 640, 480
max_display_distance = 5.0
stop_distance = 0.25
full_speed_distance = 2.0
max_throttle = 0.08
simulationTime = 100.0

# --- CLI Color ---
if len(sys.argv) >= 2 and sys.argv[1].lower() in COLOR_RANGES:
    tracking_color = sys.argv[1].lower()
else:
    print("⚠️ No valid color passed. Defaulting to RED.")
    tracking_color = "red"

# --- Voice Setup ---
engine = pyttsx3.init()
engine.setProperty('rate', 140)
def speak(text):
    try:
        print(f"[Voice] {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[Voice ERROR] {e}")

# --- Initialize ---
myCam = Camera3D(mode='RGB&DEPTH', frame_width_RGB=imageWidth, frame_height_RGB=imageHeight)
video_out = cv2.VideoWriter('tracking_output.avi', cv2.VideoWriter_fourcc(*'XVID'), 20, (imageWidth, imageHeight))
throttle_log = deque(maxlen=500)
time_log = deque(maxlen=500)

# --- Real-time Plotting ---
def live_plot():
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_ylim(0, max_throttle * 1.2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Throttle")
    line, = ax.plot([], [], 'r-')

    while running:
        line.set_xdata(list(time_log))
        line.set_ydata(list(throttle_log))
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.1)

# --- Start Live Plot Thread ---
running = True
plot_thread = Thread(target=live_plot, daemon=True)
plot_thread.start()

# --- Track State ---
last_spoken_color = None

with QCar(readMode=1, frequency=200) as myCar:
    print(f"🚗 QCar tracking started for {tracking_color.upper()} color")
    speak(f"I am tracking {tracking_color} color")
    last_spoken_color = tracking_color
    startTime = time.time()
    log_rows = []

    try:
        while time.time() - startTime < simulationTime:
            myCam.read_RGB()
            myCam.read_depth(dataMode='m')
            frame = myCam.image_buffer_RGB.copy()
            depth = myCam.image_buffer_depth_m
            elapsed = time.time() - startTime

            # Voice update if color changed
            if tracking_color != last_spoken_color:
                speak(f"I am tracking {tracking_color} color")
                last_spoken_color = tracking_color

            # Mask for current color
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = np.zeros((imageHeight, imageWidth), dtype=np.uint8)
            for lower, upper in COLOR_RANGES[tracking_color]:
                mask |= cv2.inRange(hsv, lower, upper)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            throttle, steering = 0.0, 0.0
            LEDs = np.array([0, 0, 0, 0, 0, 0, 1, 1])

            if contours:
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) > 300:
                    x, y, w, h = cv2.boundingRect(largest)
                    cx = x + w // 2
                    cy = y + h // 2
                    obj_depth = float(depth[cy, cx])

                    if np.isfinite(obj_depth):
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, f"{tracking_color.upper()} {obj_depth:.2f}m", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                        if obj_depth > stop_distance:
                            norm = min(1.0, (obj_depth - stop_distance) / (full_speed_distance - stop_distance))
                            throttle = max_throttle * norm
                        else:
                            throttle = 0.0

                        offset = (cx - imageWidth // 2) / (imageWidth // 2)
                        steering = -0.4 * offset

                        if steering > 0.15:
                            LEDs[0] = LEDs[2] = 1
                        elif steering < -0.15:
                            LEDs[1] = LEDs[3] = 1

            # Control + Write
            myCar.read()
            myCar.write(throttle, steering, LEDs)
            video_out.write(frame)

            # Overlay
            cv2.putText(frame, f"Tracking: {tracking_color.upper()}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow("Tracking", frame)
            cv2.imshow("Depth", np.clip(depth / max_display_distance, 0, 1))

            # Log
            throttle_log.append(throttle)
            time_log.append(elapsed)
            log_rows.append([elapsed, tracking_color, throttle, steering])

            # Key switch
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                tracking_color = "red"
            elif key == ord('g'):
                tracking_color = "green"
            elif key == ord('b'):
                tracking_color = "blue"

    except KeyboardInterrupt:
        print("🛑 Stopped manually.")

    finally:
        running = False
        video_out.release()
        myCam.terminate()
        cv2.destroyAllWindows()
        with open("qcar_log.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Time (s)", "Color", "Throttle", "Steering"])
            writer.writerows(log_rows)
        print("✅ Log saved: qcar_log.csv")
        print("🎥 Video saved: tracking_output.avi")

