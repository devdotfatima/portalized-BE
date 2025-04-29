# core/firebase.py
import firebase_admin
from firebase_admin import credentials
from django.conf import settings
import json

def initialize_firebase():
    if not firebase_admin._apps:
        firebase_credentials_str = settings.FIREBASE_CREDENTIALS
        if firebase_credentials_str:
            firebase_credentials_dict = json.loads(firebase_credentials_str)
            cred = credentials.Certificate(firebase_credentials_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized")
        else:
            print("❌ Firebase credentials not found in environment variables!")