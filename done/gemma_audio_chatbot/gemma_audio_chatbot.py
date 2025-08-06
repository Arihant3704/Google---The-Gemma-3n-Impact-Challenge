import requests
import json
import os
import sys
import speech_recognition as sr
from gtts import gTTS


# --- Configuration ---
# Get your API key. It's best to set this as an environment variable
# for security, but we'll put it here for simplicity.
# To set it: export GEMINI_API_KEY="your_key_here"
# api_key = os.environ.get("GEMINI_API_KEY")
# --- Library Configuration ---
# The 'playsound' library is used to play the generated audio.
# If it fails, we will fall back to the system's 'espeak' command.

try:
    import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    print("Warning: 'playsound' module not found. Falling back to 'espeak' for audio output.")
    PLAYSOUND_AVAILABLE = False

# --- API and Model Configuration ---
# IMPORTANT: Paste your new Gemini API key here.
api_key = "GEMINI_API_KEY"

# The API endpoint for the Gemini model
gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key

# --- Core Functions ---

def speak(text):
    """Converts text to speech and plays it."""
    try:
        print(f"Gemma: {text}")
        tts = gTTS(text=text, lang='en')
        filename = "response.mp3"
        tts.save(filename)

        if PLAYSOUND_AVAILABLE:
            playsound.playsound(filename)
        else:
            # Fallback for systems where playsound has issues
            os.system(f'espeak -s 150 "{text}"')
            
        os.remove(filename) # Clean up the audio file

    except Exception as e:
        print(f"Error in text-to-speech module: {e}")
        # A final fallback if gTTS also fails
        os.system(f'espeak -s 150 "{text}"')

def listen_for_command():
    """
    Listens for a command from the microphone, converts it to text,
    and returns the recognized text. Includes robust error handling.
    """
    r = sr.Recognizer()

    # --- Crucial settings for noise cancellation ---
    # This is the most important setting to adjust.
    # Higher value = less sensitive to background noise. Try 300, 500, 1000, or 4000.
    r.energy_threshold = 500 
    
    # If the recognizer is too slow to stop listening after you speak, decrease this value.
    r.pause_threshold = 0.8
    r.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("\n" + "="*40)
        print("Calibrating for ambient noise...")
        # Automatically adjust energy threshold based on ambient noise
        r.adjust_for_ambient_noise(source, duration=1)
        
        print("Listening for your command...")
        try:
            # Listen for the first phrase and extract it into audio data
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("DEBUG: Listening timed out while waiting for phrase to start.")
            return ""

    try:
        print("Recognizing speech...")
        # Use Google's online speech recognition
        command = r.recognize_google(audio).lower()
        print(f"DEBUG: Successfully recognized -> '{command}'")
        return command
        
    except sr.UnknownValueError:
        print("DEBUG: Google Speech Recognition could not understand the audio.")
        return "" # Return empty string if speech is unintelligible
        
    except sr.RequestError as e:
        print(f"DEBUG: Could not request results from Google service; {e}")
        return "" # Return empty string on network error
        
    except Exception as e:
        print(f"DEBUG: An unexpected error occurred in speech recognition: {e}")
        return ""

def main():
    """Main function to run the interactive chatbot loop."""
    if not api_key or "YOUR_NEW_API_KEY" in api_key:
        print("Error: Gemini API key is not set.")
        print("Please open the script and replace 'YOUR_NEW_API_KEY' with your actual key.")
        sys.exit(1)
        
    # --- Main Chat Logic ---
    headers = {'Content-Type': 'application/json'}
    # Store the conversation history
    history = []

    # Initial greeting
    speak("Hello, I am Gemma, your in-car AI assistant. How can I help you?")

    while True:
        # Get user command from the microphone
        user_input = listen_for_command()

        # If nothing was recognized, or an error occurred, loop back and listen again.
        if not user_input:
            continue

        # Check for exit commands
        if any(cmd in user_input for cmd in ["goodbye", "exit", "quit", "stop"]):
            speak("Goodbye!")
            break

        # Add user's message to conversation history for context
        history.append({"role": "user", "parts": [{"text": user_input}]})

        # Prepare the data for the API request
        data = {"contents": history}

        try:
            # Send the request to the Gemini API
            response = requests.post(gemini_url, headers=headers, data=json.dumps(data), timeout=20)
            response.raise_for_status() # Raise an exception for bad status codes (4xx/5xx)

            # Extract the response text
            response_json = response.json()
            gemma_response = response_json['candidates'][0]['content']['parts'][0]['text']

            # Add Gemma's response to history to maintain conversation flow
            history.append({"role": "model", "parts": [{"text": gemma_response}]})

            # Speak the response
            speak(gemma_response)

        except requests.exceptions.RequestException as e:
            speak("Sorry, I'm having trouble connecting to the network right now.")
            print(f"API Request Error: {e}")
        except (KeyError, IndexError):
            speak("I received a response I couldn't quite understand. Please try again.")
            print(f"API Response Parsing Error. Full response: {response.text}")

if __name__ == "__main__":
    main()
