import os
import requests
from router import choose_model, increment_usage
from dotenv import load_dotenv
import cohere
import time

load_dotenv()

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Initialize Cohere client
cohere_client = None
if COHERE_API_KEY:
    try:
        cohere_client = cohere.Client(COHERE_API_KEY)
    except Exception as e:
        print(f"[COHERE INIT ERROR] {e}")

def build_prompt(context, user_input):
    return f"{context}\nUser: {user_input}\nAI:"

def estimate_tokens(text):
    return len(text.split())

def call_openrouter_model(model_name, prompt, max_retries=2):
    if not OPENROUTER_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://hikari-assistant.com",
        "X-Title": "HIKARI Assistant",
        "Content-Type": "application/json"
    }

    chat_payload = {
        "model": model_name,
        "messages": [
            {"role": "system",
             "content": "You are HIKARI, a helpful AI assistant. Keep responses concise and friendly."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 0.9
    }
    # Fallback to completions format
    completions_payload = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop": ["\nUser:", "\nHuman:"]
    }

    for attempt in range(max_retries + 1):
        try:
            # First try chat completions
            print(f"[OPENROUTER] Attempting chat completions for {model_name} (attempt {attempt + 1})")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=chat_payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content'].strip()
                    if content:
                        print(f"[OPENROUTER] Success with chat completions")
                        return content

            # If chat completions failed, try regular completions
            print(f"[OPENROUTER] Trying completions format for {model_name}")
            response = requests.post(
                "https://openrouter.ai/api/v1/completions",
                json=completions_payload,
                headers=headers,
                timeout=30
            )
            # if response.status_code == 200:
            #     result = response.json()
            #     if 'choices' in result and len(result['choices']) > 0:
            #         content = result['choices'][0]['text'].strip()
            #         if content:
            #             print(f"[OPENROUTER] Success with completions")
            #             return content

            # Handle specific error cases
            if response.status_code == 429:
                print(f"[OPENROUTER] Rate limited, waiting...")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            elif response.status_code == 402:
                print(f"[OPENROUTER] Insufficient credits for {model_name}")
                return None
            else:
                print(f"[OPENROUTER] HTTP {response.status_code}: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print(f"[OPENROUTER] Timeout for {model_name} (attempt {attempt + 1})")
        except requests.exceptions.RequestException as e:
            print(f"[OPENROUTER] Request error: {e}")
        except Exception as e:
            print(f"[OPENROUTER ERROR] {e}")

        if attempt < max_retries:
            time.sleep(1)  # Brief pause between retries

    print(f"[OPENROUTER] All attempts failed for {model_name}")
    return None

def call_cohere(prompt, max_retries=2):
    """Call Cohere as backup with improved error handling"""

    if not cohere_client:
        print("[COHERE ERROR] Client not initialized")
        return None

    for attempt in range(max_retries + 1):
        try:
            print(f"[COHERE] Attempting generation (attempt {attempt + 1})")
            response = cohere_client.generate(
                model="command",
                prompt=prompt,
                max_tokens=150,
                temperature=0.7,
                stop_sequences=["\nUser:", "\nHuman:", "\n\n"]
            )

            if response.generations and len(response.generations) > 0:
                content = response.generations[0].text.strip()
                if content:
                    print("[COHERE] Success")
                    return content

        except Exception as e:
            print(f"[COHERE ERROR] Attempt {attempt + 1}: {e}")
            if attempt < max_retries:
                time.sleep(1)

    print("[COHERE] All attempts failed")
    return None


def generate_dynamic_response(user_input, context):
    """Main entry point for generating AI responses"""

    if not user_input or not user_input.strip():
        return "I didn't receive any input. Could you please try again?"

    try:
        # Build the prompt
        prompt = build_prompt(context, user_input)
        print(f"[GENERATOR] Processing input: '{user_input[:50]}{'...' if len(user_input) > 50 else ''}'")

        # Choose the best model
        model, category = choose_model(user_input)

        if not model:
            return "I'm currently at capacity. Please try again in a few moments."

        print(f"[GENERATOR] Using {model} from {category} category")

        # Generate response
        response = None

        if model == "cohere":
            response = call_cohere(prompt)
        else:
            response = call_openrouter_model(model, prompt)

        # If primary model failed, try Cohere as fallback
        if not response and model != "cohere" and cohere_client:
            print("[GENERATOR] Primary model failed, trying Cohere fallback")
            response = call_cohere(prompt)
            model = "cohere"  # Update model name for token tracking

        if response:
            # Track token usage
            estimated_tokens = estimate_tokens(prompt + response)
            increment_usage(model, estimated_tokens)

            # Clean up the response
            response = response.strip()

            # Remove any unwanted prefixes
            prefixes_to_remove = ["AI:", "Assistant:", "HIKARI:", "Response:"]
            for prefix in prefixes_to_remove:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()

            print(f"[GENERATOR] Generated {len(response)} character response")
            return response
        else:
            print("[GENERATOR] No response generated from any model")
            return "Response generation failed. Try again."

    except Exception as e:
        print(f"[GENERATOR ERROR] Unexpected error: {e}")
        return "I encountered an unexpected error. Please try again."


def test_model_connection():
    """Test if the model connections are working"""
    test_prompt = "Hello, please respond with a simple greeting."

    print("Testing OpenRouter connection...")
    model, category = choose_model("test")
    if model and model != "cohere":
        response = call_openrouter_model(model, test_prompt)
        if response:
            print(" OpenRouter working with {model}")
        else:
            print(" OpenRouter connection failed")

    print("Testing Cohere connection...")
    if cohere_client:
        response = call_cohere(test_prompt)
        if response:
            print(" Cohere working")
        else:
            print(" Cohere connection failed")
    else:
        print(" Cohere not configured")

if __name__ == "__main__":
    test_model_connection()