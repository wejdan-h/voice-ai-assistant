# -*- coding: utf-8 -*-

import os

# Prevent OpenMP duplicate library errors on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


import sys
import time
import warnings
import cohere
import speech_recognition as sr
import whisper

from dotenv import load_dotenv
from gtts import gTTS
import pygame



# Suppress unnecessary warnings
warnings.filterwarnings("ignore")

# Configure UTF-8 output encoding
sys.stdout.reconfigure(encoding="utf-8")



# Load API credentials from environment variables
load_dotenv()

api_key = os.getenv("COHERE_API_KEY")

if not api_key:
    raise ValueError("COHERE_API_KEY not found")


# Initialize Cohere client
co = cohere.ClientV2(api_key)



# Initialize Whisper speech recognition model
print("Loading Whisper model...")

stt_model = whisper.load_model("small")



# =========================
# Speech-to-Text Processing
# =========================

def listen_and_transcribe():

    recognizer = sr.Recognizer()

    # Configure microphone sensitivity settings
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    try:

        with sr.Microphone() as source:

            print("\n🎤 Listening...")

            # Adjust microphone input based on surrounding noise
            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            # Capture user voice input
            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=10
            )


        print("🔄 Processing...")


        # Save recorded audio temporarily
        filename = "temp.wav"

        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())


        # Convert speech audio into text using Whisper
        result = stt_model.transcribe(
            filename,
            language="ar",
            fp16=False
        )


        text = result["text"].strip()


        # Remove temporary audio file
        if os.path.exists(filename):
            os.remove(filename)


        print("You said:", text)

        return text


    except sr.WaitTimeoutError:

        print("No speech detected")
        return None


    except KeyboardInterrupt:

        stop_program()


    except Exception as e:

        print("Speech error:", e)
        return None




# =========================
# Text-to-Speech Processing
# =========================

def speak_text(text):

    try:

        filename = "answer.mp3"


        # Convert generated text response into speech
        tts = gTTS(
            text=text,
            lang="ar"
        )

        tts.save(filename)


        # Play generated audio response
        pygame.mixer.init()

        pygame.mixer.music.load(filename)

        pygame.mixer.music.play()


        while pygame.mixer.music.get_busy():

            time.sleep(0.1)


        pygame.mixer.music.stop()

        pygame.mixer.quit()


        # Remove temporary audio file
        if os.path.exists(filename):
            os.remove(filename)


    except KeyboardInterrupt:

        stop_program()


    except Exception as e:

        print("TTS Error:", e)




# =========================
# Application Shutdown
# =========================

def stop_program():

    print("\nAssistant stopped.")

    try:

        pygame.mixer.quit()

    except:

        pass


    # Force application termination
    os._exit(0)




# =========================
# Main Application Loop
# =========================

if __name__ == "__main__":


    print("\n===== Voice AI Assistant Started =====")


    while True:


        try:


            # Receive and transcribe user voice input
            user_input = listen_and_transcribe()


            if not user_input:
                continue



            # Normalize Arabic characters for command matching
            cleaned = user_input.lower()

            cleaned = cleaned.replace(
                "إ",
                "ا"
            ).replace(
                "أ",
                "ا"
            ).replace(
                "آ",
                "ا"
            )


            # Supported exit commands
            exit_words = [
                
                "مع السلامة",
                "stop",
                "exit",
                "bye"

            ]


            # Check if user requested to stop the assistant
            if any(word in cleaned for word in exit_words):

                speak_text(
                    "مع السلامة، أتمنى لك يوما سعيدا"
                )

                stop_program()



            print("\n🤖 Generating response...")


            # Generate AI response using Cohere LLM
            response = co.chat(

                model="command-r-08-2024",

                messages=[

                    {

                        "role": "user",

                        "content": user_input

                    }

                ],

                max_tokens=150

            )


            answer = response.message.content[0].text.strip()


            print(
                "AI:",
                answer
            )


            # Convert AI response into audio output
            speak_text(answer)



        except KeyboardInterrupt:

            stop_program()



        except Exception as e:

            print(
                "Unexpected error:",
                e
            )
