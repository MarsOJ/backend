from flask import Blueprint, Flask, request, session, jsonify
from views.database import *
from views.question import *
from views.account import login_required, authority_required
import json

info_bp = Blueprint("info", __name__)

# use blueprint as app
@info_bp.route("/")
def info_index():
    return "Info Index"

@info_bp.route("/insert/", methods=['POST'])
def insert_info():
    data = json.loads(request.data)
    try:
        title = data['title']
        content = data['content']
        source = data['source']
    except:
        return "Bad Request", 400
    if db_insert_info(title, content, source):
        return "Success", 200
    return "Insert Error", 400

@info_bp.route("/update/", methods=['POST'])
def update_info():
    try:
        data = json.loads(request.data)
        _id = data['id']
        title = data['title']
        content = data['content']
        source = data['source']
    except Exception as e:
        print(e)
        return "Bad Request", 400
    if db_update_info(_id, title, content, source):
        return "Success", 200
    return "Insert Error", 400

@info_bp.route("/delete/", methods=['DELETE'])
def delete_info():
    try:
        data = json.loads(request.data)
        id_list = data['id']
        success_num = 0
        for info_id in id_list:
            if db_delete_info(info_id):
                success_num += 1
        return json.dumps([success_num]), 200
    except Exception as e:
        return str(e), 400

@info_bp.route("/details/<id>", methods=['GET'])
def get_details(id):
    selete_res = db_select_info(id)
    if selete_res:
        try:
            selete_res['id'] = str(selete_res['_id'])
            del selete_res['_id']
            selete_res['date'] = selete_res['date'].strftime("%Y-%m-%d")
            return json.dumps(selete_res), 200
        except:
            return "Get Details Error", 400
    return "Get Details Error", 400

@info_bp.route("/get-latest/", methods=['GET', 'POST'])
def get_last():
    try:
        data = json.loads(request.data)
        last_id = data['lastId']
    except:
        last_id = ''
    find_res = db_next_info(last_id)
    if find_res is False:
        return "Get Error", 400
    for item in find_res:
        item['id'] = str(item['_id'])
        del item['_id']
        del item['content']
        item['date'] = item['date'].strftime('%Y-%m-%d')
    return json.dumps(find_res), 200


@info_bp.route("/list/", methods=['GET'])
def get_list():
    try:
        page = int(request.args.get('p'))
        itemPerPage = int(request.args.get('itemPerPage'))
        find_res, state = db_list_info(page, itemPerPage)
        for item in find_res:
            item['id'] = str(item['_id'])
            del item['_id']
            # del item['content']
            item['content'] = item['content'][:20]
            item['date'] = item['date'].strftime('%Y-%m-%d')
        if not state:
            raise Exception('database error')
        return json.dumps(find_res), 200
    except Exception as e:
        print(e)
        return str(e), 400

@info_bp.route("/count/", methods=['GET'])
def info_count():
    try:
        select_res, state = db_count_info()
        print(select_res, type(select_res))
        if not state:
            raise Exception('database error')
        return json.dumps({'count':select_res}), 200
    except Exception as e:
        print(e)
        return str(e), 400