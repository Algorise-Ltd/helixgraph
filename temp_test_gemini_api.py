import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
else:
    try:
        client = genai.Client()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain how AI works in a few words",
        )

        print(response.text)
        print("API Key test successful!")
    except Exception as e:
        print(f"API Key test failed: {e}")
