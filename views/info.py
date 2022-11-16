from flask import Blueprint, Flask, request, session, jsonify
from views.database import *
import json

info_bp = Blueprint("info", __name__)
question_bp = Blueprint("question", __name__)

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


@question_bp.route("/")
def question_index():
    return "Question Index"

# 插入只有一问的问题
# 前端需要设置默认值
# title='',classification=[],source='',owner='',
# tag=[],difficultyInt=-1,submit_date='',last_modified_date='',
# nSubmit = -1,nAccept=-1,correct_rate =-1
@question_bp.route("/insert_single/", methods=['POST'])
def insert_single_question():
    data = json.loads(request.data)

    try:
        title = data['title']
        classification= data['classification']
        content= data['content']
        render_mod= data['render_mod']
        answer= data['answer']
        explanation= data['explanation']
        source= data['source']
        owner= data['owner']
        nSubmit= data['nSubmit']
        nAccept= data['nAccept'] 
        correct_rate= data['correct_rate']
        tag= data['tag']
        difficultyInt= data['difficultyInt']
        pid= data['pid']
        hidden_mod= data['hidden_mod']
    except:
        return "Bad Request", 400

    if db_insert_question(title=title,classification=classification,content=content,render_mod=render_mod,
                        answer=answer,explanation=explanation,source =source,owner=owner,
                        nSubmit=nSubmit,nAccept=nAccept,correct_rate=correct_rate,
                        tag=tag,difficultyInt=difficultyInt,
                        pid=pid,hidden_mod=hidden_mod):
        return "Success", 200

    return "Insert Error", 400

@question_bp.route("/delete/<id>", methods=['DELETE'])
def delete_question(id,big_question_id=''):
    print('enter delete_question')
    if db_delete_question(id,big_question_id):
        return "Success", 200
    return "Delete Error", 400

@question_bp.route("/delete_all/", methods=['DELETE'])
def delete_question_all():
    print('enter delete_question_all')
    if db_delete_question_all():
        return "Success", 200
    return "Delete Error", 400

@question_bp.route("/details/<id>", methods=['GET'])
def get_details(id):
    get_details_res = db_select_questions(id)
    try:
        for item in get_details_res:
            item['id'] = str(item['_id'])
            item['str_big_question_id'] = str(item['big_question_id'])
            del item['_id']
            del item['big_question_id']
            item['submit_date'] = item['submit_date'].strftime('%Y-%m-%d')
            item['last_modified_date'] = item['last_modified_date'].strftime('%Y-%m-%d')
    
        return json.dumps(get_details_res), 200
    except:
        return "Get Details Error", 400

@question_bp.route("/random_single/<classfication>", methods=['GET'])
def get_random_single(classfication):
    required_amount_dic = {
    str(classfication):1
    }
    random = db_get_random_questions(['anna'],required_amount_dic)

    if random is False:
        return "Get random single Error", 400
    for item in random:
        item['id'] = str(item['_id'])
        item['str_big_question_id'] = str(item['big_question_id'])
        del item['_id']
        del item['big_question_id']
        item['submit_date'] = item['submit_date'].strftime('%Y-%m-%d')
        item['last_modified_date'] = item['last_modified_date'].strftime('%Y-%m-%d')
    return json.dumps(random), 200

# TODO 不知道一套题多少
@question_bp.route("/random/", methods=['GET'])
def get_random_test():

    required_amount_dic = {
    '0':1
    }
    random = db_get_random_questions(['anna'],required_amount_dic)

    if random is False:
        return "Get random single Error", 400
    for item in random:
        item['id'] = str(item['_id'])
        item['str_big_question_id'] = str(item['big_question_id'])
        del item['_id']
        del item['big_question_id']
        item['submit_date'] = item['submit_date'].strftime('%Y-%m-%d')
        item['last_modified_date'] = item['last_modified_date'].strftime('%Y-%m-%d')
    return json.dumps(random), 200
