from flask import Flask, request, jsonify

app = Flask(__name__)

# Hardcoded Users
USERS = {
    "Shivendra": "newworld",
    "SRJ": "newworld",
    "Thunderstorms": "!@#321",
    "test": "123",
    "OP_ki_gumti": "+India123"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if USERS.get(username) == password:
        return jsonify({"status": "success", "message": "Login successful", "username": username})
    else:
        return jsonify({"status": "failure", "message": "Invalid username or password"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
