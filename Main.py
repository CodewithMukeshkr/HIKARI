import speech_recognition as sr
import os
import webbrowser
import requests
from datetime import datetime
import cohere
import shlex
from dotenv import load_dotenv

load_dotenv()

#Cohere API Configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
cohere_client = cohere.Client(COHERE_API_KEY)

# Weather API Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Text-to-Speech function
def say(text):
    sanitized_text = shlex.quote(text)
    os.system(f'say "{sanitized_text}"')

# Voice function
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 2.5
        r.non_speaking_duration = 1
        r.energy_threshold = 300
        try:
            audio = r.listen(source)
            kuery = r.recognize_google(audio, language="en-us")
            print(f"User said: {kuery}")
            return kuery
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            say("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError as e:
            print("Could not request results; check your internet connection.")
            say("Sorry, I didn't catch that.")
            return ""
        except Exception as e:
            print(f"Error: {str(e)}")
            say("An error occurred. Please try again.")
            return ""

# Weather function
def get_weather(location):
    try:
        params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get(WEATHER_BASE_URL, params=params)
        weather_data = response.json()

        if weather_data.get("cod") == 200:
            city = weather_data["name"]
            temp = weather_data["main"]["temp"]
            weather_desc = weather_data["weather"][0]["description"]
            return f"The weather in {city} is currently {weather_desc} with a temperature of {temp}°C."
        else:
            return f"Sorry, I couldn't find weather information for {location}."
    except Exception as e:
        return f"An error occurred while fetching weather data: {str(e)}"

# Cohere AI
def generate_response(prompt):
    try:
        response = cohere_client.generate(
            model="command",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
            stop_sequences=["\n"]
        )
        if response.generations and response.generations[0].text:
            return response.generations[0].text.strip()
        else:
            return "Sorry, I couldn't generate a response at this time."
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while generating a response."

def truncate_context(context, max_length=1500):
    if len(context) > max_length:
        return context[-max_length:]
    return context


# Check if an app exists and return its path
def find_app(app_name):
    normalized_app_name = app_name.lower()
    result = os.popen(f"mdfind 'kMDItemKind==Application' | grep -i {normalized_app_name}.app").read()
    if result.strip():
        return result.strip()  # Return the app's path
    else:
        return None

# Open a specific app
def open_app(app_name):
    app_path = find_app(app_name)
    if app_path:
        say(f"Opening {app_name}...")
        os.system(f"open '{app_path}'")
    else:
        say(f"Sorry, I couldn't find {app_name} on this system.")


if __name__ == "__main__":
    print("HIKARI")
    say("Hello, I am HIKARI, your personal AI assistant.")
    context = "You are HIKARI, a helpful AI assistant designed to assist the user in various tasks."

    while True:
        kari = takeCommand()
        if kari:
            if kari.lower().startswith("hikari"):
                kari = kari.lower().replace("hikari", "").strip()

            do = False

            # open sites
            if "open" in kari.lower():
                site_name = kari.lower().replace("open", "").strip()
                url = f"https://www.{site_name}.com"
                say(f"Opening {site_name}...")
                webbrowser.open(url)
                do = True

            # App
            elif "launch" in kari.lower():
                app_name = kari.lower().replace("launch", "").strip()
                open_app(app_name)
                do = True

            # time
            elif "time" in kari:
                time = datetime.now().strftime("%H:%M %p")
                say(f"The time is {time} o'clock.")
                do = True

            # date
            elif "date" in kari:
                date = datetime.now().strftime("%A, %d %B %Y")
                say(f"Today is {date}")
                do = True

            # weather
            elif "weather in" in kari.lower():
                location = kari.lower().split("weather in")[-1].strip()
                if location:
                    weather = get_weather(location)
                    say(weather)
                else:
                    say("I couldn't understand the location. Please try again.")
                do = True

            # exit
            elif any(keyword in kari.lower() for keyword in ["exit", "quit", "goodbye", "bye"]):
                print("Goodbye!")
                say("Goodbye!")
                break

            if not do:
                # Dynamic response generation
                prompt = f"Context: {context}\nUser: {kari}\nAI:"
                response = generate_response(prompt)
                say(response)
                print(f"HIKARI: {response}")
                context = truncate_context(context)
                context += f"\nUser: {kari}\nAI: {response}"



