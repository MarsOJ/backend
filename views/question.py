from bson.objectid import ObjectId
from views.database import *
from views.account import login_required, authority_required
from flask import Blueprint, Flask, request, session, jsonify
import pymongo
from bson.objectid import ObjectId
import datetime
import random
import json
import os
import shutil

question_bp = Blueprint("question", __name__)

# 从前端接收答案后，判断答案是否正确的函数
# 前端返回一个string[]

@question_bp.route("/")
def question_index():
    return "Question Index"
# 插入只有一问的问题
# 前端需要设置默认值
# title='',classification=[],source='',owner='',
# tag=[],difficultyInt=-1,submit_date='',last_modified_date='',
# nSubmit = -1,nAccept=-1,correct_rate =-1

TEMPFILES_DIR = 'tempfiles'

@question_bp.route("/upload/", methods=['POST'])
def upload_problem():
    try:
        file = request.files['file']
        filedir = TEMPFILES_DIR + '/' + str(uuid.uuid4())
        os.makedirs(filedir)
        filename = file.filename
        filepath = filedir + '/' + filename
        file.save(filepath)
        try:
            with open(filepath, 'r', encoding='GB2312') as f:
                data = json.load(f)
        except:
            print('utf8')
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        success_num = 0
        print(data)
        for item in data:
            if db_insert_question(**item):
                success_num += 1
        shutil.rmtree(filedir)
        print(success_num)
        return json.dumps({'success_num':success_num}), 200
    except Exception as e:
        print(str(e))
        return str(e), 200
        


@question_bp.route("/insert/", methods=['POST'])
def insert_single_question():
    data = json.loads(request.data)
    try:
        classification= data['classification']
        content= data['content']
        answer= data['answer']
        explanation= data['explanation']
        subproblem = data['subproblem']
        source= data['source']
        owner= session['username']
        difficultyInt= data['difficultyInt']
    except Exception as e:
        print(e)
        return "Bad Request", 400

    if db_insert_question(classification=classification,content=content, subproblem=subproblem,
                        answer=answer,explanation=explanation,source =source,owner=owner,difficultyInt=difficultyInt):
        # print('db_insert_question is True')
        return "Success", 200
    return "Insert Error", 400


@question_bp.route("/update/", methods=['POST'])
def update_single_question():
    data = json.loads(request.data)
    try:
        problem_id = data['id']
        content= data['content']
        answer= data['answer']
        explanation= data['explanation']
        subproblem = data['subproblem']
        source= data['source']
        difficultyInt= data['difficultyInt']
    except:
        return "Bad Request", 400

    if db_update_question(_id=problem_id, content=content, subproblem=subproblem,
                        answer=answer,explanation=explanation,source =source,difficultyInt=difficultyInt):
        return "Success", 200
    return "Insert Error", 400

@authority_required
@question_bp.route("/delete/", methods=['DELETE'])
def delete_question():
    try:
        data = json.loads(request.data)
        print(data)
        id_list = data['problemID']
        print(id_list)
        success_num = 0
        for problem_id in id_list:
            if db_delete_question(problem_id):
                success_num += 1
        return json.dumps([success_num]), 200
    except Exception as e:
        print(e)
        return str(e), 400


@question_bp.route("/details/<id>", methods=['GET'])
def get_details(id):
    try:
        res = db_select_questions(id)
        if (len(res) > 0):
            item = res[0]
            item['id'] = str(item['_id'])
            del item['_id']
            item['submit_date'] = item['submit_date'].strftime('%Y-%m-%d')
            item['last_modified_date'] = item['last_modified_date'].strftime('%Y-%m-%d')
            return json.dumps(item), 200
        else:
            raise Exception('Problem not exists')
    except Exception as e:
        return str(e), 400


@authority_required
@question_bp.route("/list/", methods=['GET'])
def problem_list():
    try:
        page = int(request.args.get('p'))
        itemPerPage = int(request.args.get('itemPerPage'))

        select_res, state = db_list_problem(page, itemPerPage)
        if not state:
            raise Exception('database error')

        ret = []
        for problem in select_res:
            ret.append({
                'id':str(problem['_id']),
                'title':problem['title'],
                'content':problem['content'][:40],
                'type':problem['classification'],
                'date':problem['last_modified_date'].strftime("%Y-%m-%d")
            })
        # print(ret)
        return json.dumps(ret), 200
    except Exception as e:
        print(e)
        return str(e), 400

@authority_required
@question_bp.route("/count/", methods=['GET'])
def problem_count():
    try:
        select_res, state = db_count_problem()
        if not state:
            raise Exception('database error')
        return json.dumps({'count':select_res}), 200
    except Exception as e:
        print(e)
        return str(e), 400

