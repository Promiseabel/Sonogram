#!/usr/bin/env python3
import sys
import os
import base64
from flask import Flask, jsonify, abort, request, make_response, session, render_template
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import pymysql.cursors
import json
import settings as settings # Our server and db settings, stored in settings.py
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import ssl
from flask_wtf.csrf import CSRFProtect

# Define SSL certificate and key file paths 
CERT_FILE = "ssl/cert.pem" 
KEY_FILE = "ssl/key.pem" 

app = Flask(__name__)
# Set Server-side session config: Save sessions in the local app directory.
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'sonogramCookie'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_DURATION'] = 3600 
Session(app)

IMAGE_UPLOAD_FOLDER = 'src/app/static/imagefiles'
AUDIO_UPLOAD_FOLDER = 'src/app/static/audiofiles'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'mpeg'}

app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
app.config['AUDIO_UPLOAD_FOLDER'] = AUDIO_UPLOAD_FOLDER

app.jinja_env.autoescape = True

limiter = Limiter(
    app=app,
    key_func=get_remote_address, 
    default_limits=["500 per day", "100 per hour"]
)

csp = {
    'default-src': [
        '\'self\'',
    ],
	'script-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
		'\'unsafe-eval\'',  # For Vue.js and Axios
    ],
    'style-src': [
        '\'self\'',
        'https://fonts.googleapis.com',  # For Google Fonts
    ],
    'font-src': [
        'https://fonts.gstatic.com',  # For Google Fonts
    ],
}
talisman = Talisman(app, content_security_policy=csp)

csrf = CSRFProtect(app)

failed_attempts = {}

####################################################################################
#
# Error handlers
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

@app.route('/')
def index():
    return render_template('index.html')

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def getUserID(username):
	dbConnection = pymysql.connect(
		host=settings.MYSQL_HOST,
		user=settings.MYSQL_USER,
		password=settings.MYSQL_PASSWD,
		database=settings.MYSQL_DB,
		charset='utf8mb4',
		cursorclass=pymysql.cursors.DictCursor
	)
	sql = 'GetUserID' 
	cursor = dbConnection.cursor()
	sqlArgs = (username,)
	cursor.callproc(sql,sqlArgs) # stored procedure, no arguments
	row = cursor.fetchone() # get the single result
	if row is None:
		return None
	else:
		return row['user_id']

