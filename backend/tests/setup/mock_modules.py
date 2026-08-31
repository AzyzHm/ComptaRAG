import os
import sys
from unittest.mock import MagicMock

os.environ.setdefault("gemini_api_key", "fake-gemini-key")
os.environ.setdefault("tavily_api_key", "fake-tavily-key")
os.environ.setdefault("firebase_project_id", "fake-project")
os.environ.setdefault("firebase_service_account_path", "fake-service-account.json")

import firebase_admin
import firebase_admin.auth  # noqa: F401
import firebase_admin.credentials  # noqa: F401
import firebase_admin.firestore  # noqa: F401
from google.cloud.firestore_v1 import SERVER_TIMESTAMP  # noqa: F401

firebase_admin._apps["[DEFAULT]"] = "fake-app-sentinel"

for _mod in [
    "chromadb",
    "ollama",
    "google.genai",
    "tavily",
]:
    sys.modules.setdefault(_mod, MagicMock())
