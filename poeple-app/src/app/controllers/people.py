import os
from flask import Blueprint
from bson import json_util
from flask import request
from flask.wrappers import Response
from werkzeug.utils import redirect
from src.app.services import main
from src.app.utils import verify_token
from src.app import mongo_client


people = Blueprint("people", __name__, url_prefix="/people")

@people.route("/", methods=['GET'])
def create_personal_info():
    try:
        user_info = main()
        user = user_info['profile']
        user_data = {
            'name': user['name'],
            'email': user['email']
        }
        contacts = user_info['contacts']
        user_exists = mongo_client.users.find_one({'email': user['email']})
        if not user_exists:
            mongo_client.users.insert_one(user_data)
            user_created = mongo_client.users.find_one({'email': user['email']})
            contacts_info = {
                'user_id': user_created['_id'],
                'contacts': contacts
                }
            mongo_client.contacts.insert_one(contacts_info)
        else:
            user_id = user_exists['_id']
            contacts_info = {
                'user_id': user_exists['_id'],
                'contacts': contacts
                }
            mongo_client.contacts.insert_one(contacts_info)
        return Response(
            response=json_util.dumps(user_info),
            status=200,
            mimetype="application/json")
    except Exception as e:
        print(e)
        return {'error': 'Something went wrong...'}, 500


@people.route("/verify/", methods=['GET'])
def auth_jwt():
    token = request.args.get('token')
    check_token = verify_token(token)
    if check_token:
        response = {'status': 'true'}
    else:
        response = {'status': 'false'}
    return Response(
        response=json_util.dumps(response),
        status=200,
        mimetype="application/json")


@people.route("/logout", methods=['GET'])
def user_logout():
    try:
        if os.path.exists('token.json'):
            os.remove('token.json')
            return {'success': 'Token removed.'}, 200
    except Exception:
        return {"error": "Token could not be removed."}, 500