import os
import base64

def test_curl():
    image_path = "/home/arihant/Downloads/down.jpeg"
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    curl_command = f"""\
    curl http://localhost:11434/api/chat -d '{{
      "model": "llava:7b",
      "messages": [
        {{
          "role": "user",
          "content": "Describe this image in detail.",
          "images": ["{encoded_string}"]
        }}
      ],
      "stream": false
    }}'"""

    os.system(curl_command)

if __name__ == "__main__":
    test_curl()