class SignUp(Resource):
	def post(self):
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "<your_name>","password": "<your_password>", "email_address": "<your_email>", "bio":"<your_bio>", "profile_picture": "<profile_picture>"}' http://localhost:8080/signup
		# Get user data
		user_data = request.form

		# Validate user data
		if 'username' not in user_data or len(user_data['username']) > 25:
			abort(400, 'Username cannot be more than 25 characters.')

		# Validate password
		if 'password' not in user_data or not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', user_data['password']):
			abort(400, 'Password does not meet complexity requirements.')

		# Validate email
		if 'email_address' not in user_data or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', user_data['email_address']) or len(user_data['email_address']) > 255:
			abort(400, 'Invalid email address.')

		# Validate bio
		if 'bio' not in user_data or len(user_data['bio']) > 255:
			abort(400, 'Bio cannot be more than 255 characters.')

		filename = "default.jpeg"

		if 'profile_picture' in request.files:
			file = request.files['profile_picture']
			if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS) and file.content_length < 5 * 1024 * 1024:
				filename = secure_filename(user_data['username'] + '_' + datetime.now().strftime('%Y%m%d%H%M%S') + os.path.splitext(file.filename)[1])
				print('Current directory:', os.getcwd())
				file.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
			else:
				response = {'Response': 'File could not be saved'}
				responseCode = 400
				os.remove(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
				abort(responseCode,response)
		
		
		user = {'username' : user_data['username'].lower(),
			'password' : user_data['password'],
			'email_address' : user_data['email_address'],
			'bio' : user_data['bio'],
			'profile_picture' : filename}
		
		# Creating a new user in DB
		try:
			dbConnection = pymysql.connect(
				host=settings.MYSQL_HOST,
				user=settings.MYSQL_USER,
				password=settings.MYSQL_PASSWD,
				database=settings.MYSQL_DB,
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor
			)
			sql = 'CreateUser'
			cursor = dbConnection.cursor()
			sqlArgs = (user['username'],user['password'], user['email_address'], user['bio'], user['profile_picture'])
			cursor.callproc(sql,sqlArgs) # stored procedure, with arguments
			row = cursor.fetchone()
			dbConnection.commit() # database was modified, commit the changes

			session['user_id'] = getUserID(user['username'])
			response = {'status': 'success'}
			responseCode = 201
		
		except:
			os.remove(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
			abort(500, "Error while running the stored procedure") # Error
		
		finally:
			cursor.close()
			dbConnection.close()
		
		return make_response(jsonify(response), responseCode)


class SignIn(Resource):
	#
	# Set Session and return Cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "<your_name>", "password": "<your_pass>"}' -c cookie-jar -k http://localhost:8080/signin
	#
	def post(self):
		
		if not request.json:
			abort(400) # bad request

		# Parse the json
		parser = reqparse.RequestParser()
		try:
 			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request 
		
		if 'user_id' in session:
			response = {'status': 'Already Signed In'}
			responseCode = 200
		else:
			try:
				print('success')
				# Check if account is locked
				if failed_attempts.get(request_params['username'], 0) >= 5:
					abort(403, "Account locked. Try again later.")		
				
				dbConnection = pymysql.connect(
					host=settings.MYSQL_HOST,
					user=settings.MYSQL_USER,
					password=settings.MYSQL_PASSWD,
					database=settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass=pymysql.cursors.DictCursor
				)

				cursor = dbConnection.cursor()

				sql = 'AuthenticateUser' 
				
				sqlArgs = (request_params['username'], request_params['password'],)
				# Prepare to call stored procedure
				cursor.callproc(sql, sqlArgs)
				
				result = cursor.fetchone()
				isAuthenticated = result['Authenticated']

				if isAuthenticated:

					session['user_id'] = getUserID(request_params['username'])
					response = {'status': 'Signed In'}
					responseCode = 201

					failed_attempts[request_params['username']] = 0

					return make_response(jsonify(response), responseCode)

				else:
					# Authentication failed, handle accordingly
					response = {'status': 'Access denied'}
					responseCode = 403
				# User is authenticated

			except Exception as e:
				print('fail')
				print(e)
				response = {'status': 'Something Went Wrong'}
				print(response)
				responseCode = 403
			finally:
				dbConnection.close()

		return make_response(jsonify(response), responseCode)

	# GET: Check for a login
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar http://localhost:8080/signin
	def get(self):
		if 'user_id' in session:
			response = {'status': 'success','user_id': session['user_id']}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)
#################################

class SignOut(Resource):
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar -k http://localhost:8080/signout

	def delete(self):
		if 'user_id' in session:
			session.pop('user_id')
			response = {'status':'success'}
			responseCode = 200
			return make_response(jsonify(response), responseCode)
		else:
			response = {'status': 'User not logged in'}
			responseCode = 403
			return make_response(jsonify(response), responseCode)

# User Profile Routes

class User(Resource):
	#
	# Updates user information
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X PUT -d '{"username": "<your_name>","password": "<your_password>", "email_address": "<your_email>", "bio":"<your_bio>", "profile_picture": "<profile_picture>"}' -b cookie-jar -k http://localhost:8080/users/{id}
	#
	def put(self, user_id):
		print('success')
		# Update user information
		if 'user_id' in session:
			# if username is in session and the username in session is equal to current username then allow update
			if session['user_id'] == user_id:
				response = {'status': 'success'}
				responseCode = 200
			else:
				abort(401,"Unauthorized Access!! You are not allowed to update someone else's data.")
		else:
			response = {'Response': 'User not Logged in'}
			responseCode = 401
			abort(responseCode,response)
		
		user_data = request.form
		# Validate user data
		if 'username' not in user_data or len(user_data['username']) > 25:
			abort(400, 'Username cannot be more than 25 characters.')
		
		# Validate email
		if 'email_address' not in user_data or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', user_data['email_address']) or len(user_data['email_address']) > 255:
			abort(400, 'Invalid email address.')

		# Validate bio
		if 'bio' not in user_data or len(user_data['bio']) > 255:
			abort(400, 'Bio cannot be more than 255 characters.')

		filename = "default.jpeg"


		if 'profile_picture' in request.files:
			file = request.files['profile_picture']
			if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS) and file.content_length < 5 * 1024 * 1024:
				filename = secure_filename(user_data['username'] + '_' + datetime.now().strftime('%Y%m%d%H%M%S') + os.path.splitext(file.filename)[1])
				print('Current directory:', os.getcwd())
				file.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
			else:
				response = {'Response': 'File could not be saved'}
				responseCode = 400
				os.remove(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
				abort(responseCode,response)
		

		#Run update user procedure
		user = {
			# user can't change user id
		  	'username' : user_data['username'],
			'email_address' : user_data['email_address'],
			'bio' : user_data['bio'],
			'profile_picture' : filename
		}
		
		try:
			dbConnection = pymysql.connect(
					host=settings.MYSQL_HOST,
					user=settings.MYSQL_USER,
					password=settings.MYSQL_PASSWD,
					database=settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass=pymysql.cursors.DictCursor
				)
			sql = 'UpdateUser'
			cursor = dbConnection.cursor()
			sqlArgs = (user_id,user['username'], user['email_address'], user['bio'], user['profile_picture']) 
			cursor.callproc(sql,sqlArgs) 
			row = cursor.fetchone()
			dbConnection.commit()
			response = {'status': 'success','message': 'User details updated successfully', 'user_details': user}
			responseCode = 204
		
		except:
			abort(500, "User information could not be updated successfully")
		
		finally:
			cursor.close()
			dbConnection.close()
		
		return make_response(jsonify(response), responseCode)

	#
	# Lists all audio files uploaded by a specific user and their information
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k http://localhost:8080/users/{id}
	#
	def get(self, user_id):
		# Check if user is logged in
		if 'user_id' in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'Response': 'User not Logged in'}
			responseCode = 401
			abort(responseCode,response)

		try:
			dbConnection = pymysql.connect(
					host=settings.MYSQL_HOST,
					user=settings.MYSQL_USER,
					password=settings.MYSQL_PASSWD,
					database=settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass=pymysql.cursors.DictCursor
				)
			sql = 'GetUser'
			cursor = dbConnection.cursor()
			sqlArgs = (user_id,)
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchone()

			if row is None:
				response = {'status': 'failure'}
				responseCode = 404
			else:
				sql = 'ListUserAudios'
				cursor = dbConnection.cursor()
				sqlArgs = (user_id,)
				cursor.callproc(sql, sqlArgs)
				rows = cursor.fetchall()
				if not rows:
					response = {'username': row['username'], 'bio': row['bio'], 'profile_picture' : row['profile_picture']}
				else:
					response = {'username': row['username'], 'bio': row['bio'], 'profile_picture' : row['profile_picture'], 'audios': rows}
				responseCode = 200

		except:
			abort(500, "User information could not be fetched successfully") 
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify(response), responseCode) # successful

	#
	# User uploads a new audio file
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"title": "<your-title>", "audio_file": "/some/random path", "parent_audio_id":1, "like_count":0}' -b cookie-jar -k http://localhost:8080/users/{id}
	
	def post(self, user_id):
		# Get the request data
		user_data = request.form

		if 'user_id' in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'Response': 'User not Logged in'}
			responseCode = 403
			abort(responseCode,response)

		# Validate the data
			
		# Validate bio
		if 'title' not in user_data or len(user_data['title']) > 255:
			abort(400, 'Title cannot be more than 255 characters.')

		filename = ""

		print("success")

		if 'audio_file' in request.files:
			file = request.files['audio_file']
			if file and allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS)  and file.content_length < 5 * 1024 * 1024:
				filename = secure_filename(user_data['title'] + '_' + datetime.now().strftime('%Y%m%d%H%M%S') + os.path.splitext(file.filename)[1])
				print('Current directory:', os.getcwd())
				file.save(os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], filename))
				print("success")

			else:
				response = {'Response': 'File could not be saved'}
				responseCode = 400
				os.remove(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
				abort(responseCode,response)

		# Create a new sound
		user_sound_upload = {
			'audio_file': filename,
			'title': user_data['title']
		}

		if filename == "":
				response = {'Response': 'File could not be saved'}
				responseCode = 400
				abort(responseCode,response)
		
		print(user_sound_upload)

		if 'parent_audio_id' in user_data:
			user_sound_upload['parent_audio_id'] = user_data['parent_audio_id']
		else:
			user_sound_upload['parent_audio_id'] = None

		if 'like_count' in user_data:
			user_sound_upload['like_count'] = user_data['like_count']
		else:
			user_sound_upload['like_count'] = 0

		try:
			dbConnection = pymysql.connect(
				host=settings.MYSQL_HOST,
				user=settings.MYSQL_USER,
				password=settings.MYSQL_PASSWD,
				database=settings.MYSQL_DB,
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor
			)
			sql = 'UploadAudio'
			cursor = dbConnection.cursor()
			sqlArgs = (user_id, user_sound_upload['title'], user_sound_upload['audio_file'], user_sound_upload['parent_audio_id'], user_sound_upload['like_count'])
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchone()
			dbConnection.commit()
		except:
			abort(500, "Audio file could not be uploaded successfully")
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify({'status': 'success', "Response": "Audio file uploaded successfully"}), 200)

