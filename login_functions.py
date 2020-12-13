"""
Login Functions
Used by server.py to handle the login logic
"""
import os
import hashlib
import json
import sys
import base64

OK = "OK"
ERROR = "ERROR"
ERROR_LOGIN = "ERROR_LOGIN"

# Good enough for now
DATABASE_LOCATION = "database.json"

# Generate json file if not present
if not os.path.exists(DATABASE_LOCATION):
		# Generate DB
		with open(DATABASE_LOCATION, 'w') as database:
			json.dump({"DUMMY_USER":{"salt":"dummysalt","salted_hash":"dummyhash"}}, database)

def register_user(user_name, password):
	print("Registering")
	# Store user_name/password in DB
	# Prepare a salt, and hash the password+salt
	salt = os.urandom(64)
	salted_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
	user_entry = {
		"salt":base64.b64encode(salt).decode('utf-8'),
		"salted_hash":salted_hash.hex()
	}
	#print(user_entry)
	#print(type(user_entry["salt"]))
	#print(type(user_entry["salted_hash"]))

	# Check if user not in DB
	if user_exists(user_name):
		print("User already exists!")
		return ERROR
	else:
		print("Store success")
		store_user(user_name, user_entry)
		return OK

def user_exists(user_name):
	"""Returns true if the user is in the DB, False otherwise."""
	with open(DATABASE_LOCATION, 'r') as database:
		database_data = json.load(database)
		return user_name in database_data
	
def store_user(user_name, user_entry):
	"""
	Takes user_name, and a dict with salt and salted_hash as input
	Stores to DB, returns OK if no error.
	"""

	database_data = {}
	with open(DATABASE_LOCATION, 'r') as database:
		input_string = database.read()
		database_data = json.loads(input_string)
		if user_name in database_data:
			return ERROR_LOGIN
		database_data[user_name] = user_entry

	with open(DATABASE_LOCATION, 'w') as database:
		output = json.dumps(database_data, indent=4)
		database.write(output)
	return OK
	

def login_user(user_name, password):
	"""
	Checks to see if the username/password pair is valid in DB
	Returns true if valid, false otherwise
	"""
	user_data = {}
	with open(DATABASE_LOCATION, 'r') as database:
			database_data = json.load(database)
			if not user_name in database_data:
				return ERROR
			user_entry = database_data[user_name]
			salt = base64.b64decode(user_entry["salt"].encode('utf-8'))
			stored_hash = user_entry["salted_hash"]
			new_hash = (hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)).hex()
			if stored_hash == new_hash:
				return OK
			else:
				return ERROR_LOGIN