from flask import Blueprint, Flask, request, session, jsonify
from views.database import *
import json

record_bp = Blueprint("record", __name__)

# use blueprint as app
@record_bp.route("/")
def record_index():
    return "Record Index"

@record_bp.route("/personal/", methods=['GET', 'POST'])
def get_personal():
    try:
        try:
            data = json.loads(request.data)
            last_id = data['lastId']
        except:
            last_id = ''
        username = session['username']
        find_res = db_next_record(username=username, _id=last_id)
        if find_res is False:
            return "Get Error", 400
        for item in find_res:
            item['id'] = str(item['_id'])
            del item['_id']
            item['rank'] = item['userList']
            del item['userList']
            del item['problemID']
            del item['userResult']
            item['date'] = item['date'].strftime('%Y-%m-%d')
        return json.dumps(find_res), 200
    except Exception as e:
        return e, 400

@record_bp.route("/all/", methods=['GET', 'POST'])
def get_all():
    try:
        try:
            data = json.loads(request.data)
            last_id = data['lastId']
        except:
            last_id = ''
        username = session['username']
        user_info = db_select_user(username)
        if not user_info['authority']:
            return False
        find_res = db_next_record( _id=last_id)
        if find_res is False:
            return "Get Error", 400
        for item in find_res:
            item['id'] = str(item['_id'])
            del item['_id']
            item['rank'] = item['userList']
            del item['userList']
            del item['problemID']
            del item['userResult']
            item['date'] = item['date'].strftime('%Y-%m-%d')
        return json.dumps(find_res), 200
    except Exception as e:
        return e, 400