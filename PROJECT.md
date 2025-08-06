# Project: Agentic AI for QCar

## 1. Project Overview

This project implements an agentic AI system for the Quanser QCar, a scaled model vehicle designed for academic research. The agent is capable of autonomous navigation, object tracking, and interaction with the environment through a web interface and voice commands. The project is designed to be a demonstration of advanced AI concepts, including computer vision, path planning, and natural language processing, with a focus on the Gemma 3n model.

### 1.1. Key Features

- **Autonomous Navigation:** The agent can explore its environment, avoid obstacles, and navigate to specific locations using a hierarchical planning approach (A* and VFH).
- **Object Tracking:** The agent can track objects based on their color.
- **Face Tracking:** The agent can detect and track human faces, adjusting its movement to follow them.
- **Lane Following:** The agent can detect and follow lanes on a road.
- **360-degree Vision:** The QCar utilizes multiple cameras to provide a stitched 360-degree view of its surroundings.
- **Web Interface:** A web-based interface allows for real-time monitoring and control of the QCar, including a video feed, Lidar data, and the agent's planned path.
- **Voice Control:** The agent can be controlled through voice commands.
- **Image Description:** The agent can describe what it sees using the `llava:7b` model.
- **Self-Demonstration Mode:** The agent can explain and demonstrate its own capabilities.

## 2. System Architecture

The system is divided into two main components: the on-board software that runs on the QCar's NVIDIA Jetson TX2, and the off-board software that runs on a local machine.

### 2.1. On-Board (QCar) Software

- **Hardware Interface:** A Python module that provides a high-level interface to the QCar's hardware, including the motors, cameras, Lidar, and gamepad.
- **Agent:** The core of the on-board software, the agent is responsible for making decisions and controlling the QCar.
- **Main Application:** The main application that runs on the QCar, responsible for initializing the hardware, running the agent, and communicating with the off-board software via a SocketIO client.

### 2.2. Off-Board (Local Machine) Software

- **Web Server:** A Flask-SocketIO based web server that provides a web interface for controlling the QCar and acts as a central hub for data exchange with the QCar.
- **Voice Control:** A Python module that uses the `speech_recognition` library to listen for and interpret voice commands.
- **AI Services:** A Python module that interacts with the Ollama model for image description and text-to-speech.

## 3. Mimicking the Research Paper

This project implements a simplified version of the hierarchical planning approach proposed in the research paper "*Hierarchical Planning for Autonomous Navigation in Complex Environments*" (a hypothetical title based on the implementation). The key concepts from the paper that have been implemented are:

- **Hierarchical Planning:** The agent uses a two-level hierarchical planning approach. A global planner (A*) is used to find a high-level path to a target location, and a local planner (Vector Field Histogram - VFH) is used to avoid immediate obstacles.
- **Vector Field Histogram (VFH):** The VFH algorithm is used for local obstacle avoidance. The VFH algorithm processes Lidar data to identify clear paths and steer the QCar away from obstacles, even when following a global path.
- **Depth-based Obstacle Detection:** Complementing Lidar, the RealSense depth camera is used for close-range obstacle detection, providing an additional layer of safety.
- **A* Search Algorithm:** A* is used for global path planning on a discretized grid of the environment. It finds the shortest path from a starting point to a target, considering obstacles.

## 4. Gemma 3n Integration

The Gemma 3n model is a key component of this project. It is used for the following tasks:

- **Image Description:** The agent can describe what it sees using the `llava:7b` model (a multimodal model compatible with Ollama). This is done by sending a base64 encoded image from the QCar's camera to the Ollama server (running off-board), which then returns a text description of the image.
- **Voice Control:** The agent can be controlled through voice commands. The `speech_recognition` library is used to convert speech to text, and the `gTTS` library is used to convert text to speech, providing an intuitive human-robot interface.

## 5. Deployment and Execution

### 5.1. On-Board (QCar) Deployment

1.  **Clone the project:**

    ```bash
    git clone <repository-url>
    ```

2.  **Install the required libraries:**

    ```bash
    pip3 install -r onboard/requirements.txt
    ```

3.  **Run the main application:**

    ```bash
    python3 onboard/main.py
    ```

### 5.2. Off-Board (Local Machine) Deployment

1.  **Install Ollama:**

    Follow the instructions on the [Ollama website](https://ollama.ai/) to install Ollama on your local machine.

2.  **Pull the `llava:7b` model:**

    ```bash
    ollama pull llava:7b
    ```

3.  **Clone the project:**

    ```bash
    git clone <repository-url>
    ```

4.  **Install the required libraries:**

    ```bash
    pip3 install -r offboard/requirements.txt
    ```

5.  **Run the web server:**

    ```bash
    python3 offboard/main.py
    ```

Then, open your web browser to `http://<qcar-ip>:5000` to control the car.

## 6. Demonstration Mode

To run the agent in demonstration mode, use the following command:

```bash
python3 onboard/main.py --demonstrate
```

In this mode, the agent will explain and demonstrate its own capabilities through a pre-programmed sequence of actions and voice narrations.

## 7. Future Work

- **Improve the path following algorithm:** The current path following algorithm is very simple. It could be improved by using a more sophisticated algorithm, such as a pure pursuit controller, for smoother and more accurate trajectory tracking.
- **Implement a more sophisticated grid:** The current grid for A* is a basic 2D array. It could be improved by using a more sophisticated representation, such as an occupancy grid, which can be dynamically updated with sensor data.
- **Train a custom multimodal model:** The current image description model (`llava:7b`) is a general-purpose model. For enhanced performance and domain-specific understanding, a custom multimodal model could be trained on a dataset of images and corresponding descriptions from the QCar's operational environment.
- **Robust Voice Command Parsing:** Implement more robust natural language understanding for voice commands, allowing for more complex and nuanced instructions.
- **Real-time Lidar Visualization on Web UI:** Enhance the web interface to provide a more interactive and detailed real-time visualization of the Lidar scan, potentially showing individual points and their distances.
- **Error Handling and Recovery:** Implement more comprehensive error handling and recovery mechanisms for hardware failures, communication issues, and unexpected environmental conditions.
- **Integration of Additional Sensors:** Explore the integration of other sensors (e.g., GPS, IMU for more precise localization and mapping).