
import speech_recognition as sr

class VoiceControl:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen_for_command(self):
        with sr.Microphone() as source:
            print("Listening for a command...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            command = self.recognizer.recognize_google(audio).lower()
            print(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None
