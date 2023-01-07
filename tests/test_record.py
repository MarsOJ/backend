from flask import session
import json
from views.database import db_competition_settlement_result, db_delete_record
import datetime


# This file is pytest-related part, run "pytest" in terminal and automatically start a test

def test_favourite(client):
    
    favorite_data = {
        'p':1,
        'itemPerPage':1,
            #  'id':// if not exists -> default favorite
    }
    user_data = {
        "username": "hsuuuuuuu1023",
        "password": "123456",
    }
    
    with client:
        # res = client.delete('/account/delete/', json=user_data)
        # assert '200' in str(res)
        res = client.post('/account/register/', json=user_data)
        assert '200' in str(res)
        client.post('/account/login/', json=user_data)
        assert "username" in session

        db_competition_settlement_result([1], ['hsuuuuuuu1023'])
        res = client.get('/record/personal/')
        assert '200' in str(res)
        res = client.get('/record/all/?p=1&itemPerPage=1')
        print('sfgsdsd',res.data)
        record =  json.loads(res.data)[-1]
        print('sfgsdsdrecord',record)
        record_id = record['id']
        res = client.get('/record/rank/',json = user_data)
        assert '200' in str(res)
        print('newest',res.data)

        res = client.get('/record/download/{}'.format(record_id),json = user_data)
        assert '200' in str(res)
        res = client.get('/record/download-all/',json = user_data)
        assert '200' in str(res)

        res = client.get('/record/count/',json = user_data)
        assert '200' in str(res)

        db_delete_record(record_id)

        res = client.delete('/account/delete/', json=user_data)
        assert '200' in str(res)



