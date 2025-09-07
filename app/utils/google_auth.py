from google.oauth2 import id_token
from google.auth.transport import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token: str):
    """Verify Google OAuth2 ID token and return user info"""
    try:
        id_info = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        return {
            "status": True,
            "user_info": {
                "google_id": id_info['sub'],
                "email": id_info.get('email'),
                "name": id_info.get('name'),
                "picture": id_info.get('picture')
            }
        }
    except ValueError:
        return {"status": False, "user_info": None}
