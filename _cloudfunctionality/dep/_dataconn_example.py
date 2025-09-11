"""UPDATE USER'S DATA"""
import requests
import jwt
#WORKING
with open("token.txt", "r") as f:
    id_token = f.read().strip()

payload = jwt.decode(id_token, options={"verify_signature": False})
uid = payload["user_id"]

url = f"https://firestore.googleapis.com/v1/projects/studify-storage/databases/(default)/documents/users/{uid}"

data = {
    "fields": {
        "favoriteColor": {"stringValue": "blue"}
    }
}

headers = {
    "Authorization": f"Bearer {id_token}",
    "Content-Type": "application/json"
}

# Write / update
r = requests.patch(url, json=data, headers=headers)
print(r.json())

# Read
r = requests.get(url, headers=headers)
print(r.json())