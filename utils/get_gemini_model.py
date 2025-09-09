from google import genai
from google.genai import types
from dotenv import load_dotenv
import os


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Only run this block for Gemini Developer API
client = genai.Client(api_key='GEMINI_API_KEY')

response = client.models.generate_content(
    model='gemini-2.0-flash-001', contents='Why is the sky blue?'
)
print(response.text)