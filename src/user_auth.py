import ast
import datetime
from flask import Flask,request, make_response
import json
import mysql.connector
from flask_jwt_login import JWT
from flask_jwt_extended import  jwt_required,get_jwt_identity
import os
from flask_cors import CORS
import jsonify

TOKEN_NAME = 'user'

# create flask app and add configs
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ['secret_key']
app.config["JWT_COOKIE_NAME"] = TOKEN_NAME
app.config['CORS_HEADERS'] = 'Content-Type'

# make jwt object
jwt = JWT(app)
cors = CORS(app)

host_var = os.environ['host_var']
username_var = os.environ['username_var']
password_var = os.environ['password_var']

def opendb():
    return mysql.connector.connect(host=host_var, user=username_var, password=password_var, database='ezhr')

class User():
    def __init__(self, email, pw,firstName,lastName):
        self.email = email
        self.pw = pw
        self.firstName = firstName
        self.lastName = lastName

    def __repr__(self):
        return "User(email=%s, password=%s ,firstName=%s ,lastName=%s)" % (self.email, self.pw,self.firstName,self.lastName)

def encode_auth_token(email,firstName,lastName):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {

            'iat': datetime.datetime.utcnow(),
            'sub': email,
            'firstname': firstName,
            'lastName': lastName
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    except Exception as e:
        return e
def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def opendb():
    return mysql.connector.connect(host=host_var, user=username_var, password=password_var, database='ezhr')


def authentication_handler(email, pw):
    mydb = opendb()
    cursor = mydb.cursor()
    cursor.execute("select email,password,firstName,lastName from ezhr.users")
    result = cursor.fetchall()
    for x in result:

        if ((x[0].decode("utf-8") == email) & (x[1].decode("utf-8") == pw)):
            return User(x[0].decode("utf-8"), x[1].decode("utf-8"), x[2].decode("utf-8"), x[3].decode("utf-8"))

    # if there is no matching user, returns None
    return None


# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/login', methods=['POST'])
def login():
    print(request.content_type)
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = ast.literal_eval(json.loads(request.data))
    print(data)
    print(type(data))
    email = data['email']
    password = data['password']
    print(email)
    print(password)

    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    token = authentication_handler(email, password)
    print(token)
    print(encode_auth_token(token.email, token.firstName, token.lastName))
    print(decode_auth_token(encode_auth_token(token.email, token.firstName, token.lastName)))
    if token is None:
        return jsonify({"msg": "Bad email or password"}), 401

    # Identity can be any data that is json serializable
    if token is not None:
        # make response to add cookie
        response = make_response("logged in!")
        response.set_cookie(TOKEN_NAME, encode_auth_token(token.email, token.firstName, token.lastName))
        return response
    jwt.decode()


# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@app.route('/protected', methods=['GET'])

@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
