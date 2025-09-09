# config.py
import os
import json
from dotenv import load_dotenv

# Loading the environment variables from the .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Check if the API keys have been loaded
if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
    raise ValueError("API keys not found. Please check your .env file.")

# Loading the Google Gemini Credentials from the JSON file (optional)
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
GOOGLE_CREDENTIALS = None

if GOOGLE_CREDENTIALS_PATH and os.path.exists(GOOGLE_CREDENTIALS_PATH):
    try:
        with open(GOOGLE_CREDENTIALS_PATH) as f:
            GOOGLE_CREDENTIALS = json.load(f)
        print("Google Credentials loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load Google credentials: {e}")
        GOOGLE_CREDENTIALS = None
else:
    print("Warning: Google Credentials path not found. Gemini will not be available.")

# Configuration settings
MAX_TURNS = 5  # Maximum number of conversation rounds
MAX_TOKENS = 4000  # Maximum number of tokens per response

# List of available models (dynamically determined)
AVAILABLE_MODELS = ["chatgpt", "claude", "granite"]

# Add Gemini if credentials are available
if GOOGLE_CREDENTIALS:
    AVAILABLE_MODELS.append("gemini")