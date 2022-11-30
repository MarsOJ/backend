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
            _, state = db_insert_favorite(username=username, favorite_name=name)
            if state:
                return 'success', 200
            return _, 400
        except Exception as e:
            print(e)
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
            return e, 400
            print(e)

    elif (request.method == 'GET'):
        try:
            username = session['username']
            select_res = db_select_all_favorites(username=username)
            res = []
            for fav in select_res:
                res.append({
                    'id': fav['favoriteID'],
                    'name': fav['name'],
                    'default': fav['favoriteID'] == '0',
                })
            return res, 200
        except Exception as e:
            return e, 400
            print(e)
