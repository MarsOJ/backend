from flask import session
import json

# This file is pytest-related part, run "pytest" in terminal and automatically start a test

def test_favourite(client):
    question1_data = {
      'classification': 1,
      'content': '判断以下命题',
      'code':'```C++\n#include <cstdlib>\n...\n```',
      'answer':['B','C', 'A'],
      'explanation':'hk for .hk, us for .us, cn for .cn',
      'subproblem':[
          {'content':'香港的顶级域名是：', 'choice':['.cn','.hk','.us','.com']}, 
          {'content':'美国的顶级域名是：', 'choice':['.cn','.hk','.us','.com']}, 
          {'content':'中国的顶级域名是：', 'choice':['.cn','.hk','.us','.com']}, 
      ],
      'source': 'CSP-J',
      'difficultyInt':1,
  }
    favorite_data = {
   'p':1,
   'itemPerPage':1,
    #  'id':// if not exists -> default favorite
}
    user_data = {
        "username": "hsu1023",
        "password": "123456",
        "name": 'list_a'
    }
    
    with client:
        # res = client.delete('/account/delete/', json=user_data)
        # assert '200' in str(res)
        res = client.post('/account/register/', json=user_data)
        assert '200' in str(res)
        client.post('/account/login/', json=user_data)
        assert "username" in session

        res = client.post('/question/insert/', json=question1_data)
        assert '200' in str(res)

        problem_res = client.get('/question/list/?p=1&itemPerPage=1')
        assert '200' in str(problem_res)
        problem = json.loads(problem_res.data)[0]
        problem_id = problem['id']

        res = client.post('/favorite/list/', json=user_data)
        assert '200' in str(res)

        res = client.get('/favorite/list/', json=user_data)
        assert '200' in str(res)
        list = json.loads(res.data)[0]
        list_id = list['id']
        list1_default = list_id
        print('list:',list)

        user_data['id'] = list_id
        user_data['newName'] = 'hello'
        res = client.put('/favorite/list/', json=user_data)
        assert '400' in str(res)
        res = client.delete('/favorite/list/', json=user_data)
        assert '400' in str(res)

        user_data['name'] = 'notdefault'
        res = client.post('/favorite/list/', json=user_data)
        assert '200' in str(res)
        res = client.get('/favorite/list/', json=user_data)
        assert '200' in str(res)
        list = json.loads(res.data)[-1] 
        list_id = list['id']
        print('second list:',list)
        user_data['id'] = list_id
        user_data['newName'] = 'yes'
        res = client.put('/favorite/list/', json=user_data)
        assert '200' in str(res)

        user_data['destID'] = list_id
        user_data['problemID'] = problem_id
        res = client.post('/favorite/problem/', json=user_data)
        assert '200' in str(res)
        user_data['problemID'] = list_id
        res = client.put('/favorite/problem/', json=user_data)
        assert '400' in str(res)
        user_data['destID'] = list1_default
        user_data['sourceID'] = list_id
        user_data['problemID'] = problem_id
        user_data['delete'] = False
        res = client.put('/favorite/problem/', json=user_data)
        assert '200' in str(res)
        res = client.get('/favorite/problem/?p=1&itemPerPage=1&id={}'.format(list_id))
        assert '200' in str(res)
        res = client.delete('/favorite/problem/', json=user_data)
        assert '200' in str(res)

        res = client.delete('/question/delete/', json={
         'problemID':[problem_id]
        })
        assert '200' in str(res) 

        res = client.delete('/account/delete/', json=user_data)
        assert '200' in str(res)


        # res = client.delete('/account/delete/', json=user_data)
        # assert '200' in str(res)

        # res = client.post('/info/insert/', json=bad_info1_data)
        # assert "Bad Request",400 == res
        # res = client.post('/info/insert/', json=info2_data)
        # assert '200' in str(res)
        # res = client.get('/info/get-latest/')
        # res_first = json.loads(res.data)[0]
        # res_first_id = res_first['id']
        # assert '软件工程' in str(res_first)
        
        # res = client.get('/info/get-latest/', json={'lastId':res_first_id})
        # res_second = json.loads(res.data)[0]
        # res_second_id = res_second['id']
        # assert 'Software Engineering' in str(res_second)
        # res = client.delete('/info/delete/',json = {'id':res_first_id})
        # assert '200' in str(res)
        # res = client.get('/info/get-latest/', json={'lastId':''})
        # assert '软件工程' in str(json.loads(res.data)[0])
        # res = client.get('/info/details/{}'.format(res_second_id))
        # assert 'for me personally' in str(json.loads(res.data))
        # info1_data['id'] = res_first_id
        # res = client.post('/info/update/', json=info1_data)
        # assert '200' in str(res)
        # res = client.delete('/info/delete/',json = {'id':res_first_id})
        # assert '200' in str(res)
        # res = client.delete('/info/delete/',json = {'id':res_second_id})
        # assert '200' in str(res)
        # res = client.get('/info/count/')
        # assert '200' in str(res)
        # res = client.get('/info/list/?p=1&itemPerPage=1')
        # assert '200' in str(res)