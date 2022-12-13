from flask import Blueprint, Flask, request, session, jsonify, make_response, send_from_directory
from views.database import *
from views.account import login_required, authority_required
import json
import csv
import os
import shutil

record_bp = Blueprint("record", __name__)

TEMPFILES_DIR = 'tempfiles'

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
            item['scores'] = [ sum(user['score']) for user in item['userResult']]
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
            item['scores'] = [ sum(user['score']) for user in item['userResult']]
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

# @authority_required
@record_bp.route("/download/", methods=['GET'])
def download_record():
    try:
        find_res, state = db_list_record()        
        if state is False:
            return "Get Error", 400
        
        write_content = []
        def index(li, idx):
            try:
                return li[idx]
            except:
                return 'N/A'
        for res in find_res:
            write_content.append({
                '对战记录ID':str(res['_id']),
                '时间': res['date'].strftime("%Y-%m-%d"),
                '第一名': index(res['userList'], 0),
                '第二名': index(res['userList'], 1),
                '第三名': index(res['userList'], 2),
                '第四名': index(res['userList'], 3),
                '题目ID': str(res['problemID']),
            })
        filedir = TEMPFILES_DIR + '/' + str(uuid.uuid4())
        os.makedirs(filedir)
        labels = ['对战记录ID', '时间', '第一名', '第二名', '第三名', '第四名', '题目ID']
        with open(filedir + r'/record.csv', 'w', encoding='GB2312',) as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writeheader()
            for elem in write_content:
                writer.writerow(elem)
        response = make_response(send_from_directory(filedir, 'record.csv', as_attachment=True))
        shutil.rmtree(filedir)
        return response
        # return 'True', 200
    except Exception as e:
        print(e)
        return str(e), 200

@authority_required
@record_bp.route("/count/", methods=['GET'])
def get_cound():
    try:
        res, state = db_count_record()
        if not state:
            raise('database error')
        return json.dumps({'count':res}), 200
    except Exception as e:
        return e, 400