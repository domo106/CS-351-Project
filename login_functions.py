"""
Login Functions
Used by login_server.py to handle the login logic
"""
import os
import hashlib

ERROR_OK = "OK"
ERROR_DB = "Error accessing DB"
ERROR_USER_EXISTS = "Error: User already exists"
# Good enough for now
DATABASE_LOCATION = "database.json"

def register_user(user_name, password):
	print("Registering")
	# Store user_name/password in DB
	# Prepare a salt, and hash the password+salt
	salt = os.urandom(32)
	salted_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
	user_entry = {
		"salt":salt,
		"salted_hash":salted_hash
	}

	# Check if user not in DB
	if user_exists(user_name):
		print("User already exists!")
		return ERROR_USER_EXISTS
	else:
		store_user(user_name, user_entry)
		return ERROR_OK

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
	if not os.path.exists(DATABASE_LOCATION):
		with open(DATABASE_LOCATION, 'w') as database:
			json.dump({}, database)
	try:
		database_data = {}
		with open(DATABASE_LOCATION, 'r') as database:
			database_data = json.load(database)
			database_data[user_name] = user_entry

		with open(DATABASE_LOCATION, 'w') as database:
			json.dump(database_data, database)
		return ERROR_OK
	except:
		return ERROR_DB

def login_user(user_name, password):
	"""
	Checks to see if the username/password pair is valid in DB
	Returns true if valid, false otherwise
	"""
	user_data = {}
	with open(DATABASE_LOCATION, 'r') as database:
			database_data = json.load(database)
			user_entry = database_data[user_name]