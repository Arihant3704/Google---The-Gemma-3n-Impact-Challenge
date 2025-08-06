import time
import cv2
import csv
import numpy as np
from Quanser.q_essential import Camera3D
from pal.products.qcar import QCar

# --- Settings ---
imageWidth, imageHeight = 640, 480
stop_distance = 0.25
full_speed_distance = 1.5
max_throttle = 0.07
max_display_distance = 5.0
simulationTime = 100.0

# --- Load OpenCV Haar face detector ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# --- Initialize camera ---
cam = Camera3D(mode='RGB&DEPTH', frame_width_RGB=imageWidth, frame_height_RGB=imageHeight)

# --- Video recording setup ---
video_out = cv2.VideoWriter('face_tracking_output.avi',
                            cv2.VideoWriter_fourcc(*'XVID'),
                            20.0,
                            (imageWidth, imageHeight))

# --- QCar initialization ---
with QCar(readMode=1, frequency=200) as car:
    print("🚗 QCar face tracking (OpenCV + Recording) started.")
    startTime = time.time()
    log_rows = []

    try:
        while time.time() - startTime < simulationTime:
            cam.read_RGB()
            cam.read_depth(dataMode='m')
            frame = cam.image_buffer_RGB.copy()
            depth = cam.image_buffer_depth_m
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # --- Detect face(s) ---
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

            throttle, steering = 0.0, 0.0
            LEDs = np.array([0, 0, 0, 0, 0, 0, 1, 1])

            if len(faces) > 0:
                # Take the largest face (assumed closest)
                x, y, w, h = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)[0]
                cx = x + w // 2
                cy = y + h // 2
                obj_depth = float(depth[cy, cx])

                # Draw box and label
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame, f"Depth: {obj_depth:.2f} m", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # --- Movement Logic ---
                if np.isfinite(obj_depth) and obj_depth > stop_distance:
                    norm = min(1.0, (obj_depth - stop_distance) / (full_speed_distance - stop_distance))
                    throttle = max_throttle * norm

                    offset = (cx - imageWidth // 2) / (imageWidth // 2)
                    steering = -0.4 * offset

                    if steering > 0.15:
                        LEDs[0] = LEDs[2] = 1
                    elif steering < -0.15:
                        LEDs[1] = LEDs[3] = 1

            # --- Apply QCar control ---
            car.read()
            car.write(throttle, steering, LEDs)

            # --- Record video ---
            video_out.write(frame)

            # --- Display ---
            cv2.putText(frame, f"Throttle: {throttle:.2f}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.imshow("QCar Face Tracking (OpenCV)", frame)
            cv2.imshow("Depth", np.clip(depth / max_display_distance, 0, 1))

            # --- Log ---
            log_rows.append([time.time() - startTime, throttle, steering])

            # --- Controls ---
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        print("🛑 Stopped manually.")

    finally:
        cam.terminate()
        cv2.destroyAllWindows()
        video_out.release()
        with open("face_tracking_opencv_log.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Time (s)", "Throttle", "Steering"])
            writer.writerows(log_rows)
        print("✅ Log saved: face_tracking_opencv_log.csv")
        print("🎥 Video saved: face_tracking_output.avi")

