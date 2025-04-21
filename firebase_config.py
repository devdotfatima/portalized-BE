import firebase_admin
from firebase_admin import credentials

# Path to the downloaded service account key file
cred = credentials.Certificate('portalized-4c162-firebase-adminsdk-fbsvc-fcfff0a0d7.json')

# Initialize Firebase app
firebase_admin.initialize_app(cred)