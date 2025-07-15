# HIKARI - Personal AI Assistant

HIKARI is a fully voice-controlled AI assistant designed for macOS. It supports intelligent model switching using OpenRouter's free models (68+ in total), fallback AI with Cohere, and performs common assistant tasks like checking the weather, opening apps/websites, and generating dynamic responses using advanced LLMs.


## Features
- 🎙️ Real-time voice interaction using SpeechRecognition + PyAudio  
- 🌤️ Weather updates (via OpenWeatherMap API)  
- 🧠 Smart AI responses using **OpenRouter (60+ models)** and **Cohere** fallback  
- 📶 Automatic model switching with token usage tracking  
- 🔁 Built-in fallback to chat models or Cohere when primary is at capacity  
- 🖥️ Open any installed macOS application with voice  
- 🌐 Launch websites hands-free  
- ⏰ Speak current time and date  
- 🚀 Startup warmup for microphone and DNS resolution  
- 🧠 Categorized model routing (chat, code, math, reasoning, logic, etc.)

## Installation
1. Clone the repository:
   

   git clone https://github.com/CodewithMukeshkr/HIKARI.git
   cd HIKARI
   
2. Create and activate a virtual environment:

   python3 -m venv .venv
   
   source .venv/bin/activate
   
3. Install dependencies:
   pip install -r requirements.txt

4. Platform Compatibility:
   HIKARI supports macOS, Windows, and Linux for text-to-speech (TTS) using native/system tools or pyttsx3.

🖥️ macOS
Uses the built-in say command. No extra setup needed.

🪟 Windows
Uses pyttsx3 for offline speech synthesis.

No additional installation required beyond pip install -r requirements.txt.

🐧 Linux
Uses espeak for TTS. You must install it manually:

sudo apt install espeak

5. Set up environment variables:

   Create a .env file in the root of your project directory.
   Add the following lines to the .env file, replacing your-cohere-api-key and your-weather-api-key with your actual API keys:

   COHERE_API_KEY=your-cohere-api-key 

   WEATHER_API_KEY=your-weather-api-key

   OPENROUTER_API_KEY=your-openrouter-api-key

6. Run the application

You can get:

OpenRouter API Key from: https://openrouter.ai

Cohere API Key from: https://cohere.com

OpenWeatherMap API Key from: https://openweathermap.org


  ## 🧠 AI Model Management
HIKARI uses a token-aware AI model router with category-based selection:

7 Categories: chat, coding, math, reasoning, logic, languages, other

Each category includes ranked models from OpenRouter (e.g. DeepSeek, Mistral, Gemma, Qwen, LLaMA, etc.)

If no models are available due to token limits, it falls back to Cohere automatically.

Usage limits are pre-configured in router.py and dynamically tracked per model.

You can view or customize models in:

model_registry.py — category mappings

router.py — usage limits & routing logic

   ## Usage
After running the application, you can interact with HIKARI using voice commands. Examples:
- "Hikari, what is the weather in New York?"
- "Hikari, open YouTube."
- "Hikari, open Facetime app."
- "Hikari, tell me the time."
- "Hikari, what is the difference between GPT and LLM?"

To exit, say:
- "Goodbye" or "Exit."
