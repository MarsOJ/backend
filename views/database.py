from flask import Blueprint, Flask, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo

database_bp = Blueprint("database", __name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")

# use blueprint as app
@database_bp.route("/")
def database_index():
    return "Database Index"

def db_select_user(name):
    try:
        db = client["MarsOJ"]
        collection = db["account"]
        user = {
            'username':name
        }
        return collection.find_one(user)
    except:
        return False

def db_insert_user(name, pw):
    try:
        pwhash = generate_password_hash('NAME:'+name+'|PW:'+pw, method='pbkdf2:sha256', salt_length=8)
        db = client["MarsOJ"]
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
        db = client["MarsOJ"]
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
        db = client["MarsOJ"]
        collection = db["account"]
        user = {
            'username':name
        }
        newpwhash = generate_password_hash('NAME:'+name+'|PW:'+newpw, method='pbkdf2:sha256', salt_length=8)
        update_res = collection.update_one(user, {'$set':{'pwhash':newpwhash}})
        if update_res.update_count != 1:
            return False
        return True
    except:
        return False