class UserPassword(Resource):
	#
	# Updates user information
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X PUT -d '{"username": "<your_name>","password": "<your_password>", "email_address": "<your_email>", "bio":"<your_bio>", "profile_picture": "<profile_picture>"}' -b cookie-jar -k http://localhost:8080/users/{id}
	#
	def put(self, user_id):
		# Update user information
		if 'user_id' in session:
			# if username is in session and the username in session is equal to current username then allow update
			if session['user_id'] == user_id:
				print(session['user_id'])
				user_data = request.get_json()
				
			else:
				abort(401,"Unauthorized Access!! You are not allowed to update someone else's data.")
		else:
			response = {'Response': 'User not Logged in'}
			responseCode = 401
			abort(responseCode,response)
		

		if 'oldPassword' not in user_data or 'newPassword' not in user_data or not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', user_data['newPassword']):
			abort(400 ,'Password does not meet complexity requirements.')
		
		#Run update user procedure
		user = {
			# user can't change user id
		  	'oldPassword' : user_data['oldPassword'],
			'newPassword' : user_data['newPassword']
		}
		
		
		try:
			dbConnection = pymysql.connect(
					host=settings.MYSQL_HOST,
					user=settings.MYSQL_USER,
					password=settings.MYSQL_PASSWD,
					database=settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass=pymysql.cursors.DictCursor
				)
			sql = 'UpdatePassword'
			cursor = dbConnection.cursor()
			sqlArgs = (user_id, user['oldPassword'], user['newPassword']) 
			cursor.callproc(sql,sqlArgs) 
			row = cursor.fetchone()
			dbConnection.commit()
			print('success')
			response = {'status': 'success','message': 'User password updated successfully'}
			responseCode = 200
		
		except:
			abort(500, "User password could not be updated successfully")
		
		finally:
			cursor.close()
			dbConnection.close()
		
		return make_response(jsonify(response), responseCode)
	
