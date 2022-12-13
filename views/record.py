from flask import Blueprint, Flask, request, session, jsonify
from views.database import *
from views.account import login_required, authority_required
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
            last_id = data['lastID']
        except:
            last_id = ''
        username = session['username']
        find_res, state = db_next_record(username=username, _id=last_id)
        print(find_res)
        if state is False:
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

@authority_required
@record_bp.route("/all/", methods=['GET'])
def get_list():
    try:
        page = int(request.args.get('p'))
        itemPerPage = int(request.args.get('itemPerPage'))
        find_res, state = db_list_record(page, itemPerPage)
        if state is False:
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
        return str(e), 400

@record_bp.route("/rank/", methods=['GET'])
def get_rank():
    try:
        find_res, state = db_ranklist()
        if not state:
            raise('Database Error')
        res = [{'username':user['username'], 'signature':user['signature'], 'score':user['credit']} for user in find_res]
        return json.dumps(res), 200
    except Exception as e:
        return e, 400