from bson.objectid import ObjectId
from views.database import *
from flask import Blueprint, Flask, request, session, jsonify
import pymongo
from bson.objectid import ObjectId
import datetime
import random
import json

favorite_bp = Blueprint("favorite", __name__)

@favorite_bp.route("/list/", methods=['POST'])
def favorite_list_post():
    """
    添加收藏夹
    ---
    tags:
      - 收藏夹
    description:
        添加收藏夹,json格式
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: name
        type: string
        required: true
        description: 收藏夹名称
    responses:
      200:
        description: return [{格式如下}], 200
        schema:
          id: id
          properties:
            id:
              type: object<id>
              description: The id of the info
            title:
              type: string
            content:
              type: string
            type:
              type: int
            date:
              type: object
              description: format "YYYY-MM-DD HH:mm:ss.mmmmmm"
      400:
        description: return error_description, 400
    """
    data = json.loads(request.data)
    try:
        username = session['username']
        name = data['name']
        print(name)
        _, state = db_insert_favorite(username=username, favorite_name=name)
        print(_)
        if state:
            return 'success', 200
        return _, 400
    except Exception as e:
        print(e)
        return str(e),400

@favorite_bp.route("/list/", methods=['DELETE'])
def favorite_list_delete():
    """
    删除收藏夹
    ---
    tags:
      - 收藏夹
    description:
        删除特定收藏夹,json格式,成功返回'success', 200,默认收藏夹不可被删除
    parameters:
      - name: id
        type: object<id>  
        required: true
        description: 收藏夹的数据库的id
    responses:
      200:
          description: OK,return 'success', 200
      400:
        description: return "Bad Request", 400 eg:'Default cannot be removed', 400
    """
    data = json.loads(request.data)
    try:
        username = session['username']
        favoriteID = data['id']
        if favoriteID == '0':
            return 'Default cannot be removed', 400
        _, state = db_delete_favorite(username=username, favorite_id=favoriteID)
        if state:
            return 'success', 200
        return _, 400
    except Exception as e:
        print(e)
        return str(e),400

@favorite_bp.route("/list/", methods=['PUT'])
def favorite_list_put():
    """
    重命名收藏夹
    ---
    tags:
      - 收藏夹
    description:
        重命名特定收藏夹,json格式,成功返回'success', 200，默认收藏夹不可重命名
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: name
        type: string
        required: true
        description: 收藏夹名称
      - name: newName
        type: string
        required: true
        description: 收藏夹新名称
    responses:
      200:
          description: OK,return 'success', 200
      400:
        description: return "Bad Request", 400 eg:'Default cannot be removed', 400
    """
    data = json.loads(request.data)
    try:
        print('enter put(/favorite/list/')
        username = session['username']
        favoriteID = data['id']
        new_name = data['newName']
        # print('put(/favorite/list/',favoriteID)
        if favoriteID == '0':
            return 'Default cannot be renamed', 400
        # print('thete put(/favorite/list/')
        _, state = db_rename_favorite(username=username, new_name=new_name, favorite_id=favoriteID)
        # print('hello put(/favorite/list/')
        if state:
            return 'success', 200
        return _, 400
    except Exception as e:
        print(e)
        return str(e), 400

@favorite_bp.route("/list/", methods=['GET'])
def favorite_list_get():
    """
    查看收藏夹列表
    ---
    tags:
      - 收藏夹
    description:
        查看收藏夹列表,json格式,成功返回 列表, 200
    responses:
      200:
        description: OK,return [{如下格式}], 200
        schema:
          id: id
          properties:
            id:
              type: object<id>
              description: The id of the collection
            name:
              type: string
            content:
              type: string
            default:
              type: int
            problemNum:
              type: int
      400:
        description: return "Get Details Error", 400或"Get Details Error", 400
    """
    try:
        username = session['username']
        select_res, state = db_select_all_favorites(username=username)
        # print(select_res)
        res = []
        for k, v in select_res.items():
            res.append({
                'id': k,
                'name': v['name'],
                'default': True if k == '0' else False,
                'problemNum':len(v['problemID']),
            })
        # print(res)
        return json.dumps(res), 200
    except Exception as e:
        print(e)
        return str(e), 400

# @favorite_bp.route("/list/", methods=['POST', 'DELETE', 'PUT', 'GET'])
# def favorite_list():
#     # """
#     # 用户收藏夹列表
#     # ---
#     # tags:
#     #   - 用户收藏夹
#     # description:
#     #     用户登录接口,json格式,注册成功返回username,200
#     # parameters:
#     #   - name: password
#     #     type: string
#     #     required: true
#     #     description: 密码
#     # responses:
#     #   200:
#     #       description: OK,return 'success', 200【'POST', 'DELETE', 'PUT'】。{'id': ,'name': ,'default': True if k == '0' else False,'problemNum':len(v['problemID']),}【'GET'】
#     #   400:
#     #     description: error_description Error
#     # """
#     if (request.method == 'POST'):
#         data = json.loads(request.data)
#         try:
#             username = session['username']
#             name = data['name']
#             print(name)
#             _, state = db_insert_favorite(username=username, favorite_name=name)
#             print(_)
#             if state:
#                 return 'success', 200
#             return _, 400
#         except Exception as e:
#             print(e)
#             return str(e),400
#     elif (request.method == 'DELETE'):
#         data = json.loads(request.data)
#         try:
#             username = session['username']
#             favoriteID = data['id']
#             if favoriteID == '0':
#                 return 'Default cannot be removed', 400
#             _, state = db_delete_favorite(username=username, favorite_id=favoriteID)
#             if state:
#                 return 'success', 200
#             return _, 400
#         except Exception as e:
#             print(e)
#             return str(e),400

