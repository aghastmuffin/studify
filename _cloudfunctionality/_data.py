import requests
import jwt
import json, datetime

with open("token.txt", "r") as f:
    id_token = f.read().strip()

payload = jwt.decode(id_token, options={"verify_signature": False})
uid = payload["user_id"]

url = f"https://firestore.googleapis.com/v1/projects/studify-storage/databases/(default)/documents/users/{uid}"
vault_url = f"https://firestore.googleapis.com/v1/projects/studify-storage/databases/(default)/documents/users/{uid}/private/vault"
headers = {
    "Authorization": f"Bearer {id_token}",
    "Content-Type": "application/json"
}

def create_user_fields(email, displayname, user_id):
    # 1. Create main user doc
    user_data = {
        "fields": {
            "email": {"stringValue": email},
            "displayName": {"stringValue": displayname},
            "study_time_sec": {"integerValue": 0},
            "createdAt": {
                "timestampValue": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(timespec="microseconds").replace("+00:00", "Z")
            },
        }
    }
    user_url = f"{url}/users/{user_id}"
    r1 = requests.patch(user_url, json=user_data, headers=headers)

    # 2. Create private/vault subdoc
    vault_data = {
        "fields": {
            "email": {"stringValue": email},
            "createdAt": {
                "timestampValue": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(timespec="microseconds").replace("+00:00", "Z")
            },
        }
    }
    vault_url = f"{url}/users/{user_id}/private/vault"
    r2 = requests.patch(vault_url, json=vault_data, headers=headers)

    return r1.json(), r2.json()

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

def reauth():
    import studify._cloud._authflask as _authflask
    _authflask.start_server()