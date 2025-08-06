import ollama
from gtts import gTTS
import pygame
import os
import base64
import threading

class AIServices:
    def __init__(self):
        pygame.mixer.init()

    def describe_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            response = ollama.chat(
                model='llava:7b',
                messages=[
                    {
                        'role': 'user',
                        'content': 'Describe this image in detail.',
                        'images': [encoded_string]
                    },
                ]
            )
            return response['message']['content']
        except Exception as e:
            return f"Error describing image: {e}"

    def _play_audio(self, file_path):
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            os.remove(file_path)
        except Exception as e:
            print(f"Error playing audio: {e}")

    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang='en')
            file_path = "response.mp3"
            tts.save(file_path)
            
            # Play audio in a separate thread to avoid blocking
            audio_thread = threading.Thread(target=self._play_audio, args=(file_path,))
            audio_thread.start()
        except Exception as e:
            print(f"Error in text-to-speech: {e}")