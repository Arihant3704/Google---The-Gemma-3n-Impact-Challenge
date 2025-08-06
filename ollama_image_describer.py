import requests
import base64
import json
import os

def describe_image_with_ollama(image_path, model_name="gemma3n:e4b", ollama_url="http://localhost:11434/api/generate"):
    """
    Sends an image to a local Ollama instance for description.

    Args:
        image_path (str): The absolute path to the image file.
        model_name (str): The name of the Ollama model to use (e.g., "gemma3n:e4b", "llava:7b").
        ollama_url (str): The URL of your local Ollama API endpoint.

    Returns:
        dict: The JSON response from Ollama, or None if an error occurred.
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
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

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

if __name__ == "__main__":
    image_file = "/home/arihant/Downloads/istockphoto-1157655660-1024x1024.jpg"
    
    print(f"Attempting to describe image: {image_file}")
    result = describe_image_with_ollama(image_file, model_name="llava:7b")

    if result:
        print("\nOllama Response:")
        # Ollama often streams responses, so we might get multiple 'response' fields
        # We'll concatenate them for a complete description
        full_response = ""
        if "response" in result:
            full_response = result["response"]
        elif "responses" in result: # Some models might return a list of responses
            for res_part in result["responses"]:
                if "response" in res_part:
                    full_response += res_part["response"]
        
        if full_response:
            print(full_response)
        else:
            print(json.dumps(result, indent=2)) # Print raw JSON if no 'response' field
    else:
        print("Failed to get a description from Ollama.")
