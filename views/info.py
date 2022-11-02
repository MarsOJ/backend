from flask import Blueprint, Flask, request, session, jsonify
from views.database import *
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

@info_bp.route("/delete/<id>", methods=['DELETE'])
def delete_info(id):
    if db_delete_info(id):
        return "Success", 200
    return "Delete Error", 400

@info_bp.route("/details/<id>", methods=['GET'])
def get_details(id):
    selete_res = db_selete_info(id)
    if selete_res:
        try:
            selete_res['id'] = str(selete_res['_id'])
            del selete_res['_id']
            return selete_res, 200
        except:
            return "Get Details Error", 400
    return "Get Details Error", 400

@info_bp.route("/get-last/", methods=['GET'])
def get_last():
    find_res = db_tail_info()
    for item in find_res:
        item['id'] = str(item['_id'])
        del item['_id']
    return find_res, 200