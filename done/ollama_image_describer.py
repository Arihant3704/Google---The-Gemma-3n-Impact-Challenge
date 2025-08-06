import requests
import base64
import json
import os
from gtts import gTTS

def describe_image_with_ollama(image_path, model_name="llava:7b", ollama_url="http://localhost:11434/api/generate"):
    """
    Sends an image to a local Ollama instance for description.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at '{image_path}'")
        return None

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return None

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "prompt": "As a QCar, describe what you see in this image.",
        "images": [base64_image]
    }

    try:
        response = requests.post(ollama_url, headers=headers, data=json.dumps(payload), stream=True)
        response.raise_for_status()

        full_response_content = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line)
                    if "response" in json_response:
                        full_response_content += json_response["response"]
                    elif "error" in json_response:
                        print(f"Ollama Error: {json_response['error']}")
                        return None
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from line: {line.decode('utf-8')}")
                    return None
        return {"response": full_response_content}
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Ollama at {ollama_url}. Is Ollama running?")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None


def speak_and_save_text(text, filename="description.mp3"):
    """
    Convert text to speech, save as MP3, and play it.
    """
    try:
        tts = gTTS(text)
        tts.save(filename)
        print(f"Audio saved to {filename}")

        # Play it using mpg123 (Linux/macOS) or use another tool if needed
        os.system(f"mpg123 {filename}")  # Use playsound or VLC if on Windows
    except Exception as e:
        print(f"Error in TTS: {e}")


if __name__ == "__main__":
    image_file = "/home/arihant/Downloads/captured.jpg"

    print(f"Attempting to describe image: {image_file}")
    result = describe_image_with_ollama(image_file, model_name="llava:7b")

    if result:
        print("\nOllama Response:")
        full_response = ""

        if "response" in result:
            full_response = result["response"]
        elif "responses" in result:
            for res_part in result["responses"]:
                if "response" in res_part:
                    full_response += res_part["response"]

        if full_response:
            print(full_response)
            speak_and_save_text(full_response)  # Speak and save as audio
        else:
            print(json.dumps(result, indent=2))
    else:
        print("Failed to get a description from Ollama.")