class UserAudio(Resource):
	#	
	# Allows user to delete an audio file
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar -k http://localhost:8080/users/f4qz3/audios/4
	# curl -i -H "Content-Type: application/json" -X DELETE -b cookie-jar -k http://localhost:8004/users/<user_id>/audios/<audio_id>
	def delete(self, user_id, audio_id):
		# Check if the user is logged in
		if 'user_id' in session:
			if session['user_id'] == user_id:
				response = {'status': 'success'}
				responseCode = 200
			else:
				abort(401, "Unauthorized Access!! You are not allowed to delete someone else's data.")
		else:
			response = {'Response': 'User not Logged in'}
			responseCode = 401
			abort(responseCode, response)

		# Run deleteAudio stored procedure
		try:
			dbConnection = pymysql.connect(
					host=settings.MYSQL_HOST,
					user=settings.MYSQL_USER,
					password=settings.MYSQL_PASSWD,
					database=settings.MYSQL_DB,
					charset='utf8mb4',
					cursorclass=pymysql.cursors.DictCursor
				)
			sql = 'DeleteAudio'
			cursor = dbConnection.cursor()
			sqlArgs = (audio_id,)  # Note the comma to create a tuple
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchone()
			dbConnection.commit()
			response = {'status': 'success', 'message': 'Audio deleted succesffuly', 'audio_id': audio_id}
			responseCode = 204
		except:
			abort(500, "Audio file could not be deleted")
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify(response), responseCode)


	#	
	# Allows user to update an audio file
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X PUT -d '{"title": "new title", "audio_file": "/new/path"}' -b cookie-jar -k http://localhost:8080/users/f4qz3/audios/5
	def put(self, user_id, audio_id):
		# Check if the user is logged in
		response = {'status': 'success'}  # Default response
		responseCode = 200  # Default response code

		if 'user_id' in session:
			logged_in_user_id = session['user_id']
			# Check if the userId in session is equal to the current userId
			if logged_in_user_id == user_id:
				# Get title and audio_file from request JSON
				request_data = request.json
				new_audio = {
					'title': request_data['title'],
					'audio_file': request_data['audio_file']
				}
				# Run updateAudio stored procedure
				try:
					dbConnection = pymysql.connect(
						host=settings.MYSQL_HOST,
						user=settings.MYSQL_USER,
						password=settings.MYSQL_PASSWD,
						database=settings.MYSQL_DB,
						charset='utf8mb4',
						cursorclass=pymysql.cursors.DictCursor
					)
					sql = 'UpdateAudio'
					cursor = dbConnection.cursor()
					sqlArgs = (audio_id, new_audio['title'], new_audio['audio_file'])
					cursor.callproc(sql, sqlArgs)
					dbConnection.commit()
					response = {'status': 'success', 'message': 'Audio file updated successfully!!'}
					responseCode = 200
				except:
					abort(500, "Audio information could not be updated successfully")
				finally:
					cursor.close()
					dbConnection.close()
			else:
				response = {'Response': 'User not Logged in'}
				responseCode = 401
				abort(responseCode, response)
		else:
			response = {'Response': 'User not Logged in'}
			responseCode = 401
			abort(responseCode, response)

		return make_response(jsonify(response), responseCode)

