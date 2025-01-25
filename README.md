# HIKARI - Personal AI Assistant

HIKARI is a personal AI assistant that can respond to voice commands, open websites, check the weather, and much more.

## Features
- Voice-based interaction
- Weather updates
- Opens websites and apps
- Tells time and date
- Dynamic AI responses using Cohere API

## Installation
1. Clone the repository:
   

   git clone https://github.com/CodewithMukeshkr/HIKARI.git
   cd HIKARI
   
2. Create and activate a virtual environment:

   python3 -m venv .venv
   
   source .venv/bin/activate
   
3. Install dependencies:
   pip install -r requirements.txt

4. Set up environment variables:
   Create a .env file in the root of your project directory.
   Add the following lines to the .env file, replacing your-cohere-api-key and your-weather-api-key with your actual API keys:
   COHERE_API_KEY=your-cohere-api-key
   WEATHER_API_KEY=your-weather-api-key

5. Run the application


   ## Usage
After running the application, you can interact with HIKARI using voice commands. Examples:
- "Hikari, what is the weather in New York?"
- "Hikari, open YouTube."
- "Hikari, Launch Facetime."
- "Hikari, tell me the time."

To exit, say:
- "Goodbye" or "Exit."
