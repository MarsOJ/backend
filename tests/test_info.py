from flask import session
import json

# This file is pytest-related part, run "pytest" in terminal and automatically start a test

def test_insert(client):
    
    info1_data = {
        "title": "Software Engineering",
        "source": "Article Generator",
        "content": '''Generally speaking, for me personally, software engineering is not just a momentous event, it can also change my life. In general, we all have to think carefully. How to implement software engineering. Knowing exactly what kind of existence software engineering is is the key to solving all problems. For me personally, software engineering is not just a momentous event, it can also change my life.
        '''
    }
    info2_data = {
        "title": "软件工程",
        "source": "文章生成器",
        "content": '''一般来说， 对我个人而言，软件工程不仅仅是一个重大的事件，还可能会改变我的人生。 一般来讲，我们都必须务必慎重的考虑考虑。 软件工程，到底应该如何实现。 了解清楚软件工程到底是一种怎么样的存在，是解决一切问题的关键。 对我个人而言，软件工程不仅仅是一个重大的事件，还可能会改变我的人生。
        '''
    }
    bad_info1_data = {
        "title": "Software Engineering",
        "source": "Article Generator",
    }
    
    with client:
         res = client.post('/info/insert/', json=info1_data)
         assert '200' in str(res)
         res = client.post('/info/insert/', json=bad_info1_data)
         assert "Bad Request",400 == res
         res = client.post('/info/insert/', json=info2_data)
         assert '200' in str(res)
         res = client.get('/info/get-latest/')
         res_first = json.loads(res.data)[0]
         res_first_id = res_first['id']
         assert '软件工程' in str(res_first)
         res = client.get('/info/get-latest/', json={'lastId':res_first_id})
         res_second = json.loads(res.data)[0]
         res_second_id = res_second['id']
         assert 'Software Engineering' in str(res_second)
         res = client.delete('/info/delete/{}'.format(res_first_id))
         assert '200' in str(res)
         res = client.get('/info/get-latest/', json={'lastId':''})
         assert 'Software Engineering' in str(json.loads(res.data)[0])
         res = client.get('/info/details/{}'.format(res_second_id))
         assert 'for me personally' in str(json.loads(res.data))
         res = client.delete('/info/delete/{}'.format(res_second_id))
         assert '200' in str(res)
         res = client.delete('/info/delete/{}'.format(res_second_id))
         assert '400' in str(res)
        
