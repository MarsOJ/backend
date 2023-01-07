from flask import session

# This file is pytest-related part, run "pytest" in terminal and automatically start a test

def test_login(client):
    user_data = {
        "username": "hsu1023",
        "password": "123456"
    }
    with client:
        # res = client.delete('/account/delete/', json=user_data)
        # assert '200' in str(res)
        res = client.post('/account/register/', json=user_data)
        assert '200' in str(res)
        client.post('/account/login/', json=user_data)
        assert "username" in session
        client.get('/account/info/', json=user_data)
        assert "200" in str(res)
        client.post('/account/profile/', json=user_data)
        assert "200" in str(res)
        client.get('/account/profile/', json=user_data)
        assert "200" in str(res)
        client.post('/account/signature/', json=user_data)
        assert "200" in str(res)
        res = client.delete('/account/delete/', json=user_data)
        assert '200' in str(res)

        pass

def test_logout(client):
    user_data = {
        "username": "hsu1023",
        "password": "123456"
    }
    with client:
        res = client.post('/account/register/', json=user_data)
        assert '200' in str(res)
        client.post('/account/login/', json=user_data)
        assert "username" in session
        res = client.get('/account/state/')
        assert user_data['username'] in str(res.data)

        client.post('/account/logout/')
        assert "username" not in session
        res = client.get('/account/state/')
        assert '400' in str(res)
        res = client.delete('/account/delete/', json=user_data)
        assert '200' in str(res)
        pass

def test_change_password(client):
    user_data = {
        "username": "hsu1023",
        "password": "123456",
    }
    change_password_wrong_data = {
        "username": "hsu1023",
        "password": "12345",
        "newPassword" : "987654",
    }
    change_password_correct_data = {
        "username": "hsu1023",
        "password": "123456",
        "newPassword" : "987654",
    }
    delete_data = {
        "username": "hsu1023",
        "password": "987654",
    }
    with client:
        res = client.post('/account/register/', json=user_data)
        assert '200' in str(res)
        client.post('/account/login/', json=user_data)
        assert "username" in session

        res = client.post('/account/change-password/', json=change_password_wrong_data)
        assert '400' in str(res)
        res = client.post('/account/change-password/', json=change_password_correct_data)
        assert '200' in str(res)

        client.post('/account/logout/')
        assert "username" not in session
        res = client.delete('/account/delete/', json=delete_data)
        assert '200' in str(res)
        pass