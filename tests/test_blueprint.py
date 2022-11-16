from flask import session

# This file is pytest-related part, run "pytest" in terminal and automatically start a test

def test_index(client):
    response = client.get("/")
    assert b"<p>Hello, World!</p>" in response.data

def test_blueprint(client):
    response = client.get("/database/")
    assert b"Database Index" in response.data    
    response = client.get("/account/")
    assert b"Account Index" in response.data 
    response = client.get("/info/")
    assert b"Info Index" in response.data
    response = client.get("/question/")
    assert b"Question Index" in response.data