from flask import Blueprint, Flask, request, session, jsonify
from views.database import *
from views.question import *
from views.account import login_required, authority_required
import json

info_bp = Blueprint("info", __name__)

# use blueprint as app
@info_bp.route("/")
def info_index():
    return "Info Index"

@info_bp.route("/insert/", methods=['POST'])
def insert_info():
    """
    新建一条资讯
    ---
    tags:
      - 资讯
    description:
        新建资讯接口,json格式,成功返回“Success", 200
    parameters:
      - name: title
        type: string
        required: true
        description: 标题
      - name: content
        type: string
        required: true
        description: 内容
      - name: source
        type: string
        required: true
        description: 来源
    responses:
      200:
          description: OK,return "Success", 200
      400:
        description: return "Insert Error", 400或"Bad Request", 400
    """
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

@info_bp.route("/update/", methods=['POST'])
def update_info():
    """
    更新特定资讯
    ---
    tags:
      - 资讯
    description:
        更新特定资讯接口,json格式,成功返回“Success", 200
    parameters:
      - name: id
        type: object<id>
        required: true
        description: 资讯的数据库的id
      - name: title
        type: string
        required: true
        description: 更新后的标题
      - name: content
        type: string
        required: true
        description: 更新后的内容
      - name: source
        type: string
        required: true
        description: 更新后的来源
    responses:
      200:
          description: OK,return "Success", 200
      400:
        description: return "Insert Error", 400或"Bad Request", 400
    """
    try:
        data = json.loads(request.data)
        _id = data['id']
        title = data['title']
        content = data['content']
        source = data['source']
    except Exception as e:
        print(e)
        return "Bad Request", 400
    if db_update_info(_id, title, content, source):
        return "Success", 200
    return "Insert Error", 400

@info_bp.route("/delete/", methods=['DELETE'])
def delete_info():
    """
    删除特定资讯列表
    ---
    tags:
      - 资讯
    description:
        更新特定资讯接口,json格式,成功返回[成功删除的数量], 200
    parameters:
      - name: id
        type: object<id> list 
        required: true
        description: 资讯的数据库的id的list
    responses:
      200:
          description: OK,return [成功删除的数量], 200
      400:
        description: return "Bad Request", 400
    """
    try:
        data = json.loads(request.data)
        id_list = data['id']
        success_num = 0
        for info_id in id_list:
            if db_delete_info(info_id):
                success_num += 1
        return json.dumps([success_num]), 200
    except Exception as e:
        return str(e), 400

@info_bp.route("/details/<id>", methods=['GET'])
def get_details(id):
    """
    获取特定资讯的详细信息
    ---
    tags:
      - 资讯
    description:
        获取特定资讯的详细信息接口,json格式,成功返回list, 200
    parameters:
      - name: id
        type: object<id>
        required: true
        description: 资讯的数据库的id
    responses:
      200:
        description: OK,return list, 200
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
            source:
              type: string
            date:
              type: object
              description: format "YYYY-MM-DD HH:mm:ss.mmmmmm"
      400:
        description: return "Get Details Error", 400或"Get Details Error", 400
    """
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
    """
    获取最新资讯详细信息
    ---
    tags:
      - 资讯
    description:
        从指定id的资讯之后获取5条最近资讯，不指定id或指定空字符串id则默认返回当前时间最近5条资讯
    parameters:
      - name: lastId
        type: object<id>
        required: false
        description: 资讯的数据库的id
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
            source:
              type: string
            date:
              type: object
              description: format "YYYY-MM-DD HH:mm:ss.mmmmmm"
      400:
        description: return "Get Error", 400
    """
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


@info_bp.route("/list/", methods=['GET'])
def get_list():
    """
    获取特定资讯的详细信息
    ---
    tags:
      - 资讯
    description:
        分页显示info，其中content显示前20个字符
    parameters:
      - name: p
        type: args
        required: true
        description: 页面数量，args
      - name: itemPerPage
        type: args
        required: true
        description: 一个页面含有info的数量，args
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
            source:
              type: string
            date:
              type: object
              description: format "YYYY-MM-DD HH:mm:ss.mmmmmm"
      400:
        description: return "database error", 400
    """
    try:
        page = int(request.args.get('p'))
        itemPerPage = int(request.args.get('itemPerPage'))
        find_res, state = db_list_info(page, itemPerPage)
        for item in find_res:
            item['id'] = str(item['_id'])
            del item['_id']
            # del item['content']
            item['content'] = item['content'][:20]
            item['date'] = item['date'].strftime('%Y-%m-%d')
        if not state:
            raise Exception('database error')
        return json.dumps(find_res), 200
    except Exception as e:
        print(e)
        return str(e), 400

@info_bp.route("/count/", methods=['GET'])
def info_count():
    """
    管理员查询info个数
    ---
    tags:
      - 资讯
    description:
        管理员查询info个数
    responses:
      200:
        description: OK,return {"count"： int}, 200
      400:
        description: return 'database error', 400
    """
    try:
        select_res, state = db_count_info()
        print(select_res, type(select_res))
        if not state:
            raise Exception('database error')
        return json.dumps({'count':select_res}), 200
    except Exception as e:
        print(e)
        return str(e), 400
