import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No API Key found")
else:
    genai.configure(api_key=api_key)
    try:
        print("--- List of models ---")
        for m in genai.list_models():
            print(f"{m.name} - {m.supported_generation_methods}")
    except Exception as e:
        print(f"Error list_models: {e}")
