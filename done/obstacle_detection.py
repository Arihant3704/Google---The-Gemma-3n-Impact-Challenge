import time
import numpy as np
import cv2
import csv
from Quanser.q_essential import Camera3D
from pal.products.qcar import QCar

# --- Settings ---
imageWidth, imageHeight = 640, 480
obstacle_threshold = 0.25  # meters
scan_box_width = 120
scan_box_height = 80
default_throttle = 0.06
simulationTime = 100.0
max_display_distance = 3.0

# --- Initialize camera ---
cam = Camera3D(mode='RGB&DEPTH', frame_width_RGB=imageWidth, frame_height_RGB=imageHeight)

# --- Obstacle detection area ---
box_x1 = imageWidth // 2 - scan_box_width // 2
box_x2 = imageWidth // 2 + scan_box_width // 2
box_y1 = imageHeight // 2 - scan_box_height // 2
box_y2 = imageHeight // 2 + scan_box_height // 2

# --- QCar Init ---
with QCar(readMode=1, frequency=200) as car:
    print("🚗 QCar obstacle detection started.")
    startTime = time.time()
    log_rows = []

    try:
        while time.time() - startTime < simulationTime:
            # Read sensor data
            cam.read_RGB()
            cam.read_depth(dataMode='m')
            rgb = cam.image_buffer_RGB.copy()
            depth = cam.image_buffer_depth_m

            # Crop depth area for obstacle scan
            obstacle_area = depth[box_y1:box_y2, box_x1:box_x2]
            min_depth = np.nanmin(obstacle_area)

            # Determine throttle
            if np.isfinite(min_depth) and min_depth < obstacle_threshold:
                throttle = 0.0
                label = f"Obstacle at {min_depth:.2f} m → STOP"
            else:
                throttle = default_throttle
                label = "Path clear → MOVING"

            # Control
            steering = 0.0
            LEDs = np.array([0, 0, 0, 0, 0, 0, 1, 1])
            car.read()
            car.write(throttle, steering, LEDs)

            # Visualization
            cv2.rectangle(rgb, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 255), 2)
            cv2.putText(rgb, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 255) if throttle > 0 else (0, 0, 255), 2)

            cv2.imshow("Obstacle Detection", rgb)
            cv2.imshow("Depth", np.clip(depth / max_display_distance, 0, 1))

            # Logging
            log_rows.append([time.time() - startTime, min_depth, throttle])

            # Quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        print("🛑 Interrupted.")

    finally:
        cam.terminate()
        cv2.destroyAllWindows()
        with open("obstacle_log.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Time (s)", "Min Depth (m)", "Throttle"])
            writer.writerows(log_rows)
        print("✅ Log saved: obstacle_log.csv")