#     elif (request.method == 'PUT'):
#         data = json.loads(request.data)
#         try:
#             print('enter put(/favorite/list/')
#             username = session['username']
#             favoriteID = data['id']
#             new_name = data['newName']
#             print('put(/favorite/list/',favoriteID)
#             if favoriteID == '0':
#                 return 'Default cannot be renamed', 400
#             print('thete put(/favorite/list/')
#             _, state = db_rename_favorite(username=username, new_name=new_name, favorite_id=favoriteID)
#             print('hello put(/favorite/list/')
#             if state:
#                 return 'success', 200
#             return _, 400
#         except Exception as e:
#             print(e)
#             return str(e), 400

#     elif (request.method == 'GET'):
#         try:
#             username = session['username']
#             select_res, state = db_select_all_favorites(username=username)
#             # print(select_res)
#             res = []
#             for k, v in select_res.items():
#                 res.append({
#                     'id': k,
#                     'name': v['name'],
#                     'default': True if k == '0' else False,
#                     'problemNum':len(v['problemID']),
#                 })
#             # print(res)
#             return json.dumps(res), 200
#         except Exception as e:
#             print(e)
#             return str(e), 400


@favorite_bp.route("/problem/", methods=['POST'])
def favorite_problem_post():
    """
    将题目加入收藏夹
    ---
    tags:
      - 收藏夹
    description:
        将题目加入收藏夹,json格式
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: destID
        type: object<id>
        required: true
        description: 收藏夹的id
      - name: problemID
        type: object<id>
        required: true
        description: 添加的题目的id
    responses:
      200:
        description: OK,return  200
      400:
        description: return error_description, 400
    """
    data = json.loads(request.data)
    try:
        print('enter favorite_problem')
        username = session['username']
        favoriteID = data['destID']
        problemID = data['problemID']
        _, state = db_insert_favorite_problem(username=username, favorite_id=favoriteID, problem_id=problemID)
        print(_)
        if state:
            return json.dumps(list(_)), 200
        return _, 400
    except Exception as e:
        print(e)
        return str(e), 400

@favorite_bp.route("/problem/", methods=['DELETE'])
def favorite_problem_delete():
    """
    将题目从收藏夹中删除
    ---
    tags:
      - 收藏夹
    description:
        将题目从收藏夹中删除,json格式
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: sourceID
        type: object<id>
        required: true
        description: 收藏夹的id
      - name: problemID
        type: object<id>
        required: true
        description: 添加的题目的id
    responses:
      200:
        description: OK,return  200
      400:
        description: return error_description, 400
    """
    data = json.loads(request.data)
    try:
        username = session['username']
        favoriteID = data['sourceID']
        problemID = data['problemID']
        _, state = db_delete_favorite_problem(username=username, favorite_id=favoriteID, problem_id=problemID)
        print(_)
        if state:
            return json.dumps(list(_)), 200
        return _, 400
    except Exception as e:
        print(e)
        return str(e), 400

@favorite_bp.route("/problem/", methods=['PUT'])
def favorite_problem_put():
    """
    将题目从一个收藏夹移动/添加至另一个收藏夹
    ---
    tags:
      - 收藏夹
    description:
        将题目从一个收藏夹移动/添加至另一个收藏夹,json格式，'Destination cannot be equal to source'
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: sourceID
        type: object<id>
        required: true
        description: 收藏夹的id
      - name: destID
        type: object<id>
        required: true
        description: 即将被加入题目的收藏夹的id
      - name: problemID
        type: object<id>
        required: true
        description: 添加的题目的id
    responses:
      200:
        description: OK,return  200
      400:
        description: return error_description, 400
    """
    data = json.loads(request.data)
    try:
        username = session['username']
        destID = data['destID']
        sourceID = data['sourceID']
        problemID = data['problemID']
        deleteOrNot = data['delete']
        if destID == problemID:
            return 'Destination cannot be equal to source', 400
        _, state = db_move_favorite_problem(username=username,  problem_id=problemID, dest_id=destID, source_id=sourceID, delete_tag = deleteOrNot)
        if state:
            return json.dumps(list(_)), 200
        return _, 400
    except Exception as e:
        print(e)
        return str(e), 400
    
