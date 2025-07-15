import pyttsx3
import speech_recognition as sr
import os
import re
import sys
import webbrowser
import requests
import socket
import threading
from datetime import datetime
from dotenv import load_dotenv
from model_switcher import generate_dynamic_response

load_dotenv()

# API Keys
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ------------------- Text-to-Speech ------------------- #
engine = pyttsx3.init() if sys.platform.startswith("win") else None

def say(text):
    try:
        clean_text = re.sub(r"[^\w\s:,.!?']", '', text)
        print(f"[DEBUG] Speaking: {clean_text}")

        if sys.platform == "darwin":
            os.system(f'say "{clean_text}"')
        elif sys.platform.startswith("linux"):
            os.system(f'espeak "{clean_text}"')
        elif sys.platform.startswith("win"):
            engine.say(clean_text)
            engine.runAndWait()
        else:
            print(f"[TTS]: {clean_text}")
    except Exception as e:
        print(f"[TTS Error] {e}")


# ------------------- Voice Input ------------------- #
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1.5
        r.non_speaking_duration = 0.5
        r.energy_threshold = 300
        try:
            audio = r.listen(source, timeout=5)
            query = r.recognize_google(audio, language="en-us")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            say("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            say("Could not request results; check your internet connection.")
            return ""
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return ""
        except Exception as e:
            say("An error occurred. Please try again.")
            print(f"Error: {str(e)}")
            return ""

# ------------------- Weather API ------------------- #
def get_weather(location):
    try:
        if not WEATHER_API_KEY:
            return "Weather API key not configured."
        params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get("http://api.openweathermap.org/data/2.5/weather", params=params, timeout=5)
        weather_data = response.json()
        if weather_data.get("cod") == 200:
            city = weather_data["name"]
            temp = weather_data["main"]["temp"]
            desc = weather_data["weather"][0]["description"]
            celsius = round(temp, 1)
            fahrenheit = round((celsius * 9 / 5) + 32, 1)
            return (
                f"The weather in {city} is {desc} with a temperature of "
                f"{celsius} degrees Celsius, or {fahrenheit} degrees Fahrenheit."
            )
        else:
            return f"Couldn't find weather info for {location}."
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

# ------------------- App Launching ------------------- #
def find_app(app_name):
    try:
        result = os.popen(f"mdfind 'kMDItemKind==Application' | grep -i {app_name}.app").read()
        return result.strip() if result.strip() else None
    except Exception as e:
        print(f"[App Search Error] {e}")
        return None

def open_app(app_name):
    app_path = find_app(app_name)
    if app_path:
        say(f"launching {app_name}...")
        try:
            os.system(f"open '{app_path}'")
        except Exception as e:
            say(f"Error opening {app_name}: {str(e)}")
    else:
        say(f"Sorry, I couldn't find {app_name} on this system.")

def preload_common_apps():
    common_apps = ["safari", "chrome", "spotify", "calculator", "calendar", "mail", "facetime"]
    for app in common_apps:
        _ = find_app(app)

# ------------------- Mic, DNS, and App Warmup ------------------- #
def warmup_mic_and_dns():
    try:
        # Warm up mic for fast first-time use
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
    except Exception:
        pass
    try:
        # Pre-resolve DNS to avoid first-time TLS delays
        socket.gethostbyname("api.openweathermap.org")
    except Exception:
        pass


threading.Thread(target=warmup_mic_and_dns, daemon=True).start()
threading.Thread(target=preload_common_apps, daemon=True).start()

# ------------------- Main Loop ------------------- #
if __name__ == "__main__":
    print("HIKARI - Personal AI Assistant")
    now = datetime.now().hour
    if 5 <= now < 12:
        say("Good morning, I am HIKARI, your personal AI assistant.")
    elif 12 <= now < 17:
        say("Good afternoon, I am HIKARI, your personal AI assistant.")
    else:
        say("Good evening, I am HIKARI, your personal AI assistant.")

    context = "You are HIKARI, a helpful AI assistant."
    wake_words = ["hikari", "shikari", "hickory", "bhikari"]

    while True:
        try:
            user_input = takeCommand()

            if user_input:
                print(f"Processing: {user_input}")
                lowered_input = user_input.lower()

                # Remove wake word if present
                for wake in wake_words:
                    if lowered_input.startswith(wake):
                        lowered_input = lowered_input.replace(wake, "", 1).strip()
                        break

                command = lowered_input
                handled = False

                # --- Handle "open ___ app"
                if command.startswith("open") and command.endswith("app"):
                    app = command.replace("open", "").replace("app", "").strip()
                    if app:
                        open_app(app)
                        handled = True

                # --- Handle "launch ___"
                elif command.startswith("launch"):
                    app = command.replace("launch", "").strip()
                    if app:
                        open_app(app)
                        handled = True

                # --- Handle "open ___" website
                elif command.startswith("open"):
                    site = command.replace("open", "").strip()
                    if site:
                        try:
                            webbrowser.open(f"https://www.{site}.com")
                            say(f"Opening {site} website...")
                        except Exception:
                            say(f"Error opening {site} website.")
                    handled = True

                elif "time" in command:
                    current_time = datetime.now().strftime('%I:%M %p').lstrip("0")
                    print(f"[DEBUG] Speaking: The time is {current_time}")
                    say(f"The time is {current_time}")
                    handled = True

                elif "date" in command:
                    current_date = datetime.now().strftime('%A, %d %B %Y')
                    say(f"Today is {current_date}")
                    handled = True

                elif "weather in" in command:
                    location = command.split("weather in")[-1].strip()
                    if location:
                        weather_info = get_weather(location)
                        say(weather_info)
                    else:
                        say("Please specify a location for the weather.")
                    handled = True

                elif any(keyword in command for keyword in ["exit", "quit", "goodbye", "bye"]):
                    now = datetime.now().hour
                    if 5 <= now < 12:
                        say("Goodbye! Have a great day!")
                    elif 12 <= now < 17:
                        say("Goodbye! Enjoy the rest of your day!")
                    else:
                        say("Goodbye!,sweet dreams! and have a great night")
                    break

                elif command in ["continue", "go on", "what next"]:
                    if context.strip():
                        last_user_input = context.split("\n")[-1]
                        if last_user_input.startswith("User:"):
                            command = last_user_input.replace("User:", "").strip()
                            say("Picking up from your last question...")
                        else:
                            say("I couldn't find what to continue. Please ask again.")
                            continue
                    else:
                        say("There's nothing to continue from. Please ask me something.")
                        continue

                # Use AI for everything else
                if not handled and command:
                    try:
                        response = generate_dynamic_response(command, context)
                        if response:
                            say(response)
                            print(f"HIKARI: {response}")
                            context += f"\nUser: {command}\nAI: {response}"
                        else:
                            say("I'm having trouble processing that request.")
                    except Exception as e:
                        print(f"[AI Error] {e}")
                        say("I encountered an error processing your request.")

        except KeyboardInterrupt:
            print("\nShutting down HIKARI...")
            say("Goodbye!")
            break
        except Exception as e:
            print(f"[Main Loop Error] {e}")
            continue
