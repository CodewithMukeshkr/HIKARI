import speech_recognition as sr
import os
import webbrowser
import openai


def say(text):
    os.system(f"say {text}")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1.5
        try:
            audio = r.listen(source)
            query = r.recognize_google(audio, language="en-us")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError as e:
            print("Could not request results; check your internet connection.")
            return ""
        except Exception as e:
            print(f"Error: {str(e)}")
            return ""

if __name__ == "__main__":
    print("HIKARI")
    say("Hello, I am HIKARI, your personal AI assistant.")
    while True:
        query = takeCommand()
        if query:
            if query.lower().startswith("hikari"):
                query = query.lower().replace("hikari", "").strip()
            if "open" in query.lower():
                site_name = query.lower().replace("open", "").strip()
                url = f"https://www.{site_name}.com"  # Construct URL dynamically
                say(f"Opening {site_name}...")
                webbrowser.open(url)
            if "open music" in query:
                path = ""
                os.system(f"open{path}")

            elif "exit" in query.lower() or "quit" in query.lower():
                say("Goodbye!")
                break
