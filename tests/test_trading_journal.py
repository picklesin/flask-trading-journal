from app.models import *
from app import db

    


def test_register(client, app):
    response = client.post('/register', data={"email": "test@test.com", 
                                              "password": "testpassword", 
                                              "confirm_password": "testpassword", 
                                              "username": "testing"})

    with app.app_context():
        user = User.query.first()
        assert user.email == "test@test.com"
        assert user.username == "testing"
        assert user.password != "testpassword"

        
def test_login(client, app, user):
    response = client.post('/login', data={"username": "testing", "password": "testpassword"}, follow_redirects=True)

    with app.app_context():
        user = User.query.first()
        assert user.username == "testing"
        assert user.password != "testpassword"
        assert b"<title>Dashboard</title>" in response.data
        assert b"<h2>Welcome back, {{ username }}</h2>"
        


def test_entry(client, app, user, entries):

    login_response = client.post('/login', data={"username": "testing", "password": "testpassword"}, follow_redirects=True)

    response = client.post('/entry', data={
            "stock_sym":"AAPL",
            "price_entry":"125.25",
            "price_exit":"136.9",
            "qty":"2",
            "entry_date":"2026-01-22",
            "exit_date":"2026-04-21",
            "status":"Long",
            "entry_journal":"good"}, follow_redirects=True)
    
    with app.app_context():
        entry = TradeEntry.query.first()
        assert entry is not None
        assert entry.stock_sym == "AAPL"
        assert entry.qty == 2
        assert b"<title>Entry</title>" in response.data
    



