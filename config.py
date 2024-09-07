#config.py
import os
from dotenv import load_dotenv

# Laden der Umgebungsvariablen aus der .env-Datei
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Überprüfen, ob die API-Schlüssel geladen wurden
if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
    raise ValueError("API keys not found. Please check your .env file.")

# Konfigurationseinstellungen
MAX_TURNS = 5  # Maximale Anzahl der Gesprächsrunden
MAX_TOKENS = 1000  # Maximale Tokenzahl pro Antwort