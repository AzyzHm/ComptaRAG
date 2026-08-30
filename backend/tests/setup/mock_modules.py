import os
import sys
from unittest.mock import MagicMock

os.environ.setdefault("gemini_api_key", "fake-gemini-key")
os.environ.setdefault("tavily_api_key", "fake-tavily-key")

for _mod in [
    "chromadb",
    "ollama",
    "google",
    "google.genai",
    "tavily",
]:
    sys.modules.setdefault(_mod, MagicMock())
