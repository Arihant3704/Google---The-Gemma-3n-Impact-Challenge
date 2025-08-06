# QCar Agent: Standalone Scripts Submission

## 1. Project Overview

This folder contains a collection of standalone Python scripts that demonstrate the core functionalities of an agentic AI system for the Quanser QCar. Each script is designed to be run independently and showcases a specific capability, from computer vision-based tracking to interaction with large language models.

This submission focuses on the successfully implemented and tested components of the project.

## 2. Implemented Features (Standalone Scripts)

This submission includes the following fully functional, standalone scripts:

*   **`colour_movement.py`**: Tracks an object of a specified color (red, green, or blue) and controls the QCar to follow it.
*   **`face_tracking.py`**: Uses OpenCV to detect and track a human face, guiding the QCar to keep the face centered.
*   **`obstacle_detection.py`**: Employs the QCar's depth camera to identify and stop for obstacles directly in its path.
*   **`lanefollower.py`**: A script designed to make the QCar detect and follow lanes on a surface.
*   **`Imaging_360.py`**: Stitches the video feeds from the QCar's four CSI cameras into a single, panoramic 360-degree view.
*   **`ollama_image_describer.py`**: Captures an image, sends it to a local Ollama instance (running the LLaVA model), and uses text-to-speech to verbally describe what the QCar sees.
*   **`project_chatbot.py`**: A terminal-based chatbot that uses a local Gemma model to answer questions about the project, using the project's documentation as context.
*   **`gemma_audio_chatbot/`**: A self-contained, voice-enabled chatbot that uses the Gemini API for conversational AI, complete with speech-to-text and text-to-speech.

## 3. Setup and Execution

### 3.1. Prerequisites

1.  **Install Python Libraries:** Navigate to this `done` directory and install all required libraries:
    ```bash
    cd done
    pip install -r requirements.txt
    ```

2.  **Install Ollama (for AI scripts):** For the `ollama_image_describer.py` and `project_chatbot.py` scripts, you must have Ollama installed and running on your machine. Follow the instructions on the [Ollama website](https://ollama.ai/).

3.  **Download AI Models:** Pull the required models for the AI scripts:
    ```bash
    ollama pull llava:7b
    ollama pull gemma:7b 
    ```

### 3.2. Running the Scripts

Each script is designed to be run from the terminal. Here are the instructions for each one.

--- 

#### **Color Tracking**

This script makes the QCar follow an object of the specified color.

```bash
# To track red (default)
python3 colour_movement.py

# To specify a color (red, green, or blue)
python3 colour_movement.py green
```

--- 

#### **Face Tracking**

This script makes the QCar follow a human face.

```bash
python3 face_tracking.py
```

--- 

#### **Obstacle Detection**

This script makes the QCar move forward and stop when it detects an obstacle.

```bash
python3 obstacle_detection.py
```

--- 

#### **Lane Follower**

This script makes the QCar follow lanes.

```bash
python3 lanefollower.py
```

--- 

#### **360-Degree Imaging**

This script displays the combined 360-degree camera view from the QCar.

```bash
python3 Imaging_360.py
```

--- 

#### **Ollama Image Describer**

This script takes a local image, gets a description from Ollama, and speaks it.

*Note: You must edit the `image_file` path inside the script to point to an image on your machine.*

```bash
python3 ollama_image_describer.py
```

--- 

#### **Project Chatbot**

This script starts a terminal-based chatbot that can answer questions about the project.

*Note: You may need to edit the `project_path` inside the script to the correct location.*

```bash
python3 project_chatbot.py
```

--- 

#### **Gemma Audio Chatbot**

This script runs a voice-controlled chatbot using the Gemini API.

*Note: You must paste your Gemini API key into the `gemma_audio_chatbot.py` script.*

```bash
cd gemma_audio_chatbot
python3 gemma_audio_chatbot.py
```
