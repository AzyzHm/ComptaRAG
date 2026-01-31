import os
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("gemini_api_key")
tavily_api_key = os.getenv("tavily_api_key")