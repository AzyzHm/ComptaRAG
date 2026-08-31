import firebase_admin
from firebase_admin import credentials, firestore

from config.api_keys import FIREBASE_PROJECT_ID, FIREBASE_SERVICE_ACCOUNT_PATH

_firestore_client = None


def init_firebase() -> None:
    """Initialize the Firebase Admin app once, using the service account
    referenced by FIREBASE_SERVICE_ACCOUNT_PATH. Safe to call multiple times,
    for example once from main.py at startup and once from tests.
    """
    if firebase_admin._apps:
        return

    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID})


def get_firestore_client():
    """Returns a shared Firestore client, initializing Firebase on first use."""
    global _firestore_client
    if _firestore_client is None:
        init_firebase()
        _firestore_client = firestore.client()
    return _firestore_client
