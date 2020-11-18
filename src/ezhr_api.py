from flask import request
from flask_restful import Resource, Api
import json

import mysql.connector

from flask import Flask
import hashlib
import os

app = Flask(__name__)
api = Api(app)

host_var = os.environ['host_var']
username_var = os.environ['username_var']
password_var = os.environ['password_var']


class Jobs(Resource):
    def get(self):
        mydb = opendb()
        cursor = mydb.cursor()
        cursor.execute("select job_title,job_company,job_location,job_summary,job_url from jobs")
        result = cursor.fetchall()
        fields = [job[0] for job in cursor.description]
        jobDict = {'jobs': [str(dict(list(zip(tuple(fields), i)))) for i in result]}
        resp = json.dumps(jobDict['jobs'])

        return resp


def opendb():
    return mysql.connector.connect(host=host_var, user=username_var, password=password_var, database='ezhr')


@app.route('/register')
def Register():
    mydb = opendb()
    cursor = mydb.cursor()
    cursor2 = mydb.cursor()
    sql = "REPLACE INTO ezhr.users (email,password,firstName,lastName,userID) VALUES (%s,%s,%s,%s,%s)"
    email = request.args.get('email')
    password = request.args.get('password')
    firstName = request.args.get('firstName')
    lastName = request.args.get('lastName')
    cursor2.execute("select email from users where email LIKE '%s'" % email)

    thisHash = hashlib.sha256(str(email + firstName).encode())
    insert_tuple = (email, password, firstName, lastName, thisHash.hexdigest())
    result = cursor2.fetchall()
    print(result)
    if not result:
        cursor.execute(sql, insert_tuple)
        mydb.commit()
        return b'successful', 200
    return b'email in use', 400


class Job_title(Resource):
    def get(self, job_title):
        mydb = opendb()
        cursor = mydb.cursor()
        cursor.execute(
            "select job_title,job_company,job_location,job_summary,job_url from jobs where job_title like '%s'" % (
                job_title))
        row_headers = [x[0] for x in cursor.description]
        result = cursor.fetchall()
        json_data = []
        for result in result:
            json_data.append(dict(zip(row_headers, result)))
        resp = json.dumps(json_data)

        return resp


@app.route('/')
def default():
    return " add jobs to what you typed bud"


api.add_resource(Jobs, '/jobs')  # Route_1

api.add_resource(Job_title, '/jobs/<job_title>')  # Route_2

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
