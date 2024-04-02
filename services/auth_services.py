from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
import hashlib

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce']
users_collection = db['user']

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if 'username' not in data  or 'password' not in data:
        abort(400, description='Username and password are required')

    username = data['username']
    password = data['password']

    if users_collection.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    users_collection.insert_one({'username': username, 'password': hashed_password})

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    if 'username' not in data  or 'password' not in data:
        abort(400, description='Username and password are required')

    username = data['username']
    password = data['password']

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users_collection.find_one({'username': username})
    if user:
        
        #check if the password matches
        if user['password'] == hashed_password:
            return jsonify({'message': 'User logged in successfully'}), 200
        else:
            return jsonify({'error': 'Incorrect password'}), 401
    else:
        return jsonify({'error': 'User not found'}), 401
    
if __name__ == '__main__':
    app.run(debug=True)