"""GET TOKEN FOR INDIVIDUAL USER"""
import webbrowser
from flask import Flask, request
import threading, os
import signal
import threading 

app = Flask(__name__)

@app.route("/")
def index():
    if threading.current_thread() == threading.main_thread():
        print("[authflask]: WARNING - Running Flask on the main thread may cause issues.")


    return """<!DOCTYPE html>
<html>
<head>
  <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-auth-compat.js"></script>
</head>
<body>
  <h2>Studify - Login with Google Portal</h2>
  <button id="loginBtn">Login</button>
  <script>
    const firebaseConfig = {
      apiKey: "AIzaSyDr_Qsy9WWqKhgvWr2mO4npvZ-dWbmGQ-g",
      authDomain: "studify-storage.firebaseapp.com",
      projectId: "studify-storage",
    };
    firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();

    document.getElementById("loginBtn").onclick = async () => {{
      try {{
        const provider = new firebase.auth.GoogleAuthProvider();
        const result = await auth.signInWithPopup(provider);
        const idToken = await result.user.getIdToken();
        fetch("/recievecreds", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "idtoken=" + encodeURIComponent(idToken)
        })
        .then(() => alert("Token sent!"))
        .catch(async err => {
          await navigator.clipboard.writeText(idToken);
          alert("Failed to send token: (We've copied it to your clipboard) " + err.message + " Copy this and paste into token.txt: " + idToken);
        });
      }} catch (err) {{
        alert("Login failed: " + err.message);
        console.error("Login error:", err);
      }}
    }};
    
  </script>
</body>
</html>"""

@app.route("/recievecreds", methods=["POST"])
def creds():
    id_token = request.form["idtoken"]
    with open("token.txt", "w") as f:
        f.write(id_token)
        f.close()
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            print("[authflask]: NOT RUNNING WITH WERKZEUG")
            threading.Timer(1, lambda: os.kill(os.getpid(), signal.SIGINT)).start() #not running werkzeug, just kill program
        func()
        return #server dead

        




def start_server():
    threading.Thread(target=webbrowser.open("http://localhost:8000/")).start()
    try:
        app.run(debug=False, host="localhost", port=8000)
    except KeyboardInterrupt as e:
        return 
    except Exception as e:
        print("[authflask]: Error occurred while running the server:", e)
        return


if __name__ == "__main__":
    def open_browser():
        webbrowser.open("http://localhost:8000/")

    threading.Thread(target=open_browser).start()
    app.run(debug=False, host="localhost", port=8000)