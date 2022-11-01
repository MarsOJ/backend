from flask import session

# This file is pytest-related part, run "pytest" in terminal and automatically start a test

def test_login(client):
    user_data = {
        "username": "hsu1023",
        "password": "123456"
    }
    with client:
        client.post('/account/init/')
        res = client.post('/account/register/', json=user_data)
        client.post('/account/login/', json=user_data)
        assert "username" in session
        res = client.delete('/account/delete/', json=user_data)
        assert '200' in str(res)
        