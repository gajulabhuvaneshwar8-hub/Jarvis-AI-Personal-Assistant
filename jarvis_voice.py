"""
jarvis_voice.py - Live Speech Recognition & Audio Response Loop
Listens continuously through your microphone, processes commands, and speaks back.
"""

import sys
import os
import subprocess
import time
import speech_recognition as sr
import jarvis_brain


def speak(text):
    """Speaks output aloud using native macOS speech or prints if headless."""
    if not text:
        return
    print(f"\n[JARVIS]: {text}\n")
    if sys.platform == "darwin":
        # Native macOS high-speed, natural voice
        subprocess.run(["say", "-v", "Samantha", text])
    else:
        # Cross-platform fallback
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass


def listen_loop():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    try:
        mic = sr.Microphone()
    except Exception as e:
        print(f"Error accessing microphone: {e}")
        print("Falling back to text console input mode.")
        while True:
            try:
                user_input = input("You: ")
                if user_input.strip():
                    reply = jarvis_brain.think(user_input)
                    speak(reply)
            except (KeyboardInterrupt, EOFError):
                break
        return

    with mic as source:
        print("\n" + "=" * 50)
        print("  JARVIS AI ASSISTANT IS ACTIVE AND LISTENING")
        print("  Say commands like:")
        print("    - 'Jarvis, open VS Code'")
        print("    - 'Play lofi on YouTube'")
        print("    - 'Stock market update' / 'Analyze Nifty'")
        print("    - 'Send WhatsApp message'")
        print("    - 'Read unread emails'")
        print("=" * 50 + "\n")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)

    while True:
        try:
            with mic as source:
                print("Listening... ", end="", flush=True)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
            print("Processing... ", end="", flush=True)

            query = recognizer.recognize_google(audio).strip()
            print(f"\nYou said: \"{query}\"")

            # Wake word filter (optional - answers directly or to "Jarvis")
            q_clean = query.lower()
            if "jarvis" in q_clean:
                q_clean = q_clean.replace("jarvis", "").strip(" ,.!?")

            if not q_clean:
                speak("Yes sir, I'm listening.")
                continue

            response = jarvis_brain.think(q_clean)
            speak(response)

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except KeyboardInterrupt:
            print("\nShutting down Jarvis. Goodbye!")
            break
        except Exception as e:
            print(f"\n[Notice]: {e}")
            time.sleep(0.5)


if __name__ == "__main__":
    listen_loop()
