import firebase_admin
from firebase_admin import credentials
import json
from django.conf import settings

# Get the Firebase credentials from the environment variable
firebase_credentials_str = settings.FIREBASE_CREDENTIALS

if firebase_credentials_str:
    # Parse the Firebase credentials JSON string into a dictionary
    firebase_credentials_dict = json.loads(firebase_credentials_str)
    
    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials_dict)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase app initialized successfully!")
else:
    print("❌ Firebase credentials not found in environment variables!")