
# QCar Agent Project

This project contains the code for an agent that controls a QCar. The agent is capable of color-based tracking, searching for objects, Lidar-based obstacle avoidance, teleoperation, image description, voice control, and has a web interface.

## Structure

- `main.py`: The main entry point for the application.
- `src/`:
    - `agent.py`: Contains the agent's logic for deciding what to do.
    - `hardware_interface.py`: Contains the low-level code for interacting with the QCar hardware.
    - `camera_processing.py`: Contains the code for processing camera images.
    - `obstacle_avoidance.py`: Contains the code for avoiding obstacles.
    - `ai_services.py`: Contains the code for interacting with the Ollama model and text-to-speech.
    - `voice_control.py`: Contains the code for listening for and interpreting voice commands.
    - `web_server.py`: Contains the Flask web server.
    - `planning.py`: Contains the path planning logic.
- `templates/`:
    - `index.html`: The HTML for the web interface.
- `tests/`:
    - `test_agent.py`: Contains unit tests for the agent.
    - `hardware_test_basic_io.py`: Tests basic I/O functionality.
    - `hardware_test_csi_cameras.py`: Tests the CSI cameras.
    - `hardware_test_gamepad.py`: Tests the gamepad.
    - `hardware_test_intelrealsense_IR.py`: Tests the Intel RealSense IR camera.
    - `hardware_test_intelrealsense.py`: Tests the Intel RealSense camera.
    - `hardware_test_rp_lidar_a2.py`: Tests the RPLIDAR A2.

## How to Run

To run the agent, execute the following command from the root of the project:

```bash
python3 onboard/main.py
```

Then, open your web browser to `http://<qcar-ip>:5000` to control the car.

### Commands

- **Web Interface:**
    - Navigate: Activate navigation mode.
    - Explore: Activate explore mode.
    - Search: Activate search mode.
    - Track: Activate track mode.
    - Stop: Stop the car.
- **Voice Commands:**
    - "navigate": Activate navigation mode.
    - "explore": Activate explore mode.
    - "describe": Describe the current view (uses the `llava:7b` model).
    - "teleop": Activate gamepad teleoperation mode.
    - "search": Activate search mode.
    - "track": Activate track mode.
    - "stop": Stop the car.
- **Keyboard Commands:**
    - `n`: Activate navigation mode.
    - `e`: Activate explore mode.
    - `d`: Describe the current view (uses the `llava:7b` model).
    - `g`: Activate gamepad teleoperation mode.
    - `s`: Activate search mode.
    - `t`: Activate track mode.
    - `space`: Stop the car.

To run the tests, execute the following command from the root of the project:

```bash
python3 -m unittest tests/test_agent.py
```

To run the hardware tests, execute the following command from the root of the project:

```bash
python3 tests/<test_file_name>.py
```
