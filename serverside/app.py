from flask import Flask, request, jsonify
import sqlite3, argon2
from datetime import datetime
#argon2 to not require salting


app = Flask(__name__)
p = argon2.PasswordHasher()



@app.route('/')
def index():
    return 200


@app.route('/lease', methods=['POST'])
def lease():
    """Lease connstring+update connstring provided appropriate authentication.

    Returns:
        jsonify: A JSON response with the lease information. Updates the lease dictionary.
        201: If the lease is successfully created.
        400: If the request data is invalid.
    """

    data = request.get_json()
    # Process the lease request here
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    return jsonify({"message": "Lease created", "data": data}), 201

def _checklogin(conn, username, password):
    """
    Queries the users table for a user with the given username and password.

    Parameters:
        conn (sqlite3.Connection): The SQLite connection object.
        username (str): The user's name.
        password (str): The user's password.

    Returns:
        tuple: A tuple containing the user data if found, otherwise None.
    """
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE name=?', (username,))
    user = c.fetchone()
    
    if user and p.verify(user[4], password):
        return user
    return None

def _get_data(conn, username):
    """
    Retrieves user data from the users table based on the username.

    Parameters:
        conn (sqlite3.Connection): The SQLite connection object.
        username (str): The user's name.

    Returns:
        tuple: A tuple containing the user data if found, otherwise None.
    """
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE name=?', (username,))
    return c.fetchone()

def _create_user(conn, name, email, hashed_password, connstr, studytime, version="0.1"):
    """
    Inserts a new user into the users table.

    Parameters:
        conn (sqlite3.Connection): The SQLite connection object.
        name (str): The user's name.
        email (str): The user's email.
        hashed_password (str): The hashed password.
        connstr (str): Connection string info.
        studytime (int): Study time in minutes.
        version (str): Schema version (default: "0.1").
    """
    created_at = datetime.utcnow().isoformat()

    with conn:
        conn.execute('''
            INSERT INTO users (
                created_at, name, email, h_pwd, connstr, studytime, version1
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (created_at, name, email, hashed_password, connstr, studytime, version))

if __name__ == '__main__':
    conn = sqlite3.connect('data.db')
    START = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, created_at TIMESTAMP, name TEXT, email TEXT, h_pwd TEXT, connstr TEXT, studytime INTEGER, version TEXT)')
    
    app.run(debug=True)
    
    