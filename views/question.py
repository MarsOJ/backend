from bson.objectid import ObjectId
from views.database import *
from flask import Blueprint, Flask, request, session, jsonify
import pymongo
from bson.objectid import ObjectId
import datetime
import random
import json

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


@question_bp.route("/insert-single/", methods=['POST'])
def insert_single_question():
    data = json.loads(request.data)
    try:
        classification= data['classification']
        content= data['content']
        answer= data['answer']
        explanation= data['explanation']
        subproblem = data['subproblem']
        source= data['source']
        owner= data['owner']
        nSubmit= data['nSubmit']
        nAccept= data['nAccept'] 
        correct_rate= data['correct_rate']
        tag= data['tag']
        difficultyInt= data['difficultyInt']
        hidden_mod= data['hidden_mod']
    except:
        return "Bad Request", 400

    if db_insert_question(classification=classification,content=content, subproblem=subproblem,
                        answer=answer,explanation=explanation,source =source,owner=owner,
                        nSubmit=nSubmit,nAccept=nAccept,correct_rate=correct_rate,
                        tag=tag,difficultyInt=difficultyInt,
                        hidden_mod=hidden_mod):
        return "Success", 200

    return "Insert Error", 400

# @question_bp.route("/insert_big_single/", methods=['POST'])
# def insert_big_single_questions():
#     data = json.loads(request.data)
#     print('type of data',type(data))
#     data_list = data['data']
#     if db_insert_big_questions(data_list):
#         return "Success", 200

#     return "Insert Error", 400


# @question_bp.route("/update-single/<id>", methods=['POST'])
# def update_single_question(id):
#     data = json.loads(request.data)

#     try:
#         # print('enter update_single_question')
#         tmp_id = data['id']
#         title = data['title']
#         classification= data['classification']
#         content= data['content']
#         render_mod= data['render_mod']

#         answer= data['answer']
#         explanation= data['explanation']
#         source= data['source']
#         owner= data['owner']
#         nSubmit= data['nSubmit']
#         nAccept= data['nAccept'] 

#         correct_rate= data['correct_rate']
#         tag= data['tag']
#         difficultyInt= data['difficultyInt']
#         pid= data['pid']
#         hidden_mod= data['hidden_mod']
#     except:
#         return "Bad Request", 400

#     print('enter if')
#     if db_update_question(_id = tmp_id,title=title,classification=classification,content=content,render_mod=render_mod,
#                         answer=answer,explanation=explanation,source =source,owner=owner,
#                         nSubmit=nSubmit,nAccept=nAccept,correct_rate=correct_rate,
#                         tag=tag,difficultyInt=difficultyInt,
#                         pid=pid,hidden_mod=hidden_mod):
#         return "Success", 200

#     return "Insert Error", 400


# @question_bp.route("/delete/<id>", methods=['DELETE'])
# def delete_question(id,big_question_id=''):
#     print('enter delete_question')
#     if db_delete_question(id,big_question_id):
#         return "Success", 200
#     return "Delete Error", 400

# @question_bp.route("/delete_all/", methods=['DELETE'])
# def delete_question_all():
#     print('enter delete_question_all')
#     if db_delete_question_all():
#         return "Success", 200
#     return "Delete Error", 400

# @question_bp.route("/details/<id>", methods=['GET'])
# def get_details(id):
#     get_details_res = db_select_questions(id)
#     try:
#         for item in get_details_res:
#             item['id'] = str(item['_id'])
#             item['str_big_question_id'] = str(item['big_question_id'])
#             del item['_id']
#             del item['big_question_id']
#             item['submit_date'] = item['submit_date'].strftime('%Y-%m-%d')
#             item['last_modified_date'] = item['last_modified_date'].strftime('%Y-%m-%d')
    
#         return json.dumps(get_details_res), 200
#     except:
#         return "Get Details Error", 400

# @question_bp.route("/random_single/<classfication>", methods=['GET'])
# def get_random_single(classfication):
#     required_amount_dic = {
#     str(classfication):1
#     }
#     random = db_get_random_questions(['anna'],required_amount_dic)

#     if random is False:
#         return "Get random single Error", 400
#     for item in random:
#         item['id'] = str(item['_id'])
#         item['str_big_question_id'] = str(item['big_question_id'])
#         del item['_id']
#         del item['big_question_id']
#         item['submit_date'] = item['submit_date'].strftime('%Y-%m-%d')
#         item['last_modified_date'] = item['last_modified_date'].strftime('%Y-%m-%d')
#     return json.dumps(random), 200

# TODO 不知道一套题多少
# @question_bp.route("/random/", methods=['GET'])
# def get_random_test():

#     required_amount_dic = {
#     '0':1
#     }
#     random = db_get_random_questions(['anna'],required_amount_dic)

#     if random is False:
#         return "Get random single Error", 400
#     for item in random:
#         item['id'] = str(item['_id'])
#         item['str_big_question_id'] = str(item['big_question_id'])
#         del item['_id']
#         del item['big_question_id']
#         item['submit_date'] = item['submit_date'].strftime('%Y-%m-%d')
#         item['last_modified_date'] = item['last_modified_date'].strftime('%Y-%m-%d')
#     return json.dumps(random), 200
