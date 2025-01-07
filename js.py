import speech_recognition as sr
import os
import webbrowser

# Predefined site URLs with variants
SITE_URLS = {
    "amazon": ["https://www.amazon.com", "https://www.amazon.in"],
    "youtube": ["https://www.youtube.com"],
    "google": ["https://www.google.com"],
    "wikipedia": ["https://www.wikipedia.org"],
}


def say(text):
    os.system(f"say {text}")


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source)
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("Could not request results; check your internet connection.")
            return ""
        except Exception as e:
            print(f"Error: {str(e)}")
            return ""


def open_site(query):
    for site, urls in SITE_URLS.items():
        if site in query.lower():
            # Check if the user specified a specific region like "amazon.in"
            for url in urls:
                if any(region in query.lower() for region in url.split("//")[-1].split(".")):
                    webbrowser.open(url)
                    say(f"Opening {site}")
                    return True

            # Open the first URL by default if no specific region specified
            webbrowser.open(urls[0])
            say(f"Opening {site}")
            return True
    return False  # If no site matches


if __name__ == "__main__":
    print("HIKARI")
    say("Hello, I am HIKARI, your personal AI assistant.")
    while True:
        query = takeCommand()
        if query:
            if "open" in query.lower():
                site_found = open_site(query)
                if not site_found:
                    # Fallback for unknown sites
                    say("I could not find the site. Searching on Google.")
                    google_search_url = f"https://www.google.com/search?q={query.replace('open', '').strip()}"
                    webbrowser.open(google_search_url)

            elif "exit" in query.lower() or "quit" in query.lower():
                say("Goodbye!")
                break
#mukesh 