@favorite_bp.route("/problem/", methods=['GET'])
def favorite_problem_get():
    """
    查看特定收藏夹的题目
    ---
    tags:
      - 收藏夹
    description:
        查看特定收藏夹的题目并分页显示,json格式，'Destination cannot be equal to source'
    parameters:
      - name: p
        type: args
        required: true
        description: 页面数量，args
      - name: itemPerPage
        type: args
        required: true
        description: 一个页面含有info的数量，args
      - name: id
        type: args
        required: true
        description: 收藏夹的id
    responses:
      200:
        description: return [{格式如下}], 200
        schema:
          id: id
          properties:
            id:
              type: object<id>
              description: The id of the info
            title:
              type: string
            content:
              type: string
            type:
              type: int
            date:
              type: object
              description: format "YYYY-MM-DD HH:mm:ss.mmmmmm"
      400:
        description: return error_description, 400
    """
    try:
        # import pdb
        # pdb.set_trace()
        print("enter get('/favorite/problem/: ,")
        print(session['username'])
        print('hello')
        username = session['username']
        print('hello')
        page = int(request.args.get('p'))
        itemPerPage = int(request.args.get('itemPerPage'))
        favoriteID = request.args.get('id', None)
        if not favoriteID:
            favoriteID = '0'
        print('hello')
        select_res, state = db_select_favorite_problem(username=username, favorite_id=favoriteID)
        if not state:
            raise Exception('database error')
        
        ret = []
        for pid in select_res[(page - 1) * itemPerPage : page * itemPerPage]:
            res = db_select_questions(_id=pid[0])
            if (len(res) > 0):
                problem = res[0]
                ret.append({
                    'id':str(problem['_id']),
                    'title':problem['title'],
                    'content':problem['content'][:20],
                    'type':problem['classification'],
                    'date':pid[1].strftime("%Y-%m-%d"),
                })
            else:
                ret.append({
                    'id':pid[0],
                    'title':'N/A',
                    'content':'题目不存在',
                    'type':0,
                    'date':"N/A",
                })
        print("200 get('/favorite/problem/: ",ret)
        return json.dumps(ret), 200
    except Exception as e:
        print("400 get('/favorite/problem/: ",e)
        return str(e), 400

# @favorite_bp.route("/problem/", methods=['POST', 'DELETE', 'PUT', 'GET'])
# def favorite_problem():
#     if (request.method == 'POST'):
#         data = json.loads(request.data)
#         try:
#             print('enter favorite_problem')
#             username = session['username']
#             favoriteID = data['destID']
#             problemID = data['problemID']
#             _, state = db_insert_favorite_problem(username=username, favorite_id=favoriteID, problem_id=problemID)
#             print(_)
#             if state:
#                 return json.dumps(list(_)), 200
#             return _, 400
#         except Exception as e:
#             print(e)
#             return str(e), 400
#     elif (request.method == 'DELETE'):
#         data = json.loads(request.data)
#         try:
#             username = session['username']
#             favoriteID = data['sourceID']
#             problemID = data['problemID']
#             _, state = db_delete_favorite_problem(username=username, favorite_id=favoriteID, problem_id=problemID)
#             print(_)
#             if state:
#                 return json.dumps(list(_)), 200
#             return _, 400
#         except Exception as e:
#             print(e)
#             return str(e), 400

#     elif (request.method == 'PUT'):
#         data = json.loads(request.data)
#         try:
#             username = session['username']
#             destID = data['destID']
#             sourceID = data['sourceID']
#             problemID = data['problemID']
#             deleteOrNot = data['delete']
#             if destID == problemID:
#                 return 'Destination cannot be equal to source', 400
#             _, state = db_move_favorite_problem(username=username,  problem_id=problemID, dest_id=destID, source_id=sourceID, delete_tag = deleteOrNot)
#             if state:
#                 return json.dumps(list(_)), 200
#             return _, 400
#         except Exception as e:
#             print(e)
#             return str(e), 400

#     elif (request.method == 'GET'):
#         try:
#             import pdb
#             # pdb.set_trace()
#             print("enter get('/favorite/problem/: ,")
#             print(session['username'])
#             print('hello')
#             username = session['username']
#             print('hello')
#             page = int(request.args.get('p'))
#             itemPerPage = int(request.args.get('itemPerPage'))
#             favoriteID = request.args.get('id', None)
#             if not favoriteID:
#                 favoriteID = '0'
#             print('hello')
#             select_res, state = db_select_favorite_problem(username=username, favorite_id=favoriteID)
#             if not state:
#                 raise Exception('database error')
            
#             ret = []
#             for pid in select_res[(page - 1) * itemPerPage : page * itemPerPage]:
#                 res = db_select_questions(_id=pid[0])
#                 if (len(res) > 0):
#                     problem = res[0]
#                     ret.append({
#                         'id':str(problem['_id']),
#                         'title':problem['title'],
#                         'content':problem['content'][:20],
#                         'type':problem['classification'],
#                         'date':pid[1].strftime("%Y-%m-%d"),
#                     })
#                 else:
#                     ret.append({
#                         'id':pid[0],
#                         'title':'N/A',
#                         'content':'题目不存在',
#                         'type':0,
#                         'date':"N/A",
#                     })
#             print("200 get('/favorite/problem/: ",ret)
#             return json.dumps(ret), 200
#         except Exception as e:
#             print("400 get('/favorite/problem/: ",e)
#             return str(e), 400
