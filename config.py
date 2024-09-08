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

# Loading the Google Gemini Credentials from the JSON file
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
with open(GOOGLE_CREDENTIALS_PATH) as f:
    GOOGLE_CREDENTIALS = json.load(f)

# Configuration settings
MAX_TURNS = 5  # Maximum number of conversation rounds
MAX_TOKENS = 1000  # Maximum number of tokens per response

# List of available models
AVAILABLE_MODELS = ["chatgpt", "claude", "gemini"]