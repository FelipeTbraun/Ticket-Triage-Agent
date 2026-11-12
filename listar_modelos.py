import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for modelo in client.models.list():
    if "generateContent" in (modelo.supported_actions or []):
        print(modelo.name)