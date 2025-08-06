import requests
import json
import os
import sys

# --- Configuration ---
# Get your API key. It's best to set this as an environment variable
# for security, but we'll put it here for simplicity.
# To set it: export GEMINI_API_KEY="your_key_here"
# api_key = os.environ.get("GEMINI_API_KEY")
api_key = "GEMINI_API_KEY" # <--- PASTE YOUR NEW API KEY HERE

if not api_key:
    print("Error: Gemini API key not found.")
    print("Please paste your key into the script or set the GEMINI_API_KEY environment variable.")
    sys.exit(1)

# The API endpoint for the Gemini-1.5 Flash model
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key

# --- Main Chat Logic ---
headers = {
    'Content-Type': 'application/json'
}

print("--- Welcome to Gemma, your in-car AI assistant! (Python 3.6 Version) ---")
print("--- Type 'quit' or 'exit' to end the chat. ---")

# Store the conversation history as a list of dictionaries
history = []

while True:
    # Get user input.
    try:
        user_input = input("You: ")
    except EOFError:
        break

    if user_input.lower() in ["quit", "exit"]:
        print("Gemma: Goodbye!")
        break

    # Add the user's message to the conversation history
    history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })

    # Prepare the data payload for the API request
    data = {
        "contents": history
    }

    try:
        # Make the POST request to the Gemini API
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        response.raise_for_status() # Raise an exception for bad status codes (like 400 or 500)

        # Extract the response text
        response_json = response.json()
        gemma_response = response_json['candidates'][0]['content']['parts'][0]['text']

        # Add Gemma's response to the history so it remembers the context
        history.append({
            "role": "model",
            "parts": [{"text": gemma_response}]
        })

        print("Gemma: " + gemma_response)

    except requests.exceptions.RequestException as e:
        print("An error occurred with the API request: {}".format(e))
    except (KeyError, IndexError) as e:
        print("Error: Could not parse the response from the API.")
        print("Full API response: {}".format(response.text))
