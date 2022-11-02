from flask import Blueprint, Flask, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from bson.objectid import ObjectId
import datetime

database_bp = Blueprint("database", __name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["MarsOJ"]

# use blueprint as app
@database_bp.route("/")
def database_index():
    return "Database Index"

def db_select_user(name):
    try:
        collection = db["account"]
        user = {
            'username':name
        }
        return collection.find_one(user) # return dict
    except Exception as e:
        print(e)
        return False

def db_insert_user(name, pw):
    try:
        pwhash = generate_password_hash('NAME:'+name+'|PW:'+pw, method='pbkdf2:sha256', salt_length=8)
        collection = db["account"]
        user = {
            'username':name, 
            'pwhash':pwhash
        }
        collection.insert_one(user)
        return True
    except:
        return False

def db_verify_user(name, pw):
    try:
        find_res = db_select_user(name)
        if find_res is None:
            return False
        pw = 'NAME:' + name + '|PW:' + pw
        pwhash = find_res['pwhash']
        
        return check_password_hash(pwhash, pw)
    except:
        return False

def db_delete_user(name):
    try:
        collection = db["account"]
        user = {
            'username':name
        }
        delete_res = collection.delete_one(user)
        if delete_res.deleted_count != 1:
            return False
        return True
    except:
        return False

def db_update_user(name, newpw):
    try:
        collection = db["account"]
        user = {
            'username':name
        }
        newpwhash = generate_password_hash('NAME:'+name+'|PW:'+newpw, method='pbkdf2:sha256', salt_length=8)
        update_res = collection.update_one(user, {'$set':{'pwhash':newpwhash}})
        if update_res.modified_count != 1:
            return False
        return True
    except:
        return False

'''
{
    _id: <>
    title: 
    content:
    source:
    time:
}
'''
def db_select_info(_id):
    try:
        collection = db["info"]
        info_data = {
            "_id": ObjectId(_id)
        }
        return collection.find_one(info_data)
    except Exception as e:
        return False

def db_tail_info():
    try:
        collection = db["info"]
        find_res = collection.find({}, sort=[{'date':pymongo.DESCENDING}], limit=5)
        find_res = list(find_res)
        return find_res
    except:
        return False


def db_insert_info(title, content, source):
    try:
        collection = db["info"]
        info_data = {
            'title': title,
            'content': content,
            'source' : source,
            'date': datetime.datetime.now(),
        }
        collection.insert_one(info_data)
        return True
    except:
        return False

def db_delete_info(_id):
    try:
        collection = db["info"]
        info_data = {
            "_id": ObjectId(_id)
        }
        delete_res = collection.delete_one(info_data)
        if delete_res.deleted_count < 1:
            return False
        return True
    except:
        return False

def db_update_info(_id, title, content, source):
    try:
        collection = db["info"]
        update_data = {
            'title': title,
            'content': content,
            'source' : source,
        }
        update_res = collection.update_one(user, {'$set':update_data})
        if update_res.modified_count < 1:
            return False
        return True
    except:
        return False