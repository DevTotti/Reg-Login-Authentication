from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token)

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mongoreg'
app.config["MONGO_URI"] = "mongodb://localhost:27017/mongoreg"
app.config["JWT_SECRET_KEY"] = 'secret'

mongo = PyMongo(app)
bcyrypt = Bcrypt(app)
jwt = JWTManager(app)


CORS(app)

@app.route("/users/register",methods=['POST'])
def register():
	users = mongo.db.users
	first_name = request.get_json()['first_name']
	last_name = request.get_json()['last_name']
	user_name = request.get_json()['user_name']
	email = request.get_json()['email']
	password = bcyrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
	created = datetime.utcnow()

	user_id = users.insert({
		'first_name': first_name,
		'last_name': last_name,
		'user_name': user_name,
		'email': email,
		'password': password,
		'created': created,
		})

	new_user = users.find_one({'_id': user_id})

	result = {'email': new_user['email']+' registered'}

	return jsonify({'result':result})

@app.route("/users/register",methods=['GET'])
def get_users():
	users = mongo.db.users

	result = []

	for field in users.find():
		result.append({'_id':str(field['_id']), 'user_name':str(field['user_name']),'email':str(field['email']),'password':str(field['password'])})

	return jsonify(result)




@app.route("/users/login",methods=['POST'])
def login():
	users = mongo.db.users
	email = request.get_json()['email']
	password = request.get_json()['password']
	result = ""

	response = users.find_one({'email':email})

	if response:
		if bcyrypt.check_password_hash(response['password'], password):
			access_token = create_access_token(identity = {
				'first_name': response['first_name'],
				'last_name': response['last_name'],
				'email': response['email']
				})

			result = jsonify({"token": access_token})

		else:
			result = jsonify({"error": "Invalid Username or Password"})

	else:
		result = jsonify({"result": "No result found"})

	return result



if __name__ == '__main__':
	app.run(host="localhost", port=5003, debug=True)
