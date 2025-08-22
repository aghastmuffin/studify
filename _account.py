import json
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
#TODO: Prod migrate to: https://cloud.google.com/endpoints/docs/openapi/authenticating-users-firebase
API_KEY = "AIzaSyDr_Qsy9WWqKhgvWr2mO4npvZ-dWbmGQ-g" 

# This file you download from Google Cloud Console (OAuth 2.0 client ID)
CLIENT_SECRETS_FILE = "client_secret.json"


def get_google_id_token():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    )
    creds = flow.run_local_server(port=0)
    return creds.id_token


def firebase_sign_in_with_google(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={API_KEY}"
    payload = {
        "postBody": f"id_token={id_token}&providerId=google.com",
        "requestUri": "http://localhost",  # dummy but required
        "returnIdpCredential": True,
        "returnSecureToken": True
    }
    r = requests.post(url, json=payload)
    return r.json()


if __name__ == "__main__":
    google_token = get_google_id_token()
    firebase_tokens = firebase_sign_in_with_google(google_token)

    print("Firebase ID token:", firebase_tokens["idToken"])
    print("Refresh token:", firebase_tokens["refreshToken"])
    print("Firebase user info:", firebase_tokens["email"])
