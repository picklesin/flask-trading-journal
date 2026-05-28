from datetime import datetime
from datetime import timezone
from flask_login import UserMixin
from app import db


# Database for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    entries = db.relationship('Entry', back_populates='parent',uselist=False, cascade='all, delete')
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())


# Database for each entry
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)) 
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   
    parent = db.relationship('User', back_populates='entries')              
    trade_info = db.relationship('TradeEntry', back_populates='parent', uselist=False, cascade='all, delete')    


# Database for trade info
class TradeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price_entry = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    price_exit = db.Column(db.Numeric(precision=10, scale=2), nullable=True)  
    stock_sym = db.Column(db.String, nullable=False)
    qty = db.Column(db.Numeric, nullable=False)         
    entry_journal = db.Column(db.Text, nullable=False)      
    entry_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    exit_date = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(db.String, nullable=True)
    

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable=False, unique=True)
    parent = db.relationship('Entry', back_populates='trade_info')

