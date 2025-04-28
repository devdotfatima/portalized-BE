import firebase_admin
from firebase_admin import credentials

# # Path to the downloaded service account key file
# cred = credentials.Certificate('portalized-4c162-firebase-adminsdk-fbsvc-fcfff0a0d7.json')

# # Initialize Firebase app
# firebase_admin.initialize_app(cred)



# import firebase_admin
# from firebase_admin import credentials
import json
from django.conf import settings  # Import settings to access FIREBASE_CREDENTIALS

# Get the Firebase credentials from the environment variable
firebase_credentials_str = settings.FIREBASE_CREDENTIALS

if firebase_credentials_str:
    # Parse the Firebase credentials JSON string into a dictionary
    firebase_credentials_dict = json.loads(firebase_credentials_str)
    
    # Initialize Firebase with the credentials
    cred = credentials.Certificate(firebase_credentials_dict)
    firebase_admin.initialize_app(cred)
    print("Firebase app initialized successfully!")
else:
    print("❌ Firebase credentials not found in environment variables!")