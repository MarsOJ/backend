from bson.objectid import ObjectId
from views.database import *
from flask import Blueprint, Flask, request, session, jsonify
import pymongo
from bson.objectid import ObjectId
import datetime
import random
import json

favorite_bp = Blueprint("favorite", __name__)

@favorite_bp.route("/list/", methods=['POST', 'DELETE', 'PUT', 'GET'])
def favorite_list():
    if (request.method == 'POST'):
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
    elif (request.method == 'DELETE'):
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

    elif (request.method == 'PUT'):
        data = json.loads(request.data)
        try:
            username = session['username']
            favoriteID = data['id']
            new_name = data['newName']
            if favoriteID == '0':
                return 'Default cannot be renamed', 400
            _, state = db_rename_favorite(username=username, new_name=new_name, favorite_id=favoriteID)
            if state:
                return 'success', 200
            return _, 400
        except Exception as e:
            print(e)
            return str(e), 400

    elif (request.method == 'GET'):
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

@favorite_bp.route("/problem/", methods=['POST', 'DELETE', 'PUT', 'GET'])
def favorite_problem():
    if (request.method == 'POST'):
        data = json.loads(request.data)
        try:
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
    elif (request.method == 'DELETE'):
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

    elif (request.method == 'PUT'):
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

    elif (request.method == 'GET'):
        try:
            username = session['username']
            page = int(request.args.get('p'))
            itemPerPage = int(request.args.get('itemPerPage'))
            favoriteID = request.args.get('id', None)
            if not favoriteID:
                favoriteID = '0'

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
            print(ret)
            return json.dumps(ret), 200
        except Exception as e:
            print(e)
            return str(e), 400