class Audio(Resource):
	#
	# List all the audios on the platform
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET -b cookie-jar -k http://localhost:8080/audios
	#

	def get(self):
		# Check if the user is logged in
		if 'user_id' in session:
			user_id = session['user_id']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'Response': 'User not Logged in'}
			responseCode = 401
			abort(responseCode, response)
		try:
			dbConnection = pymysql.connect(
				host=settings.MYSQL_HOST,
				user=settings.MYSQL_USER,
				password=settings.MYSQL_PASSWD,
				database=settings.MYSQL_DB,
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor)
			sql = 'ListAllAudios'
			cursor = dbConnection.cursor()
			cursor.callproc(sql)
			rows = cursor.fetchall()
		except:
			abort(500, "Audio files could not be fetched successfully")
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({'status': 'success','audios': rows}), responseCode)



############################################################################
            
class AudioFile(Resource):
	#
	# Updates the like count in table
	# curl -i -H "Content-Type: application/json" -X PUT -d '{"increment": true}' -b cookie-jar -k http://localhost:8080/audios/7

    def put(self, audio_id):
        # Check if the user is logged in
        if 'user_id' in session:
            logged_in_user_id = session['user_id']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'Response': 'User not Logged in'}
            responseCode = 401
            abort(responseCode, response)

        # Check if the increment parameter is provided in the request JSON
        request_data = request.json
        increment = request_data.get('increment', True)  # Default to True if not provided

        # Run the EditLikeCount stored procedure
        try:
            dbConnection = pymysql.connect(
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWD,
                database=settings.MYSQL_DB,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            sql = 'EditLikeCount'
            cursor = dbConnection.cursor()
            sqlArgs = (audio_id, increment)
            cursor.callproc(sql, sqlArgs)
            dbConnection.commit()
            response = {'status': 'success', 'message': 'Like count updated successfully'}
            responseCode = 200
        except:
            abort(500, "Failed to update like count")
        finally:
            cursor.close()
            dbConnection.close()

        return make_response(jsonify(response), responseCode)

	# Get  replies to a particular audio
	# curl -i -H "Content-Type: application/json" -X GET http://localhost:8080/audios/<audio_id>

    def get(self, audio_id):
        if 'user_id' in session:
            logged_in_user_id = session['user_id']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'Response': 'User not Logged in'}
            responseCode = 401
            abort(responseCode, response)
        try:
            dbConnection = pymysql.connect(
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWD,
                database=settings.MYSQL_DB,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            sql = 'GetAudioFile'
            cursor = dbConnection.cursor()
            sqlArgs = (audio_id,)
            cursor.callproc(sql, sqlArgs)
            row = cursor.fetchone()

            if row is None:
                response = {'status': 'failure'}
                responseCode = 404
            else:
                sql = 'ListAudioReplies'
                cursor = dbConnection.cursor()
                sqlArgs = (audio_id,)
                cursor.callproc(sql, sqlArgs)
                rows = cursor.fetchall()
                if not rows:
                    response = {'status': 'success', 'title': row['title'], 'audio_file': row['audio_file'],'like_count' : row['like_count']}
                else:
                    response = {'status': 'success', 'title': row['title'], 'audio_file': row['audio_file'],'like_count' : row['like_count'], 'replies': rows}
                responseCode = 200

        except:
            abort(500, "Failed to fetch audio information from the database")
        finally:
            cursor.close()
            dbConnection.close()

        return make_response(jsonify(response), responseCode)

####################################################################################
#
# API end points for user signin
#
api = Api(app)
api.add_resource(SignIn, '/signin')
api.add_resource(SignUp, '/signup')
api.add_resource(SignOut, '/signout')
api.add_resource(User, '/users/<int:user_id>')
api.add_resource(UserPassword, '/users/<int:user_id>/update-password')
api.add_resource(UserAudio, '/users/<int:user_id>/audios/<int:audio_id>')
api.add_resource(Audio, '/audios')
api.add_resource(AudioFile, '/audios/<int:audio_id>')



#############################################################################
# xxxxx= last 5 digits of your studentid. If xxxxx > 65535, subtract 30000
if __name__ == "__main__":
	context = (CERT_FILE, KEY_FILE)
	#app.run(host=settings.APP_HOST, ssl_context=context, port=settings.APP_PORT, debug=settings.APP_DEBUG)
	app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)