import pytest 
from app import create_app, db, bcrypt
from app.models import *
from datetime import date


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
     


@pytest.fixture()
def client(app):
   return app.test_client()

@pytest.fixture()
def user(app):
    with app.app_context():
        user = User(
            email="test@test.com",
            username="testing",
            password=bcrypt.generate_password_hash("testpassword").decode('utf-8')
        )

        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture()
def entries(app, user):
    with app.app_context():
        entry = Entry(
            created_time=date.today(),
            user_id=user.id
        )
        db.session.add(entry)
        db.session.commit()

        posts = TradeEntry(
            stock_sym="AAPL",
            price_entry=125.25,
            price_exit=136.9,
            qty=2,
            entry_date=date(2026, 1, 22),
            exit_date=date(2026, 4, 21),
            status="Long",
            entry_journal="good",
            user_id=user.id,
            entry_id=entry.id

        )

        db.session.add(posts)
        db.session.commit()

    return posts