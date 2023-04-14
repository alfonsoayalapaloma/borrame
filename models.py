from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import validates

from app import db

class Token(db.Model):
    __tablename__ = 'token'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    creation_date = Column(DateTime)
    ttl = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    
    def __str__(self):
        return self.name

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(128))
    
    def __str__(self):
        return f"{self.name}"

