import requests
import jwt
import json, datetime

with open("token.txt", "r") as f:
    id_token = f.read().strip()

payload = jwt.decode(id_token, options={"verify_signature": False})
uid = payload["user_id"]

url = f"https://firestore.googleapis.com/v1/projects/studify-storage/databases/(default)/documents/users/{uid}"

headers = {
    "Authorization": f"Bearer {id_token}",
    "Content-Type": "application/json"
}

def create_user_fields(email, displayname):
    data = {
        "fields": {
            "email": {"stringValue": email},
            "displayName": {"stringValue": displayname},
            "study_time_sec": {"integerValue": 0},
            "createdAt": {"timestampValue": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')}
        }
    }
    r = requests.patch(url, json=data, headers=headers)
    return r.json()

def update_username(displayname):
    data = {
        "fields": {
            "displayName": {"stringValue": displayname},
        }
    }
    r = requests.patch(url, json=data, headers=headers)
    return r.json()

def get_studytime():
    r = requests.get(url, headers=headers)
    time = r.json()['fields']['study_time_sec']['integerValue']
    return time

def update_studytime(sec):
    if type(sec) is int:
        sec = str(sec)
    data = {
        "fields": {
            "study_time_sec": {"integerValue": get_studytime() + sec},
        }
    }
    r = requests.patch(url, json=data, headers=headers)
    return r.json()