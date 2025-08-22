import webview
import json
import requests

# ==== Firebase config ====
FIREBASE_API_KEY = "AIzaSyDr_Qsy9WWqKhgvWr2mO4npvZ-dWbmGQ-g"
FIREBASE_PROJECT_ID = "studify-storage"
WEB_CLIENT_ID = "1069113714749-mjvr0cldqa8vvqvqbg7u4v0h1epin14m.apps.googleusercontent.com"

# ==== HTML page with Firebase Web SDK ====
html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-auth-compat.js"></script>
</head>
<body>
  <h2>Login with Google</h2>
  <button id="loginBtn">Login</button>
  <script>
    const firebaseConfig = {{
      apiKey: "{FIREBASE_API_KEY}",
      authDomain: "{FIREBASE_PROJECT_ID}.firebaseapp.com",
      projectId: "{FIREBASE_PROJECT_ID}",
    }};
    firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();

    document.getElementById("loginBtn").onclick = async () => {{
      try {{
        const provider = new firebase.auth.GoogleAuthProvider();
        const result = await auth.signInWithPopup(provider);
        const idToken = await result.user.getIdToken();
        window.pywebview.api.receiveToken(idToken);
      }} catch (err) {{
        alert("Login failed: " + err.message);
        console.error("Login error:", err);
      }}
    }};
  </script>
</body>
</html>
"""

# ==== Python API for WebView ====
class Api:
    def __init__(self):
        self.id_token = None

    def receiveToken(self, token):
        self.id_token = token
        print("✅ Firebase ID token:", token)

        # ==== Firestore REST helpers ====
        def firestore_get_doc(id_token, collection, doc_id):
            url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/{collection}/{doc_id}"
            headers = {"Authorization": f"Bearer {id_token}"}
            r = requests.get(url, headers=headers)
            return r.json()

        def firestore_set_doc(id_token, collection, doc_id, data):
            url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/{collection}/{doc_id}"
            headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
            payload = {"fields": {k: {"stringValue": str(v)} for k, v in data.items()}}
            r = requests.patch(url, headers=headers, data=json.dumps(payload))
            return r.json()

        # ==== Example usage ====
        firestore_set_doc(token, "users", "user123", {"name": "Levi Brown", "score": 42})
        doc = firestore_get_doc(token, "users", "user123")
        print("Firestore document:", doc)
        return "ok"

api = Api()
webview.create_window("Firebase Login", html=html_content, js_api=api)
webview.start()
